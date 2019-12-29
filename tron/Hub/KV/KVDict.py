__all__ = ['KV', 'KVDict', 'kvAsASCII']

import time
from collections import OrderedDict

from tron import Misc
from tron.Misc.cdict import cdict


""" Rethought a bit.

  All keys are stored as strings (or reprs), but may need to be extracted
  as some given type.

  Keys only exist in the context of their sources. This lets us easily extract
  all of a source's keys and also to flush all such keys when the source
  disconnects.

"""

knownEscapes = {'\r': '\\r', '\n': '\\n'}


def _doEscape(s, escape):
    """ If it exists in the string s, replace the escape string by
    an escaped version of itself. """

    if not escape:
        return s

    i = s.find(escape)
    while i >= 0:
        repl = ''.join([knownEscapes[c] for c in escape])
        s = s[:i] + repl + s[i + len(escape):]
        i = s.find(escape)

    return s


def kvAsASCII(key, val, escape=None):
    """ Return a canonical form of a keyword + value."""

    # val == None -- valueless keyword.
    if val is None:
        return str(key)

    if isinstance(val, KV):
        val = val.val

    if type(val) not in (list, tuple, type(None)):
        return '%s=%s' % (key, _doEscape(val, escape))
        # raise Exception("type(%s) for key(%s) value is not legit: %r" % (type(val), key, val))

    # "grammar" misfeature: empty lists show as "key", not as "key="
    if val is None or len(val) == 0:
        return str(key)

    values = []
    for v in val:
        if v is None:
            values.append('')
        else:
            values.append(_doEscape(v, escape))

    if values:
        return '%s=%s' % (key, ','.join(values))
    else:
        return str(key)


class KV(object):

    def __init__(self, key, val, reply):
        """ Create a single key-value variable. The key must be a string,
        and the value is either a typed value or an uninterpreted string.
        """

        self.key = key
        self.val = val
        self.reply = reply

#    def __str__(self):
#        return "%s=%s" % (self.key, self.val)

    def keyAsStr(self):
        return '%s' % (self.key)

    def valAsStr(self):
        return '%r' % (self.val)

    def valAs(self, converter):
        return converter(self.val)

    def __str__(self):
        if self.reply:
            t = self.reply.ctime
            cmd = self.reply.cmd
        else:
            t = 0.0
            cmd = None

        return 'KV(key=%s, val=%s, ctime=%0.4f, cmd=%s)' % (self.key, self.val, t, cmd)


class KVDict(Misc.Object):
    """ The main Key=Value dictionary.
    """

    def __init__(self, **argv):
        Misc.Object.__init__(self, **argv)
        self.sources = cdict(dictType=OrderedDict)

    def keyNamesForKVs(self, KVs):
        """ Return the key names for a list of raw KVs. """

        return [kv[0] for kv in KVs]

    def setKV(self, src, key, val, reply):
        """ Save the
        """

        if src is None:
            src = reply.src

        if self.debug > 5:
            Misc.log('KVDict.setKV', 'src=%r, key=%r, val=%r' % (src, key, val))

        if src not in self.sources:
            self.sources[src] = cdict(dictType=OrderedDict)

        self.sources[src][key] = KV(key, val, reply)

    def setKVsFromReply(self, reply, src=None):
        if src is None:
            src = reply.src
        self.setKVs(src, reply.KVs, reply)

    def setKVs(self, src, KVs, reply):
        if self.debug > 3:
            Misc.log('KVDict.setKVs', 'src = %r, keys = %r' % (src, KVs))

        for key, val in KVs.items():
            self.setKV(src, key, val, reply)

    def getKV(self, src, key, default=None):
        if src not in self.sources:
            return default
        val = self.sources[src].get(key, default)

        return val.val

    def getKey(self, src, key, default=None):
        if self.debug > 3:
            Misc.log('KVDict.getKey', 'get src=%s key=%s' % (src, key))

        if src not in self.sources:
            return default
        val = self.sources[src].get(key, default)

        if val == default:
            return val
        return val.val

    def addSource(self, source):
        """ Register the fact that a given source exists. """

        Misc.log('KVDict.addSource', 'adding source %s' % (source))
        if source in self.sources:
            Misc.log('KVDict.addSource', 'source %s already exists' % (source))
            return
        self.sources[source] = cdict(dictType=OrderedDict)

    def getSources(self):
        """ Return the known sources. """

        sourceList = sorted(self.sources.keys())

        return sourceList

    def clearSource(self, source):
        """ Remove all keys (well, actually the entire dictionary), for the given source.

        Args:
          source  - the name of a key source.

        Does not care if the source has no dictionary.
        """

        try:
            del self.sources[source]
        except BaseException:
            pass

    def getKeysForSource(self, source):
        """ Return all active keys for a given source.
        """
        pass

    def getValues(self, src, keys):
        """ Return an OrderedDict of values for the given list of keys.

        Args:
           src  - the key source to search.
           keys - a list of keys to fetch.

        Returns:
           - an OrderedDictionary of matched keys.
           - a list of unmatched key names.
        """

        vals = OrderedDict()

        if self.debug > 5:
            Misc.log('KVDict.getValues', 'get src=%s keys=%s' % (src, keys))

        d = self.sources.get(src, None)
        if d is None:
            return vals, keys

        if not keys:
            keys = list(d.keys())

        unmatched = []
        for k in keys:
            if k is None:
                Misc.log('getKVs', 'ignoring None key value in %r' % (keys))
                continue

            try:
                casek, val = d.fetch(k)
                vals[casek] = val
            except KeyError:
                unmatched.append(k)

        return vals, unmatched


if __name__ == '__main__':

    d = KVDict()
    #    d.setKV('hub', 'a', 1)
    d.setKVs('hub', (('b', 2), ('c', '3'), ('d', ('dfg', 123))), None)

    d.setKVs('xxx', (('b', 2), ('c', '3'), ('d', ('dfg', 4353))), None)

    print('\n'.join(map(str, d.listKVs(full=True))))
    print(d.listKVs(pattern='^hub'))
    print(d.listKVs(pattern='nomatch'))

    d.clearKeys(keys=('hub.b', 'hub.xx'))
    print(d.listKVs())

    d.clearKeys()
    print(d.listKVs())

    t0 = time.time()
    N = 100000
    for i in range(N):
        d.setKV('hub', repr(i), i * 3)
    t1 = time.time()
    KVL = d.listKVs(pattern='^1')
    t2 = time.time()

    print('%0.6fs per add' % ((t1 - t0) / N))
    print('%0.6fs per list' % ((t2 - t1) / N))
