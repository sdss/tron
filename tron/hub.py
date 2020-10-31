#!/usr/bin/env python

"""
   The core of the hub.
   The hub basically:
      - maintains a keyword-value ("KV") dictionary,
      - accepts commands from Commanders and passes them onto Actors,
      - accepts and generates KV responses, and passes them on to interested parties.

   We handle the fact that we can get (or generate) responses to commands that that we
   did not send by creating Commands for all responses.

   c = Command()
      cmdrCid, cmdrMid
      tgt, cmd
      [xid]

      actorCid, actorMid

   r = Reply(cmd=cmd

"""

import importlib
import json
import os
import re
import signal
import sys
import time
from collections import OrderedDict

import tron.Auth
import tron.Hub.Command.Command
import tron.Hub.KV.KVDict
import tron.IO
from tron import Misc, __version__, g
from tron.Misc.cdict import cdict


def init(programsFile=None):
    g.home = sys.path[0]
    if g.home is None or g.home == '':
        g.home = os.getcwd()

    g.rootDir = os.getcwd()

    if 'TRON_PACKAGE_DIR' in os.environ:
        tron_package_dir = os.environ['TRON_PACKAGE_DIR']
    else:
        tron_package_dir = os.path.dirname(__file__)

    # Bootstrap the whole configuration system
    configPath = os.environ.get('CONFIG_DIR', os.path.join(tron_package_dir, 'config'))

    Misc.cfg.init(path=configPath)
    os.environ['CONFIG_DIR'] = configPath

    g.logDir = Misc.cfg.get('hub', 'logDir')
    Misc.setLogdir(g.logDir)
    Misc.setID('hub')
    Misc.log('hub.init', 'logger started...')

    #   - a globally unique ID generator for Commands.
    g.xids = Misc.ID()
    g.nubIDs = Misc.ID()
    g.hubMIDs = Misc.ID()

    # The Hub is basically:
    #   All of these are in the global namespace "g".
    #
    #   - A dictionary of KVs
    g.KVs = tron.Hub.KV.KVDict.KVDict(debug=5)

    g.commanders = cdict()
    g.actors = cdict()

    g.hubcmd = None
    g.hubcmd = tron.Hub.Command.Command(
        '.hub',
        '0',
        0,
        'hub',
        None,
        actorCid=0,
        actorMid=0,
        neverEnd=True)

    #   - An authorization manager
    permsCmd = tron.Hub.Command.Command(
        '.perms',
        '0',
        0,
        'perms',
        None,
        actorCid=0,
        actorMid=0,
        neverEnd=True)
    g.perms = tron.Auth.Auth(permsCmd, debug=1)

    # Loads the programs with their custom permissions
    Misc.log('hub.init', 'loading programs ...')
    loadPrograms()

    #   - A dictionary of Commander Nubs, indexed by unique ID.
    g.commanders = CmdrDict('Commanders')
    # g.listeners = g.commanders

    #   - A dictionary of Actor Nubs, indexed by name
    g.actors = NubDict('Actors')
    g.vocabulary = cdict()

    #   - dictionary of PollAcceptors, waiting for for new connections.
    g.acceptors = cdict()

    #   - dictionary of active commands, indexed by XID.
    g.pendingCommands = {}

    #   - A PollHandler
    g.poller = tron.IO.PollHandler(debug=1)

    Misc.log('hub.init', 'loading internal vocabulary...')
    loadWords(None)

    Misc.log('hub.init', 'loading keys...')
    loadKeys()

    # atexit.register(shutdown)
    signal.signal(signal.SIGHUP, handleSIGHUP)
    signal.signal(signal.SIGTERM, handleSIGTERM)


def handleSIGHUP(signal, frame):
    restart()


def handleSIGTERM(signal, frame):
    shutdown()


def getSetHubVersion():
    """ Put the uncached svn version info into the hub.version keyword. """

    version = Misc.qstr(__version__)
    g.KVs.setKV('hub', 'version', version, None)


