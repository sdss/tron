#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2020-01-02
# @Filename: logger.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import datetime
import logging
import logging.handlers
import os

import g


class SDSSRotatingFileHandler(logging.handlers.BaseRotatingHandler):
    """A timed rotating file handler that rotates at a give MJD fraction.

    This class implements the timed rotating file logger handler in the SDSS
    way, i.e., rotating at a given MJD fraction (usually, MJD + 0.3 for APO
    and MJD + 0.5 for LCO). The file name includes the timestamp when it was
    created. A rollover simply closes that file and opens a new one.

    Parameters
    ----------
    filename : str
        The path to the log file.
    suffix : str
        A suffix to be added to the file when create. Can include standard
        ``strftime`` formats. Defaults to ``.%Y-%m-%dT%H:%M:%S``.
    kwargs : dict
        Arguments to be passed to `~logging.handlers.BaseRotatingHandler`.

    """

    def __init__(self, filename, suffix=None, **kwargs):

        self._filename_prefix = filename
        self.suffix = suffix or '%Y-%m-%dT%H:%M:%S'

        mode = kwargs.pop('mode', 'a')
        logging.handlers.BaseRotatingHandler.__init__(self, self._get_filename(), mode,
                                                      **kwargs)

        # MJD fraction at which to rollover.
        if g.location.lower() == 'apo':
            self.rollover_mjd = 0.3
        elif g.location.lower() == 'lco':
            self.rollover_mjd = 0.5
        else:
            self.rollover_mjd = 0.3

        self.rollAt = None
        self._set_next_rollover()

    def _get_filename(self, date=None):

        filename = self._filename_prefix

        if len(filename) > 0 and filename[-1] not in ['.', '/']:
            filename += '.'
        filename += self._get_datestring(date=date)

        return filename

    def _get_datestring(self, date=None):
        """Returns the datetime based on the suffix."""

        date = date or datetime.datetime.utcnow()

        return date.strftime(self.suffix)

    def _set_next_rollover(self):
        """Determines when to roll over next."""

        now = datetime.datetime.utcnow()

        next_rollover = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
        next_rollover += datetime.timedelta(days=self.rollover_mjd)

        # This should account for positive or negative rollover_mjd. We want
        # to be sure we don't end in a situation in which there is never another
        # rollover.
        while now > next_rollover:
            next_rollover += datetime.timedelta(days=1)

        self.rollAt = next_rollover

    def _open(self):
        """Opens the stream and creates a symlink to it."""

        super(SDSSRotatingFileHandler, self)._open()

        current_name = os.path.join(os.path.dirname(self.baseFilename), 'current.log')
        try:
            os.unlink(current_name)
        except BaseException:
            pass
        os.symlink(self.baseFilename, current_name)

    def doRollover(self):
        """Do a rollover."""

        if self.stream:
            self.stream.close()
            self.stream = None

        # New file.
        dfn = self._get_filename(self.rollAt)
        if os.path.exists(dfn):
            os.remove(dfn)
        self.baseFilename = dfn

        if not self.delay:
            self.stream = self._open()

        self._set_next_rollover()

    def shouldRollover(self, record):
        """Determine if rollover should occur.

        If the time is grater than ``rollAt``, rolls over.

        """

        if datetime.datetime.utcnow() > self.rollAt:
            return True

        return False


class Logfile(object):
    """Creates a new logger to log a Nub."""

    def __init__(self, name, log_dir):

        if name in logging.root.manager.loggerDict:
            # If we have already created this logger, just keep using it.
            self._logger = logging.root.manager.loggerDict[name]
        else:
            self._logger = logging.getLogger(name)
            self._logger.setLevel(1)

            log_dir = os.path.expanduser(log_dir)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            self.fh = SDSSRotatingFileHandler(log_dir + '/',
                                              suffix='%Y-%m-%dT%H:%M:%S.log')
            self.fh.formatter = logging.Formatter('%(asctime)sZ %(message)s')
            self.fh.setLevel(1)

            self._logger.addHandler(self.fh)

    def log(self, txt, note='', level=10):
        self._logger.log(level, note + ' ' + txt)
