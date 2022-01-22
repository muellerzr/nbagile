__version__ = "0.0.1"

import sys; 
if not sys.version_info < (3,9):
    raise NotImplementedError("Python 3.9+ are currently not supported")
