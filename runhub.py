"""
Start the hub server, including all Nubs for connections.
"""

import sys
import socket

import CPL
import g
import hub

def determine_location(location=None):
    """Return a location based on the domain name."""
    if location is None:
        fqdn = socket.getfqdn()
    else:
        return location

    if 'apo' in fqdn:
        return 'APO'
    elif 'lco' in fqdn:
        return 'LCO'
    else:
        return None

def startAllConnections(names):
    """ Create all default connections, as defined by the proper configuration file. """

    for n in names:
        try:
            hub.startNub(n)
        except Exception, e:
            sys.stderr.write("FAILED to start nub %s: %s\n" % (n, e))
            try:
                g.hubcmd.warn('text=%s' % (CPL.qstr('FAILED to start nub %s: %s\n', n, e)))
            except:
                sys.stderr.write("hubcmd.warn failed\n")
    
hub.init()
location = determine_location()
startAllConnections(CPL.cfg.get(location, 'nubs', doFlush=True))

hub.run()
