import os

import tron.Misc
from tron import g, hub
from tron.Hub.Command.Encoders.ASCIICmdEncoder import ASCIICmdEncoder
from tron.Hub.Nub.SocketActorNub import SocketActorNub
from tron.Hub.Reply.Decoders.ASCIIReplyDecoder import ASCIIReplyDecoder


name = 'apogeebpr'


def start(poller):
    cfg = tron.Misc.cfg.get(g.location, 'actors', doFlush=True)[name]
    stop()

    initCmds = ('ping', 'status')

    safeCmdsList = ['ping', 'status']
    safeCmds = r'^\s*({0})\s*$'.format('|'.join(safeCmdsList))

    d = ASCIIReplyDecoder(debug=3)
    e = ASCIICmdEncoder(sendCommander=True, useCID=False, debug=3)

    nub = SocketActorNub(
        poller,
        cfg['host'],
        cfg['port'],
        name=name,
        encoder=e,
        decoder=d,
        grabCID=True,  # the actor spontaneously generates a line we can eat.
        initCmds=initCmds,
        safeCmds=safeCmds,
        needsAuth=True,
        logDir=os.path.join(g.logDir, name),
        debug=3)
    hub.addActor(nub)


def stop():
    n = hub.findActor(name)
    if n:
        hub.dropActor(n)
        del n
