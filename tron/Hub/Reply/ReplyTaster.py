__all__ = ['ReplyTaster']

from tron import Misc


class ReplyTaster(Misc.Object):
    """ Control which Replys we should accept. So far, we can list match against a number
        of actors and commanders.
    """

    def __init__(self, **argv):
        Misc.Object.__init__(self, **argv)

        self.actors = {}
        self.cmdrs = {}
        self.sources = {}

    def __str__(self):
        return 'ReplyTaster(actors=%s; cmdrs=%s; sources=%s)' % (list(
            self.actors.keys()), list(self.cmdrs.keys()), list(self.sources.keys()))

    def listeningTo(self):
        return list(self.actors.keys()), list(self.cmdrs.keys()), list(self.sources.keys())

    def removeFromFilter(self, actors, cmdrs, sources):
        """ Remove a list of actors and commanders to accept Replys from. """

        for i in actors:
            if i in self.actors:
                del self.actors[i]
        for c in cmdrs:
            if c in self.cmdrs:
                del self.cmdrs[c]
        for s in sources:
            if s in self.sources:
                del self.sources[s]

    def addToFilter(self, actors, cmdrs, sources):
        """ Add a list of actors and commanders to accept Replys from. """

        for i in actors:
            self.actors[i] = True
        for c in cmdrs:
            self.cmdrs[c] = True
        for s in sources:
            self.sources[s] = True

    def setFilter(self, actors, cmdrs, sources):
        """ Set the list of actors and commanders to accept Replys from. """

        self.actors = {}
        self.cmdrs = {}
        self.sources = {}

        self.addToFilter(actors, cmdrs, sources)

    def taste(self, reply):
        """ Do we accept the given Reply? """

        cmd = reply.cmd
        return cmd.cmdrName in self.cmdrs \
            or cmd.cmdrID in self.cmdrs \
            or '*' in self.sources or '*' in self.actors \
            or cmd.actorName in self.actors \
            or reply.src in self.sources
