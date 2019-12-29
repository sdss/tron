__all__ = ['LLock']

from threading import Lock

from tron import Misc


class LLock(object):
    """ Debugging Lock. Can print when the acquire & release calls are made. """
    seq = 1

    def __init__(self, debug=0, name=None):
        self.debug = debug
        self.lock = Lock()
        if name is None:
            name = 'lock-%04d' % (self.seq)
            self.seq += 1
        self.name = name

        if self.debug > 0:
            Misc.log('LLock.create', 'name=%s' % (self.name))

    def acquire(self, block=True, src='up'):
        if self.debug > 0:
            Misc.log('LLock.acquiring', 'name=%s, block=%s, src=%s' %
                     (self.name, block, src))
        self.lock.acquire(block)
        if self.debug > 0:
            Misc.log('LLock.acquired', 'name=%s, block=%s, src=%s' %
                     (self.name, block, src))

    def release(self, src='up'):
        if self.debug > 0:
            Misc.log('LLock.release', 'name=%s, src=%s' %
                     (self.name, src))
        self.lock.release()
