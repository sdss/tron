import os.path

import tron.Misc
from tron import g, hub
from tron.Hub.Command.Encoders.ASCIICmdEncoder import ASCIICmdEncoder
from tron.Hub.Nub.SocketActorNub import SocketActorNub
from tron.Hub.Reply.Decoders.ASCIIReplyDecoder import ASCIIReplyDecoder

name = 'mcp'


def start(poller):
    stop()

    cfg = tron.Misc.cfg.get(g.location, 'actors', doFlush=True)[name]

    initCmds = ('info', )

    safeCmdsList = ['info', 'ping', 'version', 'status']
    safeCmds = r'^\s*({0})\s*$'.format('|'.join(safeCmdsList))

    d = ASCIIReplyDecoder(debug=1)
    e = ASCIICmdEncoder(debug=1)
    nub = SocketActorNub(
        poller,
        cfg['host'],
        cfg['port'],
        name=name,
        encoder=e,
        decoder=d,
        grabCID=True,  # the MCP spontaneously generates a line we can eat.
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
