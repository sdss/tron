"""Utilities for dealing with our location (APO vs. LCO)."""

import socket

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
