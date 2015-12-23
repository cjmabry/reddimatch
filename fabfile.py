from fabric.api import local


def test():
    local("python ./tests.py")

def commit():
    local("git add -p && git commit")

def push(branch):
    local("git push origin" + name)

def deploy(branch="develop"):

    if branch == "master":
        pass

    test()
    commit()
    push(branch)
