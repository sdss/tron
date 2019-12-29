__all__ = ['BinaryCmdEncoder']

import struct

from tron import Misc

from .CommandEncoder import CommandEncoder


class BinaryCmdEncoder(CommandEncoder):

    def __init__(self, **argv):
        CommandEncoder.__init__(self, **argv)

    def encode(self, cmd):
        """ Encapsulate an old-style binary command.  """

        str = cmd.cmd
        length = len(str)
        csum = 0
        for i in range(length):
            csum ^= ord(str[i])

        # See extractCompleteCommand for better notes.
        #
        packet = struct.pack('>BBihh%dsBB' % (length), 1, 1, length, cmd.actorMid, cmd.actorCid,
                             str, csum, 4)

        if self.debug > 3:
            Misc.log('BinaryCmdEncoder', 'cmd=%s data=%r' % (cmd, packet))

        return packet
