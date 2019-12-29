import os.path

import g
import hub
from Hub.Command.Encoders.ASCIICmdEncoder import ASCIICmdEncoder
from Hub.Nub.Listeners import SocketListener
from Hub.Nub.SocketActorNub import SocketActorNub
from Hub.Reply.Decoders.ASCIIReplyDecoder import ASCIIReplyDecoder


name = 'mcp'


def start(poller):
    stop()

    initCmds = ('info', )

    safeCmdsList = ['info', 'ping', 'version', 'status']
    safeCmds = r'^\s*({0})\s*$'.format('|'.join(safeCmdsList))

    d = ASCIIReplyDecoder(debug=1)
    e = ASCIICmdEncoder(debug=1)
    nub = SocketActorNub(
        poller,
        'sdssmcp',
        31012,
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