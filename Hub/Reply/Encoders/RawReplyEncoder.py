__all__ = ['RawReplyEncoder']

import Misc
from Hub.KV.KVDict import kvAsASCII
from Parsing.dequote import dequote

from .ASCIIReplyEncoder import ASCIIReplyEncoder
from .ReplyEncoder import ReplyEncoder


class RawReplyEncoder(ReplyEncoder):
    """ Encode Replys without any protocol information.

    Options:
       EOL     - choose the EOL string to use.
       keyName - set a single keyword, whose _value_ alone will be returned.
    """

    def __init__(self, **argv):
        ReplyEncoder.__init__(self, **argv)

        # How do we terminate encoded lines?
        #
        self.EOL = argv.get('EOL', '\n')
        self.keyName = argv.get('keyName', None)

    def encode(self, r, nub, noKeys=False):
        """ Encode a protocol-free reply for a given nub.  """

        if self.keyName:
            rawVal = r.KVs.get(self.keyName, '')
            val = dequote(rawVal)
            Misc.log('RAWDEQUOTE', "rawVal=%r val=%r" % (rawVal, val))
        else:
            val = self.encodeKeys(r.src, r.KVs)

        if val:
            return "%s%s" % (val, self.EOL)
        else:
            return ''

    def encodeKeys(self, src, KVs):
        """ Return a string encoding of KVs stored in an OrderedDict.

        Args:
           src   - ignored
           KVs   - an OrderedDict of values. See Parsing/parsing.py for important details.
        Notes:

        """

        if self.debug > 5:
            Misc.log("ASCIIReplyEnc.encode", "encoding %r" % (KVs, ))
        if KVs is None:
            return ""

        keylist = []
        for k, v in KVs.items():
            if self.debug > 5:
                Misc.log("ASCIIReplyEnc.encode", "encoding %r=%r" % (k, v))

            keylist.append(kvAsASCII(k, v))

        return "; ".join(keylist)
