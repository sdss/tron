#!/usr/bin/env python

__all__ = ['SocketHandler']

import Misc

from . import IOHandler


class SocketHandler(IOHandler):
    """ Class for IO connections that are connected to a socket. """

    def __init__(self, poller, in_f=None, out_f=None):
        IOHandler.__init__(self, poller, in_f, out_f)

        self.debug = 1

    def readInput(self):
        # Misc.log("Cat.readInput", "reading...")
        try:
            readIn = self.in_f.recv(self.tryToRead)
        except socket.error as e:
            Misc.log("Cat.readInput", "exception %r" % (sys.exc_info, ))
            self.poller.removeInput(self)
            if len(self.outBuffer) > 0:
                self.poller.removeOutput(self)
            return
        except BaseException:
            self.poller.removeInput(self)
            if len(self.outBuffer) > 0:
                self.poller.removeOutput(self)
            raise

        if self.debug:
            Misc.log("Cat.readInput", "read len=%d %r" % (len(readIn), readIn[:30]))
        self.inBuffer += readIn

    def mayOutput(self):
        if self.debug:
            Misc.log("Cat.mayOutput",
                     "writing len=%d %r" % (len(self.outBuffer), self.outBuffer[:30]))

        try:
            sent = self.out_f.send(self.outBuffer[:self.tryToWrite])
        except socket.error as e:
            Misc.log("Cat.mayOutput", "exception %r" % (e, ))
            self.poller.removeOutput(self)
            try:
                self.poller.removeInput(self)
            except BaseException:
                pass
            return
        except BaseException:
            raise

        self.outBuffer = self.outBuffer[sent:]
        if len(self.outBuffer) == 0:
            self.poller.removeOutput(self)
