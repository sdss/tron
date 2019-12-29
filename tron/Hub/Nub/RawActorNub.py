__all__ = ['RawActorNub']

import g
import Misc

from .ActorNub import ActorNub
from .SocketActorNub import SocketActorNub


class RawActorNub(SocketActorNub, ActorNub):

    def getCmdForReply(self, r):
        """ Assign the current (and _only_) command ID to the reply, and set flag appropriately """

        try:
            activeMid = self.activeMid
        except BaseException:
            self.activeMid = activeMid = 1

        cmdDone = False
        try:
            replyText = r['RawText']
            if replyText == " OK":
                Misc.log('rawReply', 'converting reply flag')
                r['flag'] = ':'
                cmdDone = True
                self.activeMid += 1
            else:
                Misc.log('rawReply', 'not converting reply flag :%s:' % (replyText))
        except Exception as e:
            Misc.log('rawReply', 'ignoring exceptoin: %s' % (e))

        r['cid'] = 0
        r['mid'] = activeMid
        cmd = ActorNub.getCmdForReply(self, r)

        if cmdDone:
            self.checkQueue()

        return cmd
