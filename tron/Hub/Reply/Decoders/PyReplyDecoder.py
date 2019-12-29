__all__ = ['PyReplyDecoder']

import pickle

from tron import Misc

from .ReplyDecoder import ReplyDecoder


class PyReplyDecoder(ReplyDecoder):
    """ Encode Replys as single-line pickled python objects.
    """

    def __init__(self, **argv):
        ReplyDecoder.__init__(self, **argv)

        # How do we terminate encoded lines?
        #
        self.EOL = argv.get('EOL', '\f')

    def decode(self, buf, newData):
        """ Find and extract a single complete command in the inputBuffer.
        """

        if newData:
            buf += newData

        if self.debug > 3:
            Misc.log('PyReply.decoder', 'called with EOL=%r and buf=%r' % (self.EOL, buf))

        eol = buf.find(self.EOL)
        if self.debug > 2:
            Misc.log('PyReply.decoder', 'eol at %d in buffer %r' % (eol, buf))

        # No complete reply found. make sure to return
        # the unmolested buffer.
        #
        if eol == -1:
            return None, buf

        replyString = buf[:eol]
        buf = buf[eol + len(self.EOL):]

        # Make sure to consume unparseable junk up to the next EOL.
        #
        try:
            r = pickle.loads(replyString)
        except SyntaxError:
            Misc.log('PyReply.decoder', 'Failed to unpickle %r' % (replyString))
            return None, buf

        if self.debug > 5:
            Misc.log('PyReply.decoder', 'extracted %r, returning %r' % (r, buf))

        return r, buf
