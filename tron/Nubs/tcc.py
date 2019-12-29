import os.path

import tron.Misc
from tron import g as hub_globals
from tron import hub
from tron.Hub.Command.Encoders.ASCIICmdEncoder import ASCIICmdEncoder
from tron.Hub.Nub.SocketActorNub import SocketActorNub
from tron.Hub.Reply.Decoders.ASCIIReplyDecoder import ASCIIReplyDecoder


name = 'tcc'


def start(poller):

    cfg = tron.Misc.cfg.get(hub_globals.location, 'actors', doFlush=True)[name]

    stop()

    isLCO = False
    try:
        isLCO = hub_globals.location == 'LCO'
    except BaseException:
        pass
    if isLCO:
        initCmds = (
            'device status',
            'show version',
        )
    else:
        initCmds = ('show version', 'show users', 'show time', 'show status', 'show inst/full',
                    'show object/full', 'show axisconfig', 'show focus', 'axis status',
                    'mir status')

    safeCmds = r'(^device )|(status$)'

    d = ASCIIReplyDecoder(EOL='\r', stripChars='\n', CIDfirst=False, debug=1)
    e = ASCIICmdEncoder(EOL='\r', useCID=False, CIDfirst=False, debug=1)
    tcc = SocketActorNub(
        poller,
        cfg['host'],
        cfg['port'],
        grabCID=True,  # Send an empty command to just get a CID
        initCmds=initCmds,
        safeCmds=safeCmds,
        needsAuth=True,
        name=name,
        encoder=e,
        decoder=d,
        logDir=os.path.join(hub_globals.logDir, name),
        debug=1)
    hub.addActor(tcc)


def stop():
    n = hub.findActor(name)
    if n:
        hub.dropActor(n)
        del n
