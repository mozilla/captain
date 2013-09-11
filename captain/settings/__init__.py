import sys

from .base import *


# Load special settings for CI.
if os.environ.get('TRAVIS'):
    from .travis import *
else:
    # If we're not on CI, attempt to load local settings.
    try:
        from .local import *
    except ImportError, exc:
        exc.args = tuple(['{0} (did you rename settings/local.py-dist?)'.format(exc.args[0])])
        raise exc


TEST = len(sys.argv) > 1 and sys.argv[1] == 'test'
if TEST:
    try:
        from .test import *
    except ImportError:
        pass
