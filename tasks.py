# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date: 2017-09-27
# @Filename: tasks.py
# @License: BSD 3-Clause
# @Copyright: Brian Cherinka

import os

from invoke import Collection, task


# This file contains tasks that can be easily run from the shell terminal using the Invoke
# python package. If you do not have invoke, install it with pip install
# To list the tasks available, type invoke --list from the top-level repo directory

@task
def clean(ctx):
    """Cleans up the crap before a Pip build"""

    print('Cleaning')
    ctx.run('rm -rf htmlcov **/htmlcov .coverage **/.coverage')
    ctx.run('rm -rf build')
    ctx.run('rm -rf dist')
    ctx.run('rm -rf **/*.egg-info *.egg-info')


@task(clean)
def deploy(ctx, test=False):
    """Deploy the project to pypi"""

    if test is False:
        print('Deploying to Pypi!')
        repository_url = ''
    else:
        print('Deploying to Test PyPI!')
        repository_url = '--repository-url https://test.pypi.org/legacy/'

    ctx.run('python setup.py sdist bdist_wheel')
    ctx.run(f'twine upload {repository_url} dist/*')


os.chdir(os.path.dirname(__file__))

# create a collection of tasks
ns = Collection(clean, deploy)
