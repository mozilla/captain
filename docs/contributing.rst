============
Contributing
============

Developer Setup
===============

Prerequisites:

* Python 2.6 or 2.7
* `pip <http://www.pip-installer.org/>`_
* `virtualenv <http://www.virtualenv.org/>`_
* `RabbitMQ <http://www.rabbitmq.com/download.html>`_

.. note:: While it is technically possible to work on Captain or Shove without RabbitMQ installed
   for very small changes, it is highly recommended to install it anyway.

Once you have the prerequisites installed, you must set up the Shove daemon:

.. code-block:: sh

   # Clone the repository
   git clone https://github.com/mozilla/shove.git
   cd shove

   # Create a virtualenv and activate it
   # You should consider using virtualenvwrapper instead: http://virtualenvwrapper.readthedocs.org/
   virtualenv venv
   source venv/bin/activate

   # Install shove in development mode
   python setup.py develop

   # Copy the settings file
   cp settings.py-dist settings.py
   # You must edit settings.py with the settings for your setup! It is commented with info on what
   # you need to change.

   # Start the shove daemon.
   shove

Once Shove is running, you must set up the Captain frontend:

.. code-block:: sh

   # Clone the repository
   git clone https://github.com/mozilla/captain.git
   cd shove

   # Create a virtualenv and activate it
   # You should consider using virtualenvwrapper instead: http://virtualenvwrapper.readthedocs.org/
   virtualenv venv
   source venv/bin/activate

   # Install libraries needed for development
   pip install -r requirements/dev.txt

   # Copy the settings file
   cp captain/settings/local.py-dist captain/settings/local.py
   # You must edit local.py with the settings for your setup! It is commented with info on what
   # you need to change.

   # Initialize the database
   python manage.py sync
   python manage.py migrate

   # Start the development server
   python manage.py runserver

You should now have both Captain and Shove running and connected to RabbitMQ.

The last step is to start the Captain logging event process. The process listens for messages on
the logging queue and saves them to the database to update Captain with the results of a command.
To run it, run the following in a new terminal:

.. code-block:: sh

   # Enter the captain directory.
   cd captain

   # Activate the virtualenv.
   source venv/bin/activate

   # Run the logging daemon.
   python manage.py monitor_shove_logs


Running the Tests
=================

.. code-block:: sh

   # Enter the captain directory.
   cd captain

   # Activate the virtualenv.
   source venv/bin/activate

   # Run the tests.
   python manage.py test


Changing the Database
=====================

Captain uses South_ to generate and run migrations for the database. The South documentation has
more information on how to generate and run migrations when the models change.

Make sure to check for new migrations whenever you pull new code!

.. _South: http://south.readthedocs.org/


Third-party Libraries
=====================

Third-party libraries for Captain are listed in pip requirements files in the ``requirements``
directory. There are three files:

* ``prod.txt``: Non-compiled libraries required for production.
* ``compiled.txt``: Compiled libraries required for production.
* ``dev.txt``: Libraries that are required for development (e.g. for running the tests). This also
  pulls in the requirements from ``prod.txt`` and ``compiled.txt``.

In addition, the libraries from ``prod.txt`` are also included in a directory called ``vendor``.
This is used to import the libraries in a production environment where there isn't a PyPI mirror
to install the libraries from.

If you add a new third-party library to Captain, make sure to add it to the appropriate
requirements file. If you add to or update ``prod.txt``, you'll also need to update vendor. This
can be done with using pip like so:

.. code-block:: sh

   # Executed from the repository root.
   pip install -I --install-option="--home=`pwd`/vendor" library-name==1.2

.. note:: Make sure that any requirements in ``prod.txt`` are pinned to a specific version or
   commit.


Where to Find Us
================

We hang out on IRC on irc.mozilla.org in ``#capshove``.

Additionally, we'll respond to issues in both the captain and shove projects.