def loadKeys():
    rootDir = Misc.cfg.get(g.location, 'httpRoot')
    host = Misc.cfg.get(g.location, 'httpHost')

    g.KVs.setKV('hub', 'httpRoot', [host, rootDir], None)

    getSetHubVersion()


def loadWords(words=None):
    if words is None:
        words = Misc.cfg.get('hub', 'vocabulary')

    for w in words:
        _loadWords([w])


def _loadWords(wordlist):
    """ (Re-)load a list of Vocabulary words, overwriting any existing info.
    """

    # First, (re-)load the entire Vocabulary module. Let that fail to the top
    # level.
    #
    Misc.log('hub.loadVocab', 'trying to (re-)load Vocab module')

    for w in wordlist:
        # Now try to load the module itself.
        modName = 'tron.Vocab.' + w
        if w == 'hub':
            modName = 'tron.Vocab.hubCommands'
        try:
            Misc.log('hub.loadVocab', 'trying to (re-)load vocabulary word %s' % (w,))
            mod = importlib.import_module(modName)
        except ImportError as e:
            raise Exception('Import of %s failed: %s' % (modName, e))

        Misc.log('hub.loadWords', 'loading vocabulary word %s from %s...' % (w, modName))

        cmdSet = getattr(mod, 'hubCommands' if w == 'hub' else w)()
        try:
            dropActor(cmdSet)
        except BaseException:
            pass
        g.vocabulary[w] = cmdSet

        addActor(cmdSet)

        Misc.log('hub.loadWords', 'vocabulary: %s' % (g.vocabulary))


def shutdown():
    Misc.log('hub.shutdown', 'shutting down......................................')
    try:
        _shutdown()
    except BaseException:
        pass
    sys.exit(0)


def restart():
    Misc.log('hub.restart', 'restarting......................................')
    try:
        _shutdown()
    except BaseException:
        pass

    Misc.log('hub.restart', 'for real......................................')
    time.sleep(1)
    os.execlp('tron', 'tron', 'restart')


def _shutdown():
    sys.stderr.write('final cleanup; deleting hub pieces...\n')

    sys.stderr.write('       deleting acceptors...\n')
    for aname, acceptor in list(g.acceptors.items()):
        try:
            acceptor.shutdown(notifyHub=False)
        except BaseException:
            pass

    sys.stderr.write('       deleting commanders...\n')
    for cname, cmdr in list(g.commanders.items()):
        try:
            cmdr.shutdown(notifyHub=False)
        except BaseException:
            pass

    sys.stderr.write('       deleting actors...\n')
    for aname, actor in list(g.actors.items()):
        try:
            actor.shutdown(notifyHub=False)
        except BaseException:
            pass


def run():
    """ Listens for and handles I/O on all devices.
    """
    while True:
        try:
            Misc.log('hub.run', 'actors id=%r' % (id(g.actors)))
            g.poller.run()
        except (SystemExit, KeyboardInterrupt):
            Misc.log('Hub.run', 'Normal exit."')
            raise

        except Exception as e:
            Misc.tback('Hub.run', e)


class NubDict(OrderedDict):
    """ Arrange for access to a dictionary to be annotated. """

    def __init__(self, name):
        OrderedDict.__init__(self)
        self.name = name
        self.listSelf()

    def __setitem__(self, k, v):
        OrderedDict.__setitem__(self, k, v)

        self.listSelf()

    def __delitem__(self, k):
        # k.shutdown(notifyHub=False)
        OrderedDict.__delitem__(self, k)

        self.listSelf()

    def listSelf(self, cmd=None):
        names = []
        for n in self.values():
            names.append(Misc.qstr(n.name))

        if not cmd:
            cmd = g.hubcmd

        cmd.inform('%s=%s' % (self.name, ','.join(names)))


