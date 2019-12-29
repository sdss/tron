__all__ = ['tback']

import inspect
import pprint
import sys
import traceback

from tron import Misc


def tback(system, e, info=None):
    """ Log a decently informative traceback. """

    try:
        frames = inspect.trace()
        toptrace = inspect.trace()[-1]
    except BaseException:
        one_liner = '%s: %s: %s' % (e, sys.exc_info()[0], sys.exc_info()[1])
        Misc.error(system, '======== exception botch: %s' % (one_liner))
        return

    tr_list = []
    tr_list.append('\n\n====== trace:\n')
    tr_list.append(pprint.pformat(toptrace))

    i = 0
    frames.reverse()
    for f in frames:
        # tr_list.append("\n\n====== frame %d arg+local names:\n" % (i))
        # tr_list.append(pprint.pformat(f[0].f_code.co_varnames))
        tr_list.append('\n\n====== frame %d locals:\n' % (i))
        tr_list.append(pprint.pformat(f[0].f_locals))
        i += 1

    ex_list = traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    Misc.error(system, '\n======== exception: %s\n' % (''.join(ex_list)))
    Misc.error(system, '\n======== exception details: %s\n' % (''.join(tr_list)))
