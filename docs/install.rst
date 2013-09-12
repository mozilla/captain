============================
Installing Captain and Shove
============================

These instructions are for installing Captain and Shove in a production setup. If you want to
work on Captain or Shove as a developer, see the :doc:`Contributing<contributing>` page.

Prerequisites
=============

* Python 2.6 or 2.7
* A database (or use Django's SQLite support)
* A running instance of RabbitMQ


Setting up Shove
================

Shove installs as a normal Python package. It's not on PyPI yet, but you can install it using
`pip`_:

.. code-block:: sh

   pip install git+https://github.com/mozilla/shove.git#egg=shove

This should install the ``shove`` executable into your environment, which is used to start the
Shove daemon.

Shove requires a settings file; `an example settings file`_ can be found in the Shove source code.
The ``SHOVE_SETTINGS_FILE`` environment variable should contain an absolute file path to the
settings file you want to use.

The settings file contains details for connecting to RabbitMQ, as well as a mapping of project IDs
to directories that projects are contained in. You must edit this dictionary to include file paths
to any projects that you want Shove to be able to run commands for.

.. _pip: http://www.pip-installer.org/
.. _an example settings file: https://github.com/mozilla/shove/blob/master/settings.py-dist


Setting up Captain
==================

Captain is a `Django`_ project. It's intended to be run as a `WSGI`_ application. The WSGI file for
Captain is located at ``captain/wsgi.py`` under the repository root.

You can retrieve the code for Captain by cloning ``https://github.com/mozilla/captain.git`` using
`git`_.

Dependencies
------------

Captain comes with almost all of its dependencies included in the ``vendor`` directory, and
``wsgi.py`` automatically alters the Python import path to include them. There are a few compiled
dependencies that aren't included: They are specified in ``requirements/compiled.txt`` and can be
installed on your target system using `pip`_:

.. code-block:: sh

   pip install -r requirements/compiled.txt

.. note:: Alternatively, you can create system packages for the compiled requirements and have them
   installed via a server automation framework like `Puppet`_.

Settings
--------

Once you've installed the dependencies, you need to create a settings file by copying
``captain/settings/local.py-dist`` to ``captain/settings/local.py`` and editing the contents:

.. code-block:: sh

   cp captain/settings/local.py-dist captain/settings/local.py
   vi captain/settings/local.py

The comments in the file and the `Django settings documentation`_ will help explain how to
configure the settings for your setup.

Database
--------

Next, you must initialize the database using the ``syncdb`` and ``migrate`` commands:

.. code-block:: sh

   python manage.py syncdb
   python manage.py migrate

Static Content
--------------

There are two directories that need to be served up by a static webserver alongside Captain: the
``static`` directory and the ``media`` directory. ``static`` contains all the static CSS,
JavaScript, and images for the site, while ``media`` contains the raw logs sent back from Shove.

The filesystem paths for these directories are configured by the ``MEDIA_ROOT`` and ``STATIC_ROOT``
settings in the settings file, and default to being located at the root of the repositry. The
public-facing URLs for them are controlled by the ``MEDIA_URL`` and ``STATIC_URL`` settings, and
default to ``/static`` and ``/media``.

Once you've configured these settings (if necessary), you must populate the ``static`` directory by
running the following command:

.. code-block:: sh

   python manage.py collectstatic

This should fill ``static`` with files. Then you must use the web server of your choice to serve
these files alongside the rest of the Captain interface.

Finished!
---------

After that, you should be ready to run the site via whatever WSGI-compliant web server you prefer.

.. _Django: https://www.djangoproject.com/
.. _WSGI: http://wsgi.readthedocs.org/
.. _git: http://git-scm.com/
.. _Puppet: https://github.com/puppetlabs/puppet
.. _Django settings documentation: https://docs.djangoproject.com/en/dev/ref/settings/


Log Event Listener
==================

Captain includes a command that listens for log events from Shove. After configuring Captain using
the steps above, you should be able to start the process with this command:

.. code-block:: sh

   python manage.py monitor_shove_logs

.. note:: You should probably use a process control system like `supervisord`_ to manage this
   process as well as the Shove process.

.. _supervisord: http://supervisord.org/
