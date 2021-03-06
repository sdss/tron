__all__ = ['Logfile']

import os
import os.path
from math import modf
from time import gmtime, strftime, time


class Logfile(object):
    """ A simple class offering timestamped logs to timestamped files. We maintain a logging threshold,
    against whch logging requests are compared.
    """

    def __init__(self, dir, level=1, EOL='\n', doEncode=False):
        """
        Args:
           dir       - a directory name inside which we create our logfiles. Must already exist.
           level     - a threshold. Logging requests with a level at or below this are logged.
           EOL       - a string to terminate log lines with. Set to '' to not add newlines.
           doEncode  - If True, use %r rather than %s to encode the log text.
        """

        self.dir = dir
        self.level = level
        self.EOL = EOL
        self.doEncode = doEncode

        if not os.path.isdir(self.dir):
            os.mkdir(self.dir)

        self.newLogfile()

    def setLevel(self, level):
        lastLevel = self.level
        self.level = level
        return lastLevel

    def getLevel(self):
        return self.level

    def newLogfile(self):
        """ Close the current logfile and open a new one.

        We use the current time to name the file.
        """

        name = strftime('%Y-%m-%dT%H:%M:%S.log', gmtime())
        newFile = open(os.path.join(self.dir, name), 'a+', 1)  # The 1 specifies line-buffering

        self.logfile = newFile

    def getTS(self, t=None, format='%Y-%m-%d %H:%M:%S', zone='Z'):
        """ Return a proper ISO timestamp for t, or now if t==None. """

        if t is None:
            t = time()

        if zone is None:
            zone = ''

        return strftime(format, gmtime(t)) \
            + '.%04d%s' % (10000 * modf(t)[0], zone)

    def log(self, txt, note='', level=1):
        """ Append txt to our log if the given level is <= self.level.

        Args:
            txt - the bulk of the text to log.
        """

        if level > self.level:
            return

        ts = self.getTS()

        if self.doEncode:
            self.logfile.write('%s %s %r\n' % (ts, note, txt))
        else:
            self.logfile.write('%s %s %s%s' % (ts, note, txt, self.EOL))
