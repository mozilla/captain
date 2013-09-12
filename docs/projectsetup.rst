================================
Deploying a Project with Captain
================================

So you want to execute commands for your project using Captain? Great! Assuming there's an instance
of Captain running that you want to use, here's how you add your project to it:


1. Add your commands to your project.
=====================================

Captain works on the assumption that commands that projects want to run (such as deploying,
downloading new translations, etc.) are specified in the code for the project itself in a file
called ``bin/commands.procfile``.

The file is in the same format as a `Heroku Procfile`_, which specifies one command per line in
the following format:

.. code-block:: none

   mycommand: python myscript.py
   anothercommand: python manage.py some_management_command
   git_yolo: git commit -am "DEAL WITH IT" && git push -f origin master

.. warning:: Any syntax errors in the format will cause the command in question to not be
   available.

.. note:: Commands from the procfile are executed in the environment that the Shove process is
   running in. The current working directory for the command is set to the root of your project as
   specified in the Shove configuration.

.. _Heroku Procfile: https://devcenter.heroku.com/articles/procfile#declaring-process-types


2. Setup and configure Shove to recognize your project.
=======================================================

If you haven't already, set up an instance of Shove on the machine you want to run your commands on
using the directions in the :doc:`Installation documentation<install>`.

In the Shove configuration file, add an entry to the ``PROJECTS`` setting with a name for your
project and the path to the directory where your project's code is stored:

.. code-block:: python

   PROJECTS = {
       'myproject': '/data/www/myproject-web'
   }


3. Create a project entry in Captain and grant permissions.
===========================================================

Next, a user with admin access to Captain should create a new Project entry. The project will need
the queue name for the Shove instance that will be running the command (found in the Shove
configuration) and the project name used as the key in the ``PROJECTS`` setting in Shove.

It's a good practice to also create a user group using the admin interface and grant permission to
run commands on the project to that group. That way, you can just add users to the group instead of
granting permission to each individual user.

If you set up a group, you'll need to add any users that want to run commands to that group.
Otherwise, grant permission directly to the users that need it. In either case, the link for
managing object permissions can be found on the detail page for the project in the admin interface.


4. Test running a command on the project.
=========================================

Lastly, you'll need to test running a command on the project by sending a command via Captain and
inspecting the output when the result returns. If no result is returned, this may indicate a
problem with how Shove was configured, and you should check the Shove output for any errors or
warnings.

It may be useful to add a test command like ``pwd`` to the procfile to test for errors in Shove as
opposed to errors in the command itself.


Controlling Permissions
=======================

Captain controls who can run commands on projects using project-level permissions. The interface
for these permissions is a link titled "Object Permissions" on the detail page of a project in the
admin interface.

Permissions can be assigned to individual users, or groups. It is recommended that you use groups,
as it's easier to add a user to a group than to give permission to a user. Permissions can also be
revoked, or you can remove a user from a group if you're using groups to manage permissions.
