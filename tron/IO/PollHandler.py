#!/usr/bin/env python

__all__ = ['PollHandler']

""" PollHandler.py -- wrap poll loop.

    The intent is to get non-blocking, event loop I/O.
    IOHandler instances can be registered to be checked for
    input or output. When IO is ready, the IOHandler callback is
    invoked. I.e. PollHandler does not read/write.
"""

import os
import select
import time
from threading import Lock

from tron import Misc


class NullIO(object):
    """ A Trick class to allow forcing the PollHandler to re-configure its outputs.
    """

    def __init__(self, fd, **argv):
        self.fd = fd
        self.debug = argv.get('debug', 0)

    def getInputFd(self):
        return self.fd

    def readInput(self):
        """ Pseudo-callback used to make the poller reconfigure itself. Does not need
        to actually do anything.

        """

        if self.debug > 0:
            Misc.log('NullIO', 'reading token')

        os.read(self.fd, 1)


class PollHandler(Misc.Object):
    """ Wrap the poll() system call.

        IOHandler instances get registered/unregistered for input
        and/or output. When input is available, or non-blocking output
        is possible, an IOHandler callback is triggered.

        Note that PollHandler does no I/O itself.

        Also, poll() acts on file descriptions, not files. Because it returns fds, which
        sort of determines how the callbacks are found, we only deal in fds internally.

        """

    def __init__(self, **argv):
        Misc.Object.__init__(self, **argv)

        self.poller = select.poll()

        self.files = {}
        self.lock = Lock()

        self.timedCallbacks = []
        self.cbLock = Lock()

        self.timeout = argv.get('timeout', 0.5)
        self.timeoutHandler = argv.get('timeoutHandler', None)

        # If there is any possibility that the polling list will be
        # changed during the poll() call proper, we need to wake the poller
        # up to re-read its list.
        #
        self.loopback = None
        self.looper = None
        needLoopback = argv.get('threaded', False)
        if needLoopback:
            self.startLoopback()

    def __del__(self):

        self.poller = None
        Misc.Object.__del__(self)

    def addTimer(self, timer):
        """ Add a timer.

        Args:
            timer   - a dictionary containing:
                         'callback'    - the function to call as callback(timer)
                         'time'        - a time.time() value to try to call by.
        Returns:
           - whether we have arranged for the loop to be restarted.
        """

        self.cbLock.acquire()
        self.timedCallbacks.append((timer['time'], timer))
        self.timedCallbacks.sort()

        # Kick the loop if necessary
        #
        if self.loopback and self.timedCallbacks[0][1] == timer:
            os.write(self.loopback, 'I')
        self.cbLock.release()

    def removeTimer(self, timer):
        """ Remove an existing timer.

        """
        self.cbLock.acquire()
        self.timedCallbacks.remove((timer['time'], timer))
        self.cbLock.release()

    def callMeIn(self, callback, delay):
        """ Arrange to call callback after delay seconds. """

        self.cbLock.acquire()
        self.timedCallbacks.append((time.time() + delay, callback))
        self.timedCallbacks.sort()
        self.cbLock.release()

    def startLoopback(self):
        """ Create a pipe that the poller listens to, that we can write to when the
        poller's file lists change. Also create the object that consumes the input.
        """

        rFd, wFd = os.pipe()

        self.looper = NullIO(rFd, debug=self.debug)
        self.loopback = wFd

        self.addInput(self.looper)

    def addInput(self, obj):
        """ Register an IOHandler instance for input and callback. Return existing handler or None.

        Args:
           obj  - an IOHandler instance, which must provide .getInputFd() and .readInput() methods.

        Returns:
           - the previously registered IOHandler object for the given input file, or None.
        """

        fd = obj.getInputFd()
        if fd is None or fd == -1:
            Misc.log('IOHandler.addInput', 'fd for obj=%s was %s!' % (obj, fd))
            return

        self.lock.acquire()

        pollInfo = self.files.get(fd, None)
        if self.debug > 2:
            Misc.log('Poll.registry',
                     'adding input for fd=%r obj=%s info=%r' % (fd, obj, pollInfo))

        if pollInfo:
            eventMask = pollInfo.get('eventMask', 0)
            lastHandler = pollInfo.get('putHandler', None)
            eventMask |= select.POLLIN
        else:
            lastHandler = None
            eventMask = select.POLLIN | select.POLLPRI
            pollInfo = {}
            self.files[fd] = pollInfo

        pollInfo['eventMask'] = eventMask
        pollInfo['inputHandler'] = obj
        self.poller.register(fd, eventMask)

        self.lock.release()

        # Wake the poller up.
        if self.loopback:
            os.write(self.loopback, 'I')

        if self.debug > 2:
            Misc.log(
                'Poll.registry',
                '%s added input %r(%s): %s' % (id(self), fd, self.flagNames(eventMask), repr(obj)))

        return lastHandler

    def addOutput(self, obj):
        """ Register an IOHandler instance for output and callback.

        Return existing handler or None.

        Args:
           obj  - an IOHandler instance, which must provide .getOutputFd()
                  and .canOutput() methods.

        Returns:
           - the previously registered IOHandler object for the given output file, or None.

        """
        fd = obj.getOutputFd()
        if fd is None or fd == -1:
            Misc.log('Poll.registry', 'Cannot add output for fd=%r' % (fd, ))
            return

        self.lock.acquire()
        pollInfo = self.files.get(fd, None)

        if self.debug > 2:
            Misc.log('Poll.registry',
                     'adding output for fd=%r obj=%s info=%r' % (fd, obj, pollInfo))

        if pollInfo:
            lastHandler = pollInfo.get('outputHandler', None)
            eventMask = pollInfo.get('eventMask', 0)
            eventMask |= select.POLLOUT

            changed = not eventMask & select.POLLOUT
        else:
            pollInfo = {}
            lastHandler = None
            eventMask = select.POLLOUT | select.POLLPRI
            self.files[fd] = pollInfo

            changed = True

        pollInfo['eventMask'] = eventMask
        pollInfo['outputHandler'] = obj
        self.poller.register(fd, eventMask)

        self.lock.release()

        # Wake the poller up.
        if self.loopback and changed:
            os.write(self.loopback, 'O')

        if self.debug > 2:
            Misc.log(
                'Poll.registry', '%s added output %r(%s): obj=%s info=%s' %
                (id(self), fd, self.flagNames(eventMask), obj, pollInfo))

        return lastHandler

    def removeInput(self, obj):
        return self.removeInputFd(obj.getInputFd())

    def removeInputFd(self, fd):
        """ Unregister an input. """

        if fd is None or fd == -1:
            Misc.log('Poll.registry', 'Cannot remove input for fd=%r' % (fd, ))
            return

        self.lock.acquire()

        pollInfo = self.files.get(fd, None)
        if self.debug > 2:
            Misc.log('Poll.registry', 'removing input for fd=%r info=%r' % (fd, pollInfo))

        if fd is None:
            Misc.log('Poll.registry', 'cannot change input for fd=None')
            self.lock.release()
            return

        if pollInfo:
            eventMask = pollInfo['eventMask']
            eventMask &= ~select.POLLIN
        else:
            Misc.log('Poll.registry',
                     'removeInput clearing all IO for unregistered object fd=%r.' % (fd))
            self.lock.release()
            return

        if pollInfo and eventMask != select.POLLPRI:
            pollInfo['eventMask'] = eventMask
            pollInfo['inputHandler'] = None
            self.poller.register(fd, eventMask)
            if self.debug > 2:
                Misc.log('Poll.registry',
                         'removed input %r and set mask to %s' % (fd, self.flagNames(eventMask)))
        else:
            Misc.log('Poll.registry', 'entirely removed (via in) fd=%s' % (fd))

            try:
                self.poller.unregister(fd)
            except Exception as e:
                Misc.log('Poll.registry',
                         'removeInput poller could not unregister fd=%s err=%s' % (fd, e))
            try:
                del self.files[fd]
            except Exception as e:
                Misc.log('Poll.registry', 'removeInput could not delete fd=%s err=%s' % (fd, e))

        self.lock.release()

        # Wake the poller up.
        if self.loopback:
            os.write(self.loopback, 'i')

    def removeOutput(self, obj):
        return self.removeOutputFd(obj.getOutputFd())

    def removeOutputFd(self, fd):
        """ Unregister an output. """

        self.lock.acquire()

        pollInfo = self.files.get(fd, None)
        if self.debug > 2:
            Misc.log('Poll.registry', 'removing output for fd=%r info=%r' % (fd, pollInfo))

        if fd is None:
            Misc.log('Poll.registry', 'cannot change output for fd=None')
            self.lock.release()
            return

        if pollInfo:
            eventMask = pollInfo['eventMask']
            eventMask &= ~select.POLLOUT
        else:
            Misc.log('Poll.registry',
                     'removeOutput clearing all IO for unregistered object fd=%r' % (fd))
            self.lock.release()
            return

        if pollInfo and eventMask != select.POLLPRI:
            pollInfo['eventMask'] = eventMask
            pollInfo['outputHandler'] = None
            self.poller.register(fd, eventMask)

            if self.debug > 2:
                Misc.log(
                    'Poll.registry',
                    'removed output fd=%s and set mask to %s' % (fd, self.flagNames(eventMask)))
        else:
            Misc.log('Poll.registry', 'entirely removing (via out) fd=%s' % (fd))
            try:
                self.poller.unregister(fd)
            except Exception as e:
                Misc.log('Poll.registry',
                         'removeOutput poller could not unregister fd=%s err=%s' % (fd, e))

            try:
                del self.files[fd]
            except Exception as e:
                Misc.log('Poll.registry', 'removeOutput could not delete fd=%s err=%s' % (fd, e))

        self.lock.release()

        # Wake the poller up.
        if self.loopback:
            os.write(self.loopback, 'o')

    def flagNames(self, flags):
        """ Return a string describing a poll event flag mask. """

        names = None
        for fmask, fname in ((select.POLLHUP, 'HUP'), (select.POLLERR, 'ERR'),
                             (select.POLLIN, 'IN'), (select.POLLOUT, 'OUT'),
                             (select.POLLNVAL, 'NVAL'), (select.POLLPRI, 'PRI')):
            if flags & fmask:
                if names is None:
                    names = fname
                else:
                    names += '|%s' % (fname, )

                flags &= ~fmask

        if flags != 0:
            if names is None:
                names = '%0x' % (flags, )
            else:
                names += '|%0x' % (flags, )

        return names

    def fileNames(self):
        """ Returns string describing the files we believe we are waiting on... """

        dlist = []
        for fd, f in self.files.items():
            inHandler = f.get('inputHandler', None)
            outHandler = f.get('outputHandler', None)

            dlist.append('fd=%s io=%s in=%s out=%s' %
                         (fd, self.flagNames(f['eventMask']), inHandler, outHandler))

        return ', '.join(dlist)

    def run(self):
        """ Wait for I/O and dispatch to handlers. """

        Misc.log('PollHandler.run', 'running...')

        while True:
            if self.debug > 7:
                Misc.log('PollHandler.run',
                         'loop, threaded=%s, id=%s' % (bool(self.looper is not None), id(self)))
                if self.debug > 8:
                    Misc.log('PollHandler.run', 'files=%s' % (self.fileNames()))

            # Calculate the proper timeout. Basically, use the loop default
            # or the next item in .timedCallbacks
            timeout = self.timeout
            self.cbLock.acquire()
            if self.timedCallbacks != []:
                nextTick, nextTimer = self.timedCallbacks[0]

                now = time.time()
                if nextTick - now < self.timeout:
                    timeout = nextTick - now
                    if timeout < 0.0:
                        timeout = 0.001
            self.cbLock.release()

            try:
                events = self.poller.poll(timeout * 1000.0)
            except (IOError, OSError) as e:
                Misc.log('PollHandler.run', 'poll trying to clean up: %s' % (e, ))
                try:
                    fd, eString = e
                    self.removeOutputFd(fd)
                    self.removeInputFd(fd)
                except BaseException:
                    Misc.log('PollHandler.run',
                             'poll failed with unknown error exception: %s' % (e, ))
            except Exception as e:
                Misc.log('PollHandler.run', 'poll failed with: %s (%s)' % (e, type(e)))
                if isinstance(e, type((), )) and len(e) == 2:
                    Misc.log('PollHandler.run', 'poll trying to clean up mess: %s' % (e, ))
                    fd, errString = e
                    self.removeOutputFd(fd)
                    self.removeInputFd(fd)
                else:
                    raise

            # The timer expired before any events became available.
            #
            if events == []:
                if self.timeoutHandler:
                    self.timeoutHandler()
                else:
                    if self.debug > 8:
                        Misc.log('PollHandler.run', 'time out on poll, with no timeoutHandler!')

            # Regardless of whether we got here by timeout or by event,
            # check the timed callbacks for expired events.
            #
            if self.timedCallbacks != []:
                now = time.time()
                timers = []
                self.cbLock.acquire()
                for i in range(len(self.timedCallbacks)):
                    try:
                        tick, timer = self.timedCallbacks[i]
                    except IndexError:
                        break

                    if tick > now:
                        break
                    timers.append(timer)
                    del self.timedCallbacks[i]
                self.cbLock.release()

                for timer in timers:
                    timer['callback'](timer)

            # Walk through all new events, and fire on all of them. Round-robinning provides
            # some simple protection against the worst starvation.
            #
            for event in events:
                fd, flag = event

                if self.debug > 4:
                    Misc.log('PollHandler.run', 'got fd=%s events=%s' % (fd, self.flagNames(flag)))

                if flag & ~(select.POLLIN | select.POLLOUT):
                    Misc.log(
                        'PollHandler.run',
                        'poll got exception flags: fd=%r, flag=%s' % (fd, self.flagNames(flag)))

                try:
                    d = self.files[fd]
                except KeyError:
                    Misc.log('PollHandler.run', 'invalid file on poll: %s' % (repr(fd)))

                    continue

                # Generate output first. Unlikely to matter.
                #
                if flag & select.POLLOUT:
                    callbackObj = d['outputHandler']
                    callbackObj.mayOutput()

                if flag & select.POLLIN:
                    callbackObj = d['inputHandler']
                    callbackObj.readInput()

                # Check exception flags separately from RW flags.
                # Why? Because there may have been I/O
                # pending before the error was raised.
                # Think of a client that closes right after writing.
                #
                # This is all a sad misunderstanding.
                # The original intent was to have this .run() loop
                # handle essentially all connection errors and closes.
                # But it turns out that Unixes vary
                # tremendously on how much poll() sees. In some cases,
                # HUP and ERR are never seen for
                # network sockets. Because of that, I am shifting the burden
                # to the callbacks -- read() and write()
                # do dependably generate errors.
                #
                if flag & (select.POLLHUP | select.POLLERR):
                    # On HUP or ERR, let the readInput() or mayOutput()
                    # discover the error and act on it.
                    #
                    Misc.log('PollHandler.run',
                             'HUP/ERR (%s) on poll: %s' % (self.flagNames(flag), repr(fd)))
                    outputHandler = d.get('outputHandler', None)
                    inputHandler = d.get('inputHandler', None)
                    if outputHandler:
                        outputHandler.shutdown()
                    if inputHandler:
                        inputHandler.shutdown()

                if flag & select.POLLNVAL:
                    # I don't know what I'm doing here. -- Misc
                    #
                    Misc.log('PollHandler.run',
                             'NVAL (%s) on poll: %s' % (self.flagNames(flag), repr(fd)))

                    outputHandler = d.get('outputHandler', None)
                    inputHandler = d.get('inputHandler', None)
                    if outputHandler:
                        outputHandler.shutdown()
                    if inputHandler:
                        inputHandler.shutdown()

                    # OK, the IOHandler shutdown has been called, but it is possible that
                    # it was not able to clear our polling data.
                    #
                    self.removeOutputFd(fd)
                    self.removeInputFd(fd)