class CmdrDict(NubDict):
    """ Like NubDict, but generate a 'users' keyword, depending on
    the state of the nub's isUser attribute.
    """

    def listSelf(self, cmd=None):
        if not cmd:
            cmd = g.hubcmd
        names = []
        userNames = []
        for n in self.values():
            names.append(Misc.qstr(n.name))
            if n.isUser:
                userNames.append(Misc.qstr(n.name))
            Misc.log('listCommanders', 'n=%s has info=%s' % (n, n.userInfo))
            if n.userInfo:
                cmd.inform(n.userInfo)

        cmd.inform('%s=%s' % (self.name, ','.join(names)))
        cmd.inform('users=%s' % (','.join(userNames)))


def addNubToDict(nub, nubDict):
    """Add a new nub to the given dict.
    The nub's ID must not be the same as for any existing nub. """

    existingNub = findNubInDict(nub.ID, nubDict)
    if existingNub is not None:
        Misc.log('Hub.nubs', 'nub %s already exists; not overwriting' % (nub.ID))
        return

    nubDict[nub.ID] = nub
    Misc.log('Hub.nubs', 'added nub %s to %s' % (nub, nubDict))


def dropNubFromDict(nub, nubDict, doShutdown=True):
    """ Close an existing nub. The nub must, of course, be in the given nub dict. """

    Misc.log('Hub.nubs', 'dropping nub=%s shutdown=%s' % (nub, doShutdown))
    if doShutdown:
        nub.shutdown(notifyHub=False)

    nub = findNubInDict(nub.ID, nubDict)
    if nub is None:
        Misc.log('Hub.nubs', 'nub %s is not registered; not dropping it' % (nub.ID))
        return

    del nubDict[nub.ID]


def findNubInDict(id, nubDict):
    """ Return the named nub, or None if it does not exist. """

    return nubDict.get(id, None)


def addActor(nub):
    addNubToDict(nub, g.actors)
    g.KVs.addSource(nub.name)
    if nub.needsAuth:
        g.perms.addActors([nub.name])


def dropActor(nub):
    # g.perms.dropActors([nub.name])
    g.KVs.clearSource(nub.name)
    dropNubFromDict(nub, g.actors)


def findActor(id):
    return findNubInDict(id, g.actors)


def addCommander(nub):
    Misc.log('hub.addCommander', 'adding %s' % (nub.name))
    addNubToDict(nub, g.commanders)


def dropCommander(nub, doShutdown=True):
    Misc.log('hub.dropCommander', 'dropping %s' % (nub.name))
    dropNubFromDict(nub, g.commanders, doShutdown=doShutdown)


def findCommander(id):
    return findNubInDict(id, g.commanders)


def addAcceptor(nub):
    addNubToDict(nub, g.acceptors)


def dropAcceptor(nub):
    dropNubFromDict(nub, g.acceptors)


def findAcceptor(id):
    return findNubInDict(id, g.acceptors)


def findNub(nub):
    """ Find whether a nub exists in any of the nub dictionaries. """

    for d in (g.actors, g.commanders, g.acceptors):
        if nub in d:
            return d[nub]
    return None


def dropNub(nub):
    """ Drop a Nub, regardless of its type. """

    if nub.ID in g.actors:
        dropActor(nub)
    elif nub.ID in g.commanders:
        dropCommander(nub)
    elif nub.ID in g.acceptors:
        dropAcceptor(nub)
    else:
        Misc.log('hub.dropNub',
                 'nub %s (%s) is neither in g.actors (%s) or g.commanders (%s)' %
                 (nub.ID, nub, g.actors, g.commanders))


def listActors(match):
    """ """

    actors = sorted(g.actors.keys())

    return actors


def validateCommanderNames(nub, programName, username):
    """ Transform a proposed CommanderNub name into a unique CommanderNub name.

    A Commander name must consist of a program name and a username separated by a period.
    Basically, take the proposed name and add _%d until there is no collision.
    """

    # Severely normalize the username
    #
    programName = re.sub('[^a-zA-Z0-9_]+', '_', programName)
    username = re.sub('[^a-zA-Z0-9_]+', '_', username)

    if re.match('[a-zA-Z_]', username) is None:
        username = '_' + username
    if re.match('[a-zA-Z_]', programName) is None:
        programName = '_' + programName

    fullName = '%s.%s' % (programName, username)

    n = 2
    proposedName = fullName
    ok = False
    while not ok:
        ok = True
        for c in g.commanders.values():
            if c.name == proposedName:
                ok = False
                break
        if not ok:
            proposedName = '%s_%d' % (fullName, n)
            n += 1

    return proposedName


