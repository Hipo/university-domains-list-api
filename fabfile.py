from fabric.api import cd, env, run, sudo, prefix
from contextlib import contextmanager as _contextmanager


env.directory = '/home/ubuntu/sites/university-domains-list-api'
env.activate = 'source ./env/bin/activate'


@_contextmanager
def virtualenv():
    with cd(env.directory):
        with prefix(env.activate):
            yield


def deploy_app():
    with virtualenv():
        run('git fetch origin')
        run('git reset --hard origin/master')
        sudo('supervisorctl restart university-domains-list-api')
