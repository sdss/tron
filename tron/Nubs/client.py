import time

import tron.Hub.Command.Decoders as hubDecoders
import tron.Hub.Nub.Commanders as hubCommanders
import tron.Hub.Reply.Encoders as hubEncoders
from tron import g, hub
from tron.Hub.Nub.Listeners import SocketListener


name = 'client'
listenPort = 6093


def acceptStdin(in_f, out_f, addr=None):
    """ Create a command source with the given fds as input and output. """

    nubID = g.nubIDs.gimme()

    d = hubDecoders.ASCIICmdDecoder(needCID=True,
                                    needMID=True,
                                    EOL='\n',
                                    hackEOL=True,
                                    name=name,
                                    debug=1)
    e = hubEncoders.ASCIIReplyEncoder(EOL='\n', simple=True, debug=1, CIDfirst=True)
    c = hubCommanders.StdinNub(g.poller,
                               in_f,
                               out_f,
                               name='%s.v%d' % (name, nubID),
                               encoder=e,
                               decoder=d,
                               debug=1)

    c.taster.addToFilter(('*'), (), ('hub'))
    hub.addCommander(c)

    time.sleep(1)


def start(poller):
    stop()

    ll = SocketListener(poller, listenPort, name, acceptStdin)
    hub.addAcceptor(ll)

    time.sleep(1)


def stop():
    ll = hub.findAcceptor(name)
    if ll:
        hub.dropAcceptor(ll)
        del ll
