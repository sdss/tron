"""Configuration for all sites."""

import os

# Where to save the logs
logDir = '/data/logs/tron'

# TODO: this will no longer work, since we're not checking in the password file any more.
# TODO: consider keyring python module?
# TODO: see this ticket: https://trac.sdss.org/ticket/2405

# What file has the passwords.
passwordFile = os.path.join(os.environ['TRON_DIR'], 'passwords')

# Which words to load internally.
vocabulary = ('perms', 'hub', 'keys', 'msg')
