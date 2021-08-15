__all__ = ['setID', 'setLogdir', 'enableLoggingFor', 'disableLoggingFor',
           'isoTS', 'log', 'error']

import os
from math import modf
from time import gmtime, strftime, time


systems = {}

DISABLED = '0'
ENABLED = '.'
ERROR = 'E'
FATAL = 'F'
UNDEFINED = '?'

logfileDir = os.environ["TRON_LOG_DIR"]
logfileName = None
logID = 'log'
logfile = None
rolloverOffset = -0.3 * (24 * 3600)  # Fermi MJD offset.
rolloverChunk = 24 * 3600
rolloverTime = 0


def setID(newID):
    global logID

    logID = newID


def setLogdir(dirname):
    global logfileDir

    logfileDir = dirname


def enableLoggingFor(system):
    systems[system] = ENABLED


def disableLoggingFor(system):
    systems[system] = DISABLED


def setLoggingFor(system, level):
    if level:
        systems[system] = ENABLED
    else:
        systems[system] = DISABLED


def isoTS(t=None, format='%Y-%m-%d %H:%M:%S', zone='Z'):
    """ Return a proper ISO timestamp for t, or now if t==None. """

    if t is None:
        t = time()

    if zone is None:
        zone = ''

    return strftime(format, gmtime(t)) \
        + '.%03d%s' % (1000 * modf(t)[0], zone)


def rollover(t):
    global logfile
    global logfileName
    global rolloverTime

    if t > rolloverTime:
        logfile = None

    if logfile is None:
        # Set next rollover time.
        rolloverTime = t - t % rolloverChunk + rolloverChunk + rolloverOffset

        # this can happen at startup
        if rolloverTime < t:
            rolloverTime += rolloverChunk
        logfileName = '%s.log' % (strftime('%Y-%m-%dT%H:%M:%S', gmtime(t)))
        os.makedirs(os.path.join(logfileDir, logID), exist_ok=True)
        logfile = open(os.path.join(logfileDir, logID, logfileName), 'w', 1)
        currentName = os.path.join(logfileDir, logID, 'current.log')
        try:
            os.unlink(currentName)
            os.symlink(logfileName, currentName)
        except BaseException:
            pass
        log('log', 'next rollover is at %d (%s)' % (rolloverTime, isoTS(rolloverTime)))


def log(system, detail, state=None):
    now = time()
    nowStamp = isoTS(now)
    rollover(now)

    # if not hasattr(globals(), 'logfile'):
    #    logfile = sys.stderr

    # If the logging state has not explicitely been enabled or disabled,
    # print the notice, but mark the system name with a '?'
    #
    if state is None:
        state = systems.get(system, UNDEFINED)

    if state == UNDEFINED:
        state = systems.get('default', state)

    if state != DISABLED:
        logfile.write('%s %s %s %s %s\n' % (nowStamp, logID, state, system, detail))
        logfile.flush()


def error(*args):
    log(*args, **{'state': ERROR})
