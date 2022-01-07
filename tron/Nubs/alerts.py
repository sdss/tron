import os.path

from tron import g, hub
from tron.Hub.Command.Encoders.ASCIICmdEncoder import ASCIICmdEncoder
from tron.Hub.Nub.SocketActorNub import SocketActorNub
from tron.Hub.Reply.Decoders.ASCIIReplyDecoder import ASCIIReplyDecoder
from tron.Misc import cfg


name = 'alerts'


def start(poller):

    my_cfg = cfg.get(g.location, 'actors', doFlush=True)[name]

    stop()

    initCmds = ('ping', 'status')

    safeCmdsList = ['info', 'ping', 'version', 'status']
    safeCmds = r'^\s*({0})\s*$'.format('|'.join(safeCmdsList))

    d = ASCIIReplyDecoder(EOL='\r', stripChars='\n', CIDfirst=False, debug=1)
    e = ASCIICmdEncoder(EOL='\r', sendCommander=True, useCID=False, CIDfirst=False, debug=1)
    nub = SocketActorNub(poller, my_cfg['host'], my_cfg['port'],
                         name=name, encoder=e, decoder=d,
                         grabCID=True,  # the actor spontaneously generates a line we can eat.
                         initCmds=initCmds, safeCmds=safeCmds,
                         needsAuth=True,
                         logDir=os.path.join(g.logDir, name),
                         debug=1)
    hub.addActor(nub)


def stop():
    n = hub.findActor(name)
    if n:
        hub.dropActor(n)
        del n
