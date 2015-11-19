__all__ = ['CommandDecoder']

import Misc

class CommandDecoder(Misc.Object):
    def __init__(self, **argv):
        Misc.Object.__init__(self, **argv)
        
        self.name = argv.get('name', '.unnamed')
        self.nubID = None
        
    def setNub(self, n):
        self.nubID = n
        
    def setName(self, s):
        self.name = s
        
