__all__ = ['InternalCmd']

import re

from tron import Misc


class InternalCmd(object):

    def __init__(self, name, isActor=True, **argv):
        """ The common parts of internal actors.

        Args:
           name         - our public name

        Optional Args:
           isActor      - whether we should be listed as an Actor

        """

        self.name = name
        self.ID = name
        self.isActor = isActor
        self.needsAuth = argv.get('needsAuth', False)
        # if self.needsAuth == True:
        #     self.needsAuth = self.name

        self.locked = False

        self.debug = argv.get('debug', 0)
        self.commands = {}

        safeCmds = argv.get('safeCmds', None)
        if safeCmds:
            self.safeCmds = re.compile(safeCmds)
        else:
            self.safeCmds = None

        # Some stats
        self.totalCommands = 0

    def sendCommand(self, cmd):
        """
        """

        Misc.log('%s.cmd' % (self.name), 'running cmd=%s' % (Misc.qstr(cmd.cmd)))
        self.totalCommands += 1

        cmd.parseArgs()
        words = list(cmd.argDict.keys())
        if len(words) == 0:
            cmd.finish('')
            return

        cmdWord = words[0]
        cmdHandler = self.commands.get(cmdWord, None)
        if cmdHandler is None:
            cmd.fail('%sTxt=%s' %
                     (self.name, Misc.qstr('No command named %s' % (cmdWord))))
            return

        cmd.reportQueued()
        try:
            cmdHandler(cmd)
        except Exception as e:
            Misc.tback('Vocab.sendCommand', e)
            cmd.fail('%sTxt=%s' % (self.name, Misc.qstr(e, tquote='"')))
            return

    def statusCmd(self, cmd, doFinish=True):
        """ """

        cmd.inform('vocabStats=%s,%d' % (Misc.qstr(self.name), self.totalCommands))

        if doFinish:
            cmd.finish()

    def listCommandsCmd(self, cmd, doFinish=True):
        """ """

        if doFinish:
            cmd.finish()

    def shutdown(self, notifyHub=None):
        pass
