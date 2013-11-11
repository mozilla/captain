"""
Deployment for captain.

Requires commander (https://github.com/oremj/commander) which is installed on
the systems that need it.
"""

import os
import sys
import urllib
import urllib2

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from commander.deploy import task, hostgroups

import commander_settings as settings


@task
def update_code(ctx, tag):
    with ctx.lcd(settings.SRC_DIR):
        ctx.local("git fetch")
        ctx.local("git checkout -f %s" % tag)
        ctx.local("git submodule sync")
        ctx.local("git submodule update --init --recursive")
        ctx.local("find . -type f -name '.gitignore' -or -name '*.pyc' -delete")

@task
def update_assets(ctx):
    with ctx.lcd(settings.SRC_DIR):
        ctx.local("LANG=en_US.UTF-8 python2.6 manage.py collectstatic --noinput")

@task
def update_database(ctx):
    with ctx.lcd(settings.SRC_DIR):
        ctx.local("python2.6 manage.py syncdb")
        ctx.local("python2.6 manage.py migrate")

@task
def checkin_changes(ctx):
    ctx.local(settings.DEPLOY_SCRIPT)


@hostgroups(settings.WEB_HOSTGROUP, remote_kwargs={'ssh_key': settings.SSH_KEY})
def deploy_app(ctx):
    ctx.remote(settings.REMOTE_UPDATE_SCRIPT)
    ctx.remote('/bin/touch {0}'.format(settings.REMOTE_WSGI))


@task
def update_info(ctx, tag):
    with ctx.lcd(settings.SRC_DIR):
        ctx.local('date')
        ctx.local('git branch')
        ctx.local('git log -3')
        ctx.local('git status')
        ctx.local('git submodule status')
        ctx.local('python ./manage.py migrate --list')
        ctx.local('git rev-parse HEAD > static/revision.txt')


# these commands are run by Chief by default and so this script
# is structured to run the pieces in those, in the order
# that makes sense.
@task
def pre_update(ctx, ref=settings.UPDATE_REF):
    update_code(ref)
    update_info(ref)


@task
def update(ctx):
    update_assets()
    update_database()


@task
def deploy(ctx):
    checkin_changes()
    deploy_app()


# this is so we can use the script from the cli too!

def main():
    """
    deploy all the things
    """

    pre_update()
    update()
    deploy()

if __name__ == "__main__":
    main()
