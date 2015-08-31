import os.path

from Hub.Command.Encoders.ASCIICmdEncoder import ASCIICmdEncoder
from Hub.Reply.Decoders.ASCIIReplyDecoder import ASCIIReplyDecoder
from Hub.Nub.SocketActorNub import SocketActorNub
import g as hub_globals
import hub

name = 'tcc'

def start(poller):

    stop()

    initCmds = ('show version',
                'show users',
                'show time',
                'show status',
                'show inst/full',
                'show object/full',
                'show axisconfig',
                'show focus',
                'axis status',
                'mir status')

    safeCmds = r"(^show )|(status$)"

    d = ASCIIReplyDecoder(EOL='\r', stripChars='\n', CIDfirst=False, debug=1)
    e = ASCIICmdEncoder(EOL='\r', useCID=False, CIDfirst=False, debug=1)
    tcc = SocketActorNub(poller, 'localhost', 25000,
                         grabCID=True, # Send an empty command to just get a CID
                         initCmds=initCmds, safeCmds=safeCmds,
                         needsAuth=False,
                         name=name, encoder=e, decoder=d,
                         logDir=os.path.join(hub_globals.logDir, name),
                         debug=1)
    hub.addActor(tcc)

def stop():
    n = hub.findActor(name)
    if n:
        hub.dropActor(n)
        del n

