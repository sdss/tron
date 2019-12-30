"""Utilities for dealing with our location (APO vs. LCO)."""

import os
import socket
import warnings


def determine_location(location=None):
    """Return a location based on the domain name."""

    location = location or os.environ.get('OBSERVATORY', None)

    if location is None:
        fqdn = socket.getfqdn().split('.')
    else:
        location = location.upper()
        assert location in ['APO', 'LCO', 'LOCAL'], 'invalid location'
        return location

    if 'apo' in fqdn:
        return 'APO'
    elif 'lco' in fqdn:
        return 'LCO'
    elif 'ACTORCORE_LOCAL' in os.environ and os.environ['ACTORCORE_LOCAL'] == '1':
        return 'LOCAL'
    else:
        warnings.warn('Using local setup for tron.', UserWarning)
        return 'LOCAL'
