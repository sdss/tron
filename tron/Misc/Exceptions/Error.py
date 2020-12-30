__all__ = ['Error']


class Error(Exception):

    def __init__(self, oneliner, **argv):
        """ Create a generic error with arbitray attributes.

        Args:
           error   - one line of text, intended for users.
           argv    - a dictionary of attributes.
        """

        Exception.__init__(self)

        self.oneliner = oneliner

        self.argv = argv
        self.args = oneliner

    def __getattr__(self, name):
        try:
            return self.argv[name]
        except BaseException:
            raise AttributeError('%s instance has no attribute %s' %
                                 (self.__class__.__name__, name))
