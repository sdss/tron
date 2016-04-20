import os.path

from Hub.Command.Encoders.ASCIICmdEncoder import ASCIICmdEncoder
from Hub.Reply.Decoders.ASCIIReplyDecoder import ASCIIReplyDecoder
from Hub.Nub.SocketActorNub import SocketActorNub
from Hub.Nub.Listeners import SocketListener
import Misc.cfg
import hub
import g

name = 'telemetry'

def start(poller):
    cfg = Misc.cfg.get('hub', 'actors', doFlush=True)[name]

    stop()

    initCmds = ('ping',
                'status')

    # safeCmds = r'^\s*info\s*$'

    d = ASCIIReplyDecoder(debug=3)
    e = ASCIICmdEncoder(sendCommander=True, useCID=False, debug=3)
    nub = SocketActorNub(poller, cfg['host'], cfg['port'],
                         name=name, encoder=e, decoder=d,
                         grabCID=True, # the actor spontaneously generates a line we can eat.
                         initCmds=initCmds, # safeCmds=safeCmds,
                         needsAuth=False,
                         logDir=os.path.join(g.logDir, name),
                         debug=3)
    g.perms.addPrograms([name])
    hub.addActor(nub)
    g.perms.addActorsToProgram(name, [actor]) for actor in Misc.cfg.get('hub', 'actors').keys()

def stop():
    n = hub.findActor(name)
    if n:
        hub.dropActor(n)
        del n
