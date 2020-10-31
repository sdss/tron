import socket
import time

from tron import g, hub
from tron.Hub.Command.Decoders.ASCIICmdDecoder import ASCIICmdDecoder
from tron.Hub.Nub.Commanders import AuthStdinNub
from tron.Hub.Nub.Listeners import SocketListener
from tron.Hub.Reply.Encoders.ASCIIReplyEncoder import ASCIIReplyEncoder


name = 'TUI'
listenPort = 9877


def acceptTUI(in_f, out_f, addr=None):
    """ Create a command source with the given fds as input and output. """

    # Fetch a unique ID
    #
    nubID = g.nubIDs.gimme()
    fullname = '%s_%d' % (name, nubID)

    # all = ('tcc','mcp',
    #       'hub','msg')
    all = ('*', )

    otherIP, otherPort = in_f.getpeername()
    try:
        otherFQDN = socket.getfqdn(otherIP)
    except BaseException:
        otherFQDN = 'unknown'

    # os.system("/usr/bin/sudo /usr/local/bin/www-access add %s" % (otherIP))

    d = ASCIICmdDecoder(needCID=False, EOL='\r\n', debug=1)
    e = ASCIIReplyEncoder(EOL='\r', simple=True, debug=1, CIDfirst=True)
    c = AuthStdinNub(g.poller,
                     in_f,
                     out_f,
                     name=fullname,
                     encoder=e,
                     decoder=d,
                     debug=1,
                     type='TUI',
                     needsAuth=True,
                     isUser=True,
                     otherIP=otherIP,
                     otherFQDN=otherFQDN)
    c.taster.addToFilter(all, (), all)
    hub.addCommander(c)


def start(poller):
    stop()

    lt = SocketListener(poller, listenPort, name, acceptTUI)
    hub.addAcceptor(lt)


def stop():
    a = hub.findAcceptor(name)
    if a:
        hub.dropAcceptor(a)
        del a
        time.sleep(0.5)  # OK, why did I put this in here?
