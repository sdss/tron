import os.path

from tron import g
from tron import hub
from tron import Misc.cfg
from tron.Hub.Command.Encoders.ASCIICmdEncoder import ASCIICmdEncoder
from tron.Hub.Nub.Listeners import SocketListener
from tron.Hub.Nub.SocketActorNub import SocketActorNub
from tron.Hub.Reply.Decoders.ASCIIReplyDecoder import ASCIIReplyDecoder


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
