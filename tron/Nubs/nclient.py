import os
import time

from tron import g, hub
from tron.Hub.Command.Decoders.ASCIICmdDecoder import ASCIICmdDecoder
from tron.Hub.Nub.Commanders import StdinNub
from tron.Hub.Nub.Listeners import SocketListener
from tron.Hub.Reply.Encoders.ASCIIReplyEncoder import ASCIIReplyEncoder


name = 'nclient'
listenPort = 6095


def acceptStdin(in_f, out_f, addr=None):
    """ Create a command source with the given fds as input and output. """

    all = ('*', )

    nubID = g.nubIDs.gimme()
    fullname = '%s_%d' % (name, nubID)

    d = ASCIICmdDecoder(needCID=True, needMID=True, EOL='\n', hackEOL=True, name=name, debug=2)
    e = ASCIIReplyEncoder(CIDfirst=True, name=name, debug=2)
    c = StdinNub(g.poller,
                 in_f,
                 out_f,
                 name=fullname,
                 logDir=os.path.join(g.logDir, fullname),
                 encoder=e,
                 decoder=d,
                 debug=2)

    c.taster.addToFilter(all, (), all)
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
