import os

from tron import g, hub
from tron.Hub.Command.Encoders.ASCIICmdEncoder import ASCIICmdEncoder
from tron.Hub.Nub.Listeners import SocketListener
from tron.Hub.Nub.SocketActorNub import SocketActorNub
from tron.Hub.Reply.Decoders.ASCIIReplyDecoder import ASCIIReplyDecoder


name = 'apogeetest'


def start(poller):
    stop()

    initCmds = ('ping', 'status')

    # safeCmds = r'^\s*info\s*$'

    d = ASCIIReplyDecoder(debug=3)
    e = ASCIICmdEncoder(sendCommander=True, useCID=False, debug=3)
    # nub = SocketActorNub(poller, 'hub25m-p.apo.nmsu.edu', 18281,
    nub = SocketActorNub(
        poller,
        'apogee-ql.apo.nmsu.edu',
        18281,
        # nub = SocketActorNub(poller, 'matt-1.astro.virginia.edu', 33221,
        name=name,
        encoder=e,
        decoder=d,
        grabCID=True,  # the actor spontaneously generates a line we can eat.
        initCmds=initCmds,  # safeCmds=safeCmds,
        needsAuth=False,
        logDir=os.path.join(g.logDir, name),
        debug=3)
    hub.addActor(nub)


def stop():
    n = hub.findActor(name)
    if n:
        hub.dropActor(n)
        del n
