#!/usr/bin/env python


# http://stackoverflow.com/a/14050282
def check_antipackage():
    from sys import version_info
    sys_version = version_info[:2]
    found = True
    if sys_version < (3, 0):
        # 'python 2'
        from pkgutil import find_loader
        found = find_loader('antipackage') is not None
    elif sys_version <= (3, 3):
        # 'python <= 3.3'
        from importlib import find_loader
        found = find_loader('antipackage') is not None
    else:
        # 'python >= 3.4'
        from importlib import util
        found = util.find_spec('antipackage') is not None
    if not found:
        print('Install missing package "antipackage"')
        print('Example: pip install git+https://github.com/ellisonbg/antipackage.git#egg=antipackage')
        from sys import exit
        exit(1)
check_antipackage()

# ref: https://github.com/ellisonbg/antipackage
import antipackage
from github.appscode.libbuild import libbuild
from github.appscode.pysemver import semver

import os
import os.path
import subprocess
import sys
from os.path import expandvars
import yaml
from collections import Counter

libbuild.REPO_ROOT = expandvars('$GOPATH') + '/src/github.com/kubedb/cli'

RELEASE_TAG = '1.0.0'
REPO_NAME = 'go-avro-convert'

def die(status):
    if status:
        sys.exit(status)


def call(cmd, stdin=None, cwd=libbuild.REPO_ROOT, eoe=True):
    print(cwd + ' $ ' + cmd)
    status = subprocess.call([expandvars(cmd)], shell=True, stdin=stdin, cwd=cwd)
    if eoe:
        die(status)
    else:
        return status


def check_output(cmd, stdin=None, cwd=libbuild.REPO_ROOT):
    print(cwd + ' $ ' + cmd)
    return subprocess.check_output([expandvars(cmd)], shell=True, stdin=stdin, cwd=cwd)


def git_branch_exists(branch, cwd=libbuild.REPO_ROOT):
    return call('git show-ref --quiet refs/heads/{0}'.format(branch), eoe=False, cwd=cwd) == 0


def git_checkout(branch, cwd=libbuild.REPO_ROOT):
    call('git fetch --all --prune', cwd=cwd)
    call('git fetch --tags', cwd=cwd)
    if git_branch_exists(branch, cwd):
        call('git checkout {0}'.format(branch), cwd=cwd)
    else:
        call('git checkout -b {0}'.format(branch), cwd=cwd)


def git_requires_commit(tag, cwd=libbuild.REPO_ROOT):
    status = call('git rev-parse {0} >/dev/null 2>&1'.format(tag), eoe=False, cwd=cwd)
    if status == 0:
        return False
    changed_files = check_output('git diff --name-only', cwd=cwd).strip().split('\n')
    return Counter(changed_files) != Counter(['glide.lock'])


def glide_mod(glide_config, changes):
    for dep in glide_config['import']:
        if dep['package'] in changes:
            dep['version'] = changes[dep['package']]


def glide_write(f, glide_config):
    f.seek(0)
    pkg = glide_config.pop('package')
    out = 'package: ' + pkg + '\n' + yaml.dump(glide_config, default_flow_style=False)
    f.write(out)
    f.truncate()
    glide_config['package'] = pkg


class Kitten(object):
    def __init__(self):
        self.rel_deps = {}
        self.master_deps = {}
        self.rel_deps['github.com/aerokite/go-avro-convert'] = RELEASE_TAG
        self.master_deps['github.com/kubedb/go-avro-convert'] = 'master'
        print self.rel_deps
        print self.master_deps

    def release_cli(self):
        tag = RELEASE_TAG
        version = semver.parse(tag)
        release_branch = 'release-{0}.{1}'.format(version['major'], version['minor'])

        repo = libbuild.GOPATH + '/src/github.com/aerokite/' + REPO_NAME
        print(repo)
        print('----------------------------------------------------------------------------------------')
        call('git clean -xfd', cwd=repo)
        git_checkout('master', cwd=repo)
        with open(repo + '/glide.yaml', 'r+') as glide_file:
            glide_config = yaml.load(glide_file)
            glide_mod(glide_config, self.rel_deps)
            glide_write(glide_file, glide_config)
            call('glide slow', cwd=repo)
            if git_requires_commit(tag, cwd=repo):
                call('./hack/make.py', cwd=repo)
                call('git add --all', cwd=repo)
                call('git commit -a -m "Prepare release {0}"'.format(tag), cwd=repo, eoe=False)
                call('git push origin master', cwd=repo)
            else:
                call('git reset HEAD --hard', cwd=repo)
            git_checkout(release_branch, cwd=repo)
            call('git merge master', cwd=repo)
            call('git tag -fa {0} -m "Release {0}"'.format(tag), cwd=repo)
            call('git push origin {0} --tags --force'.format(release_branch), cwd=repo)
            call('rm -rf dist', cwd=repo)
            call('./hack/make.py build', cwd=repo)
            git_checkout('master', cwd=repo)
            glide_mod(glide_config, self.master_deps)
            glide_write(glide_file, glide_config)
            call('git commit -a -m "Start next dev cycle"', cwd=repo, eoe=False)
            call('git push origin master', cwd=repo)

if __name__ == "__main__":
    cat = Kitten()
    cat.release_cli()
