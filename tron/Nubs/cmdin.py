from tron import g, hub
from tron.Hub.Command.Decoders.ASCIICmdDecoder import ASCIICmdDecoder
from tron.Hub.Nub.Listeners import SocketListener
from tron.Hub.Nubs.StdinNub import StdinNub
from tron.Hub.Reply.Encoders.ASCIIReplyEncoder import ASCIIReplyEncoder


name = 'cmdin'
listenPort = 6098


def acceptStdin(in_f, out_f, addr=None):
    """ Create a command source with the given fds as input and output. """

    nubID = g.nubIDs.gimme()

    d = ASCIICmdDecoder(needCID=False, needMID=False, EOL='\r\n', name=name, debug=1)
    e = ASCIIReplyEncoder(name=name, simple=True, debug=1)
    c = StdinNub(g.poller,
                 in_f,
                 out_f,
                 name='%s-%d' % (name, nubID),
                 encoder=e,
                 decoder=d,
                 debug=1)
    c.taster.addToFilter(('*'), (), ('*'))
    hub.addCommander(c)


def start(poller):
    stop()

    ll = SocketListener(poller, listenPort, name, acceptStdin)
    hub.addAcceptor(ll)


def stop():
    ll = hub.findAcceptor(name)
    if ll:
        hub.dropAcceptor(ll)
        del ll
