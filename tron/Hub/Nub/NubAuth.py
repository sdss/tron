__all__ = ['NubAuth']


import os
import hashlib as sha
import configparser

from tron import Misc, Parsing, g, hub


class NubAuth(object):
    """
    Intercepts and act on login and logout commands.
    """

    CONNECTED = 'connected'
    NOT_CONNECTED = 'not connected'
    CONNECTING = 'connecting'

    def __init__(self, **argv):
        object.__init__(self)

        self.state = self.NOT_CONNECTED
        self.nonce = None
        self.passwords = {}

    def rejectClient(self, cmd, clientType, clientVersion, clientPlatform):
        return False

    def parseVersion(self, s):
        """ Parse a comma-delimited pair of strings. Not really, though.

        I'm assuming there is no comma in the two parts of the version
        string. Oh, the shame of it. Someone should fire my sorry ass.

        """

        Misc.log('NubAut', 'parsing version %s' % (s))

        parts = s.split(',')
        dqparts = list(map(Parsing.dequote, parts))

        Misc.log('NubAut', 'parsed %s' % (dqparts))
        return dqparts

    def checkLogin(self, cmd):
        """ Try to match a name and password to an entry in the password file.

        The passwords are encrypt-only, so we need to match against the encrypted form
        of one of the password file entries. The scheme I originally chose is to allow
        left-prefix matches for the _parts_ of the program names, with '*' as a default match.
        For example, if the program given is 'PU04', we would try to find an entry in the password
        file for 'PU04', 'PU', and '*'. Basically, remove trailing digits, then try '*'.

        But that leaves holes -- enter no program, or 'XX', and you will drop through to the
        default. So always match.

        Returns True, or a string describing the problem.

        """

        if self.state != self.CONNECTING or self.nonce is None:
            return 'unexpected login ignored.'

        matched, unmatched, leftovers = cmd.match([('program', Parsing.dequote),
                                                   ('password', Parsing.dequote),
                                                   ('username', Parsing.dequote),
                                                   ('type', Parsing.dequote),
                                                   ('version', Parsing.dequote),
                                                   ('platform', Parsing.dequote)])

        if 'program' not in matched or 'password' not in matched:
            return 'not all arguments to login were found.'

        # OK. Look for the full program name:
        program = matched['program'].upper()

        config = configparser.ConfigParser()
        config.readfp(open(os.path.expanduser('~/.tronpass.cfg')))
        ourPW = config.get('hub', program, fallback=None)

        if ourPW is None:
            return 'unknown program'

        enc = sha.sha1((self.nonce + ourPW).encode())
        if enc.hexdigest() != matched['password']:
            return 'incorrect password'

        # Register our IDs.
        #
        username = matched.get('username', None)
        if not username:
            username = program

        hub.dropCommander(self, doShutdown=False)
        self.setNames(program, username)
        hub.addCommander(self)

        # Try to squirrel away some useful facts about the client.
        self.clientType = matched.get('type', 'unknown')
        self.clientPlatform = matched.get('platform', 'unknown')
        self.clientVersion = matched.get('version', 'unknown')
        Misc.log('NubAuth', 'checkLogin version %s, platform %s' %
                 (self.clientVersion, self.clientPlatform))

        # Check whether we don't like the version
        #
        reject = self.rejectClient(cmd, self.clientType, self.clientVersion, self.clientPlatform)
        if reject:
            return reject

        return True

    def setUserInfo(self):
        """ Save a keyword describing our client.

        Kinda gross for it to be here. But there is no obvious good place for it,
        except maybe to name a TUINub.
        """

        Misc.log('reportAuth', 'reporting on %s' % (self))

        try:
            otherIP = self.otherIP
            otherFQDN = self.otherFQDN
        except BaseException:
            otherIP = otherFQDN = 'unknown'

        # And tell others all about us. Well, have the 'hub' tell them.
        self.userInfo = 'user=%s,%s,%s,%s,%s,%s' % \
                        (Misc.qstr(self.name), Misc.qstr(self.clientType),
                         Misc.qstr(self.clientVersion),
                         Misc.qstr(self.clientPlatform),
                         Misc.qstr(otherIP), Misc.qstr(otherFQDN))

    def makeMyNonce(self):
        """ Generate an ASCIIfied large random number. Put it in .nonce """

        import base64

        f = open('/dev/urandom', 'rb')
        bits = f.read(64)
        s = base64.encodebytes(bits)

        # base64 encoding inserts and appends NLs. Strip these.
        #
        self.nonce = s.decode().replace('\n', '')

        f.close()

    def interceptReply(self, reply):
        """ Trap and handle the login/logout commands here.

        Args:
            cmd   - the command to inspect.
        Return:
            bool  - True if we have consumed the command.
        """

        if self.state == self.CONNECTED:
            return False

        if reply.cmd.cmdrName == self.name:
            return False
        return True

    def interceptCmd(self, cmd):
        """ Trap and handle the login/logout commands here.

        Args:
            cmd   - the command to inspect.
        Return:
            bool  - True if we have consumed the command.
        """

        # Fast track the usual case.
        #
        if cmd.actorName != 'auth':
            if self.state == self.CONNECTED:
                return False
            else:
                cmd.fail('why=%s' % (Misc.qstr('please log in.')), src='auth')
                return True

        cmdWords = cmd.cmd.split()
        if len(cmdWords) < 1:
            return self.state != self.CONNECTED

        cmdWord = cmdWords[0]

        if self.state == self.CONNECTED:
            if cmdWord == 'logout':
                self.state = self.NOT_CONNECTED
                cmd.finish('bye', src='auth')
            else:
                return False
                # cmd.fail('unknownCommand=%s' % (Misc.qstr(cmdWord)),
                #         src='auth')
            return self.state != self.CONNECTED
        elif self.state == self.NOT_CONNECTED:
            if cmdWord == 'knockKnock':
                self.state = self.CONNECTING
                self.makeMyNonce()
                cmd.finish('nonce=%s' % (Misc.qstr(self.nonce)), src='auth')
            else:
                cmd.fail('why=%s' % (Misc.qstr('please log in.')), src='auth')

            return True
        else:
            if cmdWord == 'login':
                ret = self.checkLogin(cmd)
                if ret:
                    self.state = self.CONNECTED
                    cmd.finish(('loggedIn', 'cmdrID=%s' % Misc.qstr(self.name)), src='auth')
                    Misc.log('auth', 'logged in %s' % (self))
                    self.setUserInfo()
                    g.hubcmd.inform(self.userInfo)
                else:
                    self.state = self.NOT_CONNECTED
                    cmd.fail('why=%s' % Misc.qstr(ret), src='auth')
            else:
                self.state = self.NOT_CONNECTED
                cmd.fail('why=%s' % (Misc.qstr('please play by the rules.')), src='auth')
            return True
