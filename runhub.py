"""
Start the hub server, including all Nubs for connections.
"""

import sys

import CPL
import g
import hub

def startAllConnections(names):
    """ Create all default connections, as defined by the proper configuration file. """

    for n in names:
        try:
            hub.startNub(n)
        except Exception, e:
            msg = "FAILED to start nub %s: %s\n" % (n, e)
            sys.stderr.write(msg)
            try:
                g.hubcmd.warn('text=%s' % (CPL.qstr(msg)))
            except:
                sys.stderr.write("hubcmd.warn failed\n")
    
# NOTE: jkp: I don't like it, but I'll work with the "everything's global" setup
# for now to store the location.
# TODO: hub should be a class we init() anyway!
g.location = CPL.location.determine_location('test')

hub.init()
startAllConnections(CPL.cfg.get(g.location, 'nubs', doFlush=True))

hub.run()
