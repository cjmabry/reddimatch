from fabric.api import local

def prepare_deploy():
    local("python ./tests.py")
    local("git add -p && git commit")
    local("git push origin develop")
