from fabric.api import local, env, execute, task, lcd
from fabric.state import output

project = "tflsgo"

env.warn_only = True

log = ['stdout', 'status', 'aborts',  'users', 'exceptions', 'user']
ignore = ['warnings', 'debug', 'stderr', 'exceptions', 'status', 'aborts', 'user']

for level in output:
    if level in ignore:
        output[level] = False


def create(project):
    # with settings(warn_only=True):
    result = local('heroku apps:create --json {}'.format(project))

    if not result.failed:
        print("Cloned git project")


def copy(directory):
    if local('cp -aH ../tflsgo_comp/* {}'.format(directory)).failed:
        print("Error copying")

    if local('cp -aH ../requirements.txt {}'.format(directory)).failed:
        print("Error copying requirements")

    local('rm -Rf {}/__pycache__'.format(directory))
    local('rm -Rf __pycache__')
    print("Copied {} -> git".format(directory))

def get_info():
    result_info = local('heroku apps:info tflsgo', capture=True)

    if result_info.failed:
        print("Error: tflsgo is not defined")

    info = dict()

    for line in result_info.split('\n'):
        if ':' not in line:
            continue

        name, val = line.split(':', 1)
        value = val.strip()

        if value.strip():
            info[name] = value.strip()

    return info


def git_clone(git_url):
    result = local('git clone {}'.format(git_url))

    if not result.failed:
        print("Cloned project")


def git_deploy():
    with lcd(project):
        local('echo *.pyc >.gitignore')
        local('echo "web: gunicorn api:app" >Procfile')
        local('git add *')
        local('git add .gitignore')


@task
def git_push(message):
    with lcd(project):
        local('git commit -am "{}"'.format(message))
        local('git push')

@task(default=True)
def deploy(message=""):
    """fab [environment] deploy"""
    create(project)
    info = get_info()
    git_url = info['Git URL']
    web_url = info['Web URL']
    git_clone(git_url)
    copy(project)
    execute(git_deploy)

    if message:
        git_push(message)

    print("Run {}".format(web_url))

@task
def off():
    local('heroku maintance:on --app {}'.format(project))

@task
def on():
    local('heroku maintance:off --app {}'.format(project))
