__all__ = ['msg']

import time

import Vocab.InternalCmd as InternalCmd

from tron import Misc


""" A simple instant messaging system.

    The single command is:
        msg a bunch of text

    which responds with:
        : msgTime="2003-03-15T01:02:03" msgSender="Craig" msg="a bunch of text"

"""


class msg(InternalCmd.InternalCmd):

    def __init__(self, **argv):
        InternalCmd.InternalCmd.__init__(self, 'msg', **argv)

    def sendCommand(self, cmd):
        """ Simply arrange for the argument string to be visible by all interested commanders.
        """

        ts = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(cmd.ctime))
        cmd.finish('msg=%s, %s' % (Misc.qstr(ts), Misc.qstr(cmd.cmd)))
