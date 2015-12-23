from fabric.api import local


def test():
    local("python ./tests.py")

def commit():
    local("git add -p && git commit")

def push():
    local("git push origin develop")

def prepare_deploy():
    test()
    commit()
    push()
