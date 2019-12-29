""" Various string parsers. """


def floatArgs(s, cnt=None, failWith=None):
    """ Parse a comma-delimited list of floats.

    Args:
        s        - the string to parse
        cnt      - if set, the required number of floats.
        failWith - if set, a string to flesh out error strings.

    Returns:
        a list of values.

    Raises:
        RuntimeError
    """

    try:
        stringList = s.split(',')
        floatList = list(map(float(stringList)))
    except Exception:
        if failWith:
            raise RuntimeError('%s: %s' % (failWith, s))
        else:
            raise

    if cnt is not None and len(floatList) != cnt:
        raise RuntimeError('%s. wrong number of arguments: %s' % (failWith, s))

    return floatList
