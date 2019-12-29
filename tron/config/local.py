"""Configuration for local."""

# flake8: noqa

# Where to save the logs
logDir = '/tmp/logs/tron'

# Which words to load internally.
vocabulary = ('perms', 'hub', 'keys', 'msg')


from .apo import *

for actor in actors:
    actor['host'] = 'localhost'
