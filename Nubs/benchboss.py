import os.path

from Hub.Command.Encoders.ASCIICmdEncoder import ASCIICmdEncoder
from Hub.Reply.Decoders.ASCIIReplyDecoder import ASCIIReplyDecoder
from Hub.Nub.SocketActorNub import SocketActorNub
import Misc.cfg
import hub
import g

name = 'benchboss'

def start(poller):
    cfg = Misc.cfg.get(g.location, 'actors', doFlush=True)[name]

    stop()

    initCmds = ('ping',
                'status')

    safeCmdsList = ['info', 'ping', 'version', 'status']
    safeCmds = r'^\s*({0})\s*$'.format('|'.join(safeCmdsList))

    d = ASCIIReplyDecoder(debug=1)
    e = ASCIICmdEncoder(sendCommander=True, useCID=False, debug=1)
    nub = SocketActorNub(poller, cfg['host'], cfg['port'],
                         name=name, encoder=e, decoder=d,
                         grabCID=True, # BOSS spontaneously generates a line we can eat.
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
