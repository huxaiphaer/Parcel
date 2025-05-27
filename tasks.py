from invoke import task

@task
def flake8(c):
    """Run flake8 to lint Python code."""
    c.run("flake8")

@task
def black(c):
    """Run black to format Python code."""
    c.run("black .")

@task
def isort(c):
    """Run isort to sort imports in Python code."""
    c.run("isort .")

@task
def format(c):
    """Run black, isort, and flake8."""
    black(c)
    isort(c)
    flake8(c)