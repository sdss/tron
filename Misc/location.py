"""Utilities for dealing with our location (APO vs. LCO)."""

import socket
import warnings


def _warning(message, category=UserWarning, filename='', lineno=-1):
    print('{0}: {1}'.format(category.__name__, message))

warnings.showwarning = _warning


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
        warnings.warn('Using test setup for tron.', UserWarning)
        return 'TEST'
