import os

import g
import hub
import Misc.cfg
from Hub.Command.Encoders.ASCIICmdEncoder import ASCIICmdEncoder
from Hub.Nub.SocketActorNub import SocketActorNub
from Hub.Reply.Decoders.ASCIIReplyDecoder import ASCIIReplyDecoder


name = 'apogee'


def start(poller):
    cfg = Misc.cfg.get(g.location, 'actors', doFlush=True)[name]
    stop()

    initCmds = ('ping', 'status')

    safeCmdsList = ['info', 'ping', 'version', 'status']
    safeCmds = r'^\s*({0})\s*$'.format('|'.join(safeCmdsList))

    d = ASCIIReplyDecoder(debug=3)
    e = ASCIICmdEncoder(sendCommander=True, useCID=False, debug=3)
    # nub = SocketActorNub(poller, 'hub25m-p.apo.nmsu.edu', 18281,
    # nub = SocketActorNub(poller, 'apogee-ql.apo.nmsu.edu', 18281,
    # nub = SocketActorNub(poller, 'matt-1.astro.virginia.edu', 33221,
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
