''' Packaging script '''

import os
import subprocess
from setuptools import setup


def git_version():
    ''' Return the git revision as a string '''
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for envvar in ['SYSTEMROOT', 'PATH']:
            val = os.environ.get(envvar)
            if val is not None:
                env[envvar] = val
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        git_revision = out.strip().decode('ascii')
    except OSError:
        git_revision = u"Unknown"

    return git_revision


setup(
    description=('Tool for building a suite of slapacl / LDAP access tests.\n' +
                 'This package is built upon commit ' + git_version()),
)