def getActor(cmd):
    """ Find either an actor or vocabulary word matching the given command.
    """

    actorName = cmd.actorName

    # Misc.log("hub.getActor", "looking for actor %s" % (actorName))
    tgt = g.actors.get(actorName, None)

    if tgt is None:
        # Misc.log("hub.getActor", "looking for vocabulary word %s" % (actorName))
        tgt = g.vocabulary.get(actorName, None)

    Misc.log('hub.getActor', 'actornName %s target = %s' % (actorName, tgt))
    return tgt


def addCommand(cmd):
    """ Add a new command, and arrange for it to be executed by the appropriate target.

    Need to add:
        Automatically start an Actor if it is not running. Do this by:
          - check for starteable Nub - just call startNub in a catch.
          - send (i.e. queue) the command. We need to add the logic for the Actor's
        queue to be flushed when the connection has been established.

          - Provide some throttling to avoid idiocy when, say, the tcc password is changed.
    """

    Misc.log('hub.addCommand', 'new cmd=%s' % (cmd))

    if cmd.actorName == 'dbg':
        runCmd(cmd)
        return

    actor = getActor(cmd)

    if actor is None:
        cmd.fail('NoTarget=%s' %
                 Misc.qstr('the target named %s is not connected' % (cmd.actorName)),
                 src='hub')
        return

    # Checks whether the commander requires authentication
    if cmd.cmdr().needsAuth:
        # Enforce permissions if the actor requires them.
        ok = g.perms.checkAccess(cmd.cmdrCid, actor, cmd)
        if not ok:
            cmd.fail('NoPermission=%s' %
                     Misc.qstr('you do not have permission to command %s %s' %
                               (actor.name, cmd.cmd)),
                     src='hub')
            return

    actor.sendCommand(cmd)


def runCmd(c):
    cmd = c.cmd.strip()
    Misc.log('hub.runCmd', 'cmd = %r' % (cmd))
    if cmd == '':
        c.finish('Eval=%s' % (Misc.qstr('')),
                 src='hub')
        return

    try:
        ret = eval(cmd)
    except Exception as e:
        c.fail('EvalError=%s' % Misc.qstr(e),
               src='hub')
        raise

    c.finish('Eval=%s' % (Misc.qstr(ret)), src='hub')
    Misc.log('hub.runCmd', 'ret = %r' % (ret))


def forceReload(name):
    """ Do whatever we can to force a given module/package to be reloaded.

    """
    try:
        Misc.log('hub.forceReload', 'trying to (re-)load %s' % (name))
        mod = importlib.import_module(f'tron.Nubs.{name}')
    except BaseException:
        raise

    return mod


def stopNub(name):
    n = findActor(name)
    if n:
        dropActor(n)


def startNub(name):
    """Launch a single Nub.

    (Re-)Loads a module named 'name' from the Nubs folder and calls the start function.
    """

    Misc.log('hub.startNub', 'trying to start %s' % (name))

    mod = importlib.import_module(f'tron.Nubs.{name}')

    # And call the start() function.
    #
    Misc.log('hub.startNub', 'starting Nub %s...' % (name))
    mod.start(g.poller)


def loadPrograms(programsFile=None):
    """Loads the programs with their specific permissiosns."""

    if programsFile is None:
        programsFile = os.path.join(os.path.dirname(__file__), 'programs.json')

    if not os.path.exists(programsFile):
        Misc.log('hub.loadPrograms', 'programs file not found. Skipping.')
        return

    try:
        programs = json.load(open(programsFile))
    except BaseException:
        Misc.log('hub.loadPrograms', 'problem parsing JSON file.')
        return

    for program in programs:
        actors = programs[program]['actors']
        g.perms.addPrograms(programs=[program], actors=actors)
