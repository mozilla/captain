#!/usr/bin/env python
import os
import site
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
def path(*a):
    return os.path.join(ROOT, *a)


# Add vendor/lib/python as a sitedir so that libraries included there are in the PATH.
site.addsitedir(path('vendor/lib/python'))


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "captain.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
