"""Utilities for dealing with our location (APO vs. LCO)."""

import os
import socket
import warnings


def determine_location(location=None):
    """Return a location based on the domain name."""

    if location is None:
        fqdn = socket.getfqdn()
    else:
        return location

    if 'ACTORCORE_LOCAL' in os.environ and os.environ['ACTORCORE_LOCAL'] == '1':
        return 'LOCAL'
    elif 'apo' in fqdn:
        return 'APO'
    elif 'lco' in fqdn:
        return 'LCO'
    else:
        warnings.warn('Using local setup for tron.', UserWarning)
        return 'LOCAL'
