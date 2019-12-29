__all__ = ['ReplyDecoder']

from tron import Misc


class ReplyDecoder(Misc.Object):
    """ Base class for decoders for incoming replies.

    """

    def __init__(self, **argv):
        Misc.Object.__init__(self, **argv)

        self.name = argv.get('name', 'unnamed')
        self.nubID = None

    def setNub(self, n):
        self.nubID = n

    def setName(self, s):
        self.name = s

    def decode(self, s0, s1):
        raise RuntimeError('.decode() must be defined in a ReplyDecoder subclass.')
