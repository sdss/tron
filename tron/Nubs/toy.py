import os.path

import g
import hub
import Misc.cfg
from Hub.Command.Encoders.ASCIICmdEncoder import ASCIICmdEncoder
from Hub.Nub.Listeners import SocketListener
from Hub.Nub.SocketActorNub import SocketActorNub
from Hub.Reply.Decoders.ASCIIReplyDecoder import ASCIIReplyDecoder


name = 'toy'


def start(poller):
    cfg = Misc.cfg.get(g.location, 'actors', doFlush=True)[name]

    stop()

    initCmds = ('ping', 'status')
    safeCmds = r'^\s*(ping|status)\s*$'

    d = ASCIIReplyDecoder(debug=1)
    e = ASCIICmdEncoder(sendCommander=True, useCID=False, debug=1)
    nub = SocketActorNub(poller,
                         cfg['host'],
                         cfg['port'],
                         name=name,
                         encoder=e,
                         decoder=d,
                         grabCID=True,
                         initCmds=initCmds,
                         safeCmds=safeCmds,
                         needsAuth=True,
                         logDir=os.path.join(g.logDir, name),
                         debug=1)
    hub.addActor(nub)


def stop():
    n = hub.findActor(name)
    if n:
        hub.dropActor(n)
        del n
