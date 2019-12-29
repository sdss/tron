#!/usr/bin/env python

import os

from tron import Misc


location = Misc.location.determine_location()


def getActors(actorName=None, hostName=None):
    # Bootstrap the whole configuration system
    configPath = os.environ.get('CONFIG_DIR', os.path.join(os.environ['TRON_DIR'], 'config'))
    Misc.cfg.init(path=configPath, verbose=False)

    actors = Misc.cfg.get(location, 'actors')
    if actorName:
        actors = dict([(key, val) for key, val in list(actors.items()) if key == actorName])
    if hostName:
        actors = dict([(key, val) for key, val in list(actors.items())
                       if (hostName in (val['host'], val['host'].split('.', 1)[0]))])
    return actors


def printActors(actors, verbose=False):
    if verbose:
        actorList = [
            '%s,%s,%s' % (actors[name]['actorName'], actors[name]['host'], actors[name]['port'])
            for name in list(actors.keys())
        ]
    else:
        actorList = [actors[name]['actorName'] for name in list(actors.keys())]

    if actorList:
        print('\n'.join(actorList))


def main():
    printActors(getActors())


if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-H',
                      '--host',
                      dest='hostName',
                      default=None,
                      help='match actors on given host',
                      metavar='HOST')
    parser.add_option('-n',
                      '--name',
                      dest='actorName',
                      default=None,
                      help='match given actor',
                      metavar='ACTOR')
    parser.add_option('-v',
                      '--verbose',
                      action='store_true',
                      dest='verbose',
                      default=False,
                      help='print all actor fields')

    (options, args) = parser.parse_args()

    actors = getActors(actorName=options.actorName, hostName=options.hostName)
    printActors(actors, verbose=options.verbose)
