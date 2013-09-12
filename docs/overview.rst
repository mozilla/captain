========
Overview
========

Captain Shove is a system for remote command execution for multiple projects via a central
frontend. Projects define a whitelist of acceptable commands. Users use the Captain web frontend to
execute commands on a remote machine running a Shove daemon. Captain then shows info about the
result of executing that command including the return code, console log and its current favorite
ice cream flavor.

Captain_ is the frontend portion of the system, and is a Django_ project. Shove_ is a process that
executes commands on the remote machine. The two systems communicate via RabbitMQ_; Captain  sends
messages to Shove processes via queues, and Shove processes send the results and logs of command
executions back to Captain via queues.

.. _Captain: https://github.com/mozilla/captain
.. _Django: https://www.djangoproject.com/
.. _Shove: https://github.com/mozilla/shove
.. _RabbitMQ: http://www.rabbitmq.com/


Server Architecture
===================

Since we (Mozilla) built it for our own setup, Captain Shove was designed with a few things in
mind:

* Servers are organized into clusters, and each cluster may host one or more projects.
* Each cluster has at least one "admin" node, which performs tasks like minifying CSS and JS or
  pulling translation files during a deployment. Once these tasks are done, the admin node syncs
  code on the other servers in the cluster that actually serve the site.
* Admin nodes perform commands for all the projects in the cluster.
* The commands we want to execute should be executed on the admin node; executing commands on each
  individual application server is handled by another system (in our case, commander_).
* There is a single RabbitMQ cluster that most admin nodes already connect to for other reasons.

In our setup, Captain lives in its own cluster, and Shove processes are installed on any admin node
that we want to run commands on. The :doc:`project setup documentation<projectsetup>` has more info
on how to register an individual project with Captain.

.. _commander: https://github.com/oremj/commander


Captain
=======

Captain is a Django-based site that presents an interface for sending commands to Shove and showing
the results of those commands. Users log into Captain using `Persona`_ and are given permission by
an administrator to run commands on certain projects registered with Captain.

.. note:: The command history and logs are visible to all users who can access the site; we run
   Captain behind a VPN so the logs aren't visible to the public.

.. _Persona: https://persona.org/


Shove
=====

The Shove process runs on the admin nodes for each cluster and is responsible for executing
commands it receives from Captain. The Shove configuration includes a dictionary that maps project
names to directories on the filesystem of the admin node. These directories are usually a checkout
of the project's repository, and all commands are run with this directory as the working directory.

Shove will only run whitelisted commands; each project should have a whitelist stored in the
``bin/commands.procfile`` relative to the project's directory in the Shove configuration. A
procfile maps a command name to an actual shell command. When Shove receives an order, it looks up
the procfile for the requested project, and looks for a command matching the command name in the
order. If it finds one, it executes that command and sends the logs back to Captain.


Communication Flow
==================

Captain and Shove communicate via RabbitMQ. Each instance of Shove creates a queue that it listens
to for commands. When you create a project in Captain, you give it the name of this queue, and
Captain will send commands for that project to the queue.

Once Shove has executed a command, it sends the return code and logs back to a log event queue
specified in the command it received. A process included in the Captain codebase listens to this
queue and updates Captain's database with the results of the command when it receives these events.

The following is a diagram of the processes and queues involved with the system:

.. code-block:: none

   .-----------------.                      .-----------------------.
   | Captain Server  |                      |RabbitMQ               |
   |-----------------|                      |-----------------------|
   |  .-----------.  |                      |      +---------+      |
   |  |Captain Log|<-+-- Reads log events --+------|Log Queue|<-----+------- Sends log events -----------.
   |  |  Process  |  |                      |      +---------+      |                                    |
   |  '-----------'  |                      |                       |                  .-------------.   |
   |                 |                      |                       |                  | Admin Node  |   |
   |                 |                      |                       |                  |-------------|   |
   |                 |                      |                       |                  |  .-------.  |   |
   |                 |                      |      .-----------.    |                  |  | Shove |  |   |
   |                 |                      |  .-->|Shove Queue|----+- Reads commands -+->|Process|--+---|
   |                 |                      |  |   '-----------'    |                  |  '-------'  |   |
   |                 |                      |  |                    |                  '-------------'   |
   |  .-----------.  |                      |  |                    |                                    |
   |  |Captain Web|--+--- Sends commands ---+--|                    |                  .-------------.   |
   |  |  Process  |  |                      |  |                    |                  | Admin Node  |   |
   |  '-----------'  |                      |  |                    |                  |-------------|   |
   '-----------------'                      |  |                    |                  |  .-------.  |   |
                                            |  |   .-----------.    |                  |  | Shove |  |   |
                                            |  '-->|Shove Queue|----+- Reads commands -+->|Process|--+---'
                                            |      '-----------'    |                  |  '-------'  |
                                            '-----------------------'                  '-------------'

Security
========

There are a few features to point out when evaluating the security of Captain Shove:

* Commands are whitelisted by the procfile for each project, so only developers with commit access
  to a project's repository can specify a command to run.
* RabbitMQ includes access control features that allow you to restrict certain users to only be
  able to read or write to certain queues. For example, Shove users should only be able to read
  their own queues and write to the log queue, and the Captain user should only be able to read the
  log queue and write to the Shove queues.

  You can also encapsulate all of these operations in a RabbitMQ virtual host to keep other users
  away from interacting with the Captain Shove system.
* Captain uses standard Django username/password authentication for the admin interface, and
  Persona authentication for the user-facing side. Admins can create projects and grant permissions
  (using the `django-guardian`_ library) to certain users to allow them to run commands on a
  project.

.. _django-guardian: http://django-guardian.readthedocs.org/


Example Flow
============

The following is an example from start to finish of executing a command with Captain Shove:

1.  User logs into Captain via Persona.
2.  User enters a command named "pwd" into a form for the "Firefox Flicks" project and submits.
3.  Captain creates a log entry in it's database for this submission.
4.  Knowing that Flicks is on the "generic" cluster, Captain sends a message to the queue for the
    generic cluster that contains an order to run the "pwd" command on the "Firefox Flicks" project
    as well as the ID of the log entry it created and the name of the queue it is listening for log
    events on.

       * The user sees a message confirming the command has been sent and will have to revisit the
         page after the results are saved to be able to view the output.

5.  The Shove process on the generic cluster admin node, which has been listening on the generic
    cluster queue, receives the message and looks up the directory for "Firefox Flicks" in it's
    configuration.
6.  Once it finds the directory, Shove reads in the procfile for Flicks and looks for a command
    named "pwd".
7.  When it finds the command, it takes the shell command listed in the procfile and spins off a
    subprocess to execute the command.
8.  Shove waits for the command to finish and captures the output of the command, including any
    errors, and the return code.
9.  Shove combines the output of the command, return code, and the ID of the log entry in Captain
    into a log event message and sends it to the logging queue specified in the command from
    Captain.
10. The Captain logging process, which is listening on the logging queue, receives the logging
    event and saves the output and return code to the log in the database specified by the log
    entry ID.
