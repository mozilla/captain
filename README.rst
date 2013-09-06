===================
Hooray for Captain!
===================

Captain is the web frontend for the `Captain Shove`_ system. It sends commands to the shove_
daemon, which executes the commands on a remote server.

.. image:: https://api.travis-ci.org/mozilla/captain.png
   :target: https://travis-ci.org/mozilla/captain

.. image:: https://coveralls.io/repos/mozilla/captain/badge.png?branch=master
   :target: https://coveralls.io/r/mozilla/captain?branch=master


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

Captain works together with shove_ through RabbitMQ_. In order to interact with shove, you'll need
to install a local RabbitMQ server; the `RabbitMQ Installation Documentation`_ will tell you how.
Once you have the server running, you can configure captain to connect to RabbitMQ in
``captain/settings/local.py``.


To test
=======

1. If your virtual environment isn't activated, then do
   ``source venv/bin/activate``
2. ``python manage.py test``


.. _Captain Shove: https://wiki.mozilla.org/Websites/Captain_Shove
.. _shove: https://github.com/mozilla/shove
.. _RabbitMQ: http://www.rabbitmq.com/
