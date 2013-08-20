===================
Hooray for Captain!
===================

Captain is the web frontend for the Captain Shove system.


Project details
===============

:Code:          https://github.com/mozilla/captain
:Documentation: Ha!
:Issue tracker: https://github.com/mozilla/captain/issues
:IRC:           ``#capshove`` on irc.mozilla.org
:License:       Mozilla Public License v2


To hack on Captain
==================

Required:

* pip
* virtualenv
* python: 2.6 or 2.7

Steps:

1. ``git clone https://github.com/mozilla/captain``
2. ``cd captain``
3. ``virtualenv venv``
4. ``source venv/bin/activate``
6. ``pip install -r requirements/dev.txt``
7. ``cp captain/settings/local.py-dist captain/settings/local.py``
8. Edit ``captain/settings/local.py``. The comments tell you what
   you need to change.
9. ``./manage.py sync``
10. ``./manage.py migrate``


To test
=======

1. If your virtual environment isn't activated, then do
   ``source venv/bin/activate``
2. ``python manage.py test``
