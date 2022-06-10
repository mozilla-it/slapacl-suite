'''
    generate_commands
'''

import unittest
import tests.context  # noqa F401 pylint: disable=unused-import
from slapaclsuite.yaml_input_validator import validate_input
from slapaclsuite.commands import generate_commands


class TestGenerateCommands(unittest.TestCase):
    ''' Class of tests about generate_commands '''

    def setUp(self):
        self.inputs = {
            'administrative': {
                'name': 'production',
                'DN_substitutions_key': 'SUB:',
                'DN_substitutions': {
                    'foo_person': 'uid=foo,ou=logins,dc=example'
                }
            },
            'scripting': {
                'executable': 'slapacl',
                'path': ['/usr/local/sbin', '/usr/sbin'],
                'default_arguments': ['-F', '/etc/openldap/slapd.d']
            },
            'tests':
                [
                    {
                        'description': 'anonymous may auth from anywhere',
                        'requestDN': 'uid=binder,ou=logins,dc=example',
                        'requestattr': 'userPassword/auth',
                        'fetchentry': True,
                        'expects': 'ALLOWED'
                    },
                    {
                        'description': 'a user can search for bar from two IPs',
                        'authcDN': 'SUB:foo_person',
                        'requestDN': 'uid=bar,ou=logins,dc=example',
                        'requestattr': 'uid/search',
                        'fetchentry': True,
                        'peername': [
                            '10.20.30.40',
                            '20.40.60.80'
                        ],
                        'expects': 'ALLOWED'
                    },
                    {
                        'description': 'baz can not read quux from one IP',
                        'authcDN': 'uid=baz,ou=logins,dc=example',
                        'requestDN': 'uid=quux,ou=logins,dc=example',
                        'requestattr': 'uid/read',
                        'fetchentry': True,
                        'peername': '1.2.3.4',
                        'expects': 'DENIED'
                    },
                    {
                        'description': 'frob can make a new user',
                        'authcDN': 'uid=frob,ou=logins,dc=example',
                        'requestDN': 'uid=newguy,ou=logins,dc=example',
                        'requestattr': [
                            'entry/add',
                            'uid/add',
                            'objectClass/add'
                        ],
                        'fetchentry': False,
                        'peername': '1.2.3.4',
                        'expects': 'DENIED'
                    }
                ]
            }

    def test_good_inputs(self):
        ''' Good basic test '''
        config_objects = validate_input(self.inputs, verbose=False)
        result = generate_commands(config_objects)
        self.assertEqual(len(result), 7)
        self.assertEqual(
            result[0],
            ('anonymous may auth from anywhere userPassword/auth any-IP',
             {'script': ['slapacl', '-F', '/etc/openldap/slapd.d',
                         '-b', 'uid=binder,ou=logins,dc=example', 'userPassword/auth'],
              'path': ['/usr/local/sbin', '/usr/sbin'],
              'expects': 'ALLOWED'}))
        self.assertEqual(
            result[1],
            ('a user can search for bar from two IPs uid/search 10.20.30.40',
             {'script': ['slapacl', '-F', '/etc/openldap/slapd.d',
                         '-D', 'uid=foo,ou=logins,dc=example',
                         '-b', 'uid=bar,ou=logins,dc=example',
                         '-o', 'peername=IP=10.20.30.40', 'uid/search'],
              'path': ['/usr/local/sbin', '/usr/sbin'],
              'expects': 'ALLOWED'}))
        self.assertEqual(
            result[2],
            ('a user can search for bar from two IPs uid/search 20.40.60.80',
             {'script': ['slapacl', '-F', '/etc/openldap/slapd.d',
                         '-D', 'uid=foo,ou=logins,dc=example',
                         '-b', 'uid=bar,ou=logins,dc=example',
                         '-o', 'peername=IP=20.40.60.80', 'uid/search'],
              'path': ['/usr/local/sbin', '/usr/sbin'],
              'expects': 'ALLOWED'}))
        self.assertEqual(
            result[3],
            ('baz can not read quux from one IP uid/read 1.2.3.4',
             {'script': ['slapacl', '-F', '/etc/openldap/slapd.d',
                         '-D', 'uid=baz,ou=logins,dc=example',
                         '-b', 'uid=quux,ou=logins,dc=example',
                         '-o', 'peername=IP=1.2.3.4', 'uid/read'],
              'path': ['/usr/local/sbin', '/usr/sbin'],
              'expects': 'DENIED'}))
        self.assertEqual(
            result[4],
            ('frob can make a new user entry/add 1.2.3.4',
             {'script': ['slapacl', '-F', '/etc/openldap/slapd.d',
                         '-D', 'uid=frob,ou=logins,dc=example', '-u',
                         '-b', 'uid=newguy,ou=logins,dc=example',
                         '-o', 'peername=IP=1.2.3.4', 'entry/add'],
              'path': ['/usr/local/sbin', '/usr/sbin'],
              'expects': 'DENIED'}))
        self.assertEqual(
            result[5],
            ('frob can make a new user uid/add 1.2.3.4',
             {'script': ['slapacl', '-F', '/etc/openldap/slapd.d',
                         '-D', 'uid=frob,ou=logins,dc=example', '-u',
                         '-b', 'uid=newguy,ou=logins,dc=example',
                         '-o', 'peername=IP=1.2.3.4', 'uid/add'],
              'path': ['/usr/local/sbin', '/usr/sbin'],
              'expects': 'DENIED'}))
        self.assertEqual(
            result[6],
            ('frob can make a new user objectClass/add 1.2.3.4',
             {'script': ['slapacl', '-F', '/etc/openldap/slapd.d',
                         '-D', 'uid=frob,ou=logins,dc=example', '-u',
                         '-b', 'uid=newguy,ou=logins,dc=example',
                         '-o', 'peername=IP=1.2.3.4', 'objectClass/add'],
              'path': ['/usr/local/sbin', '/usr/sbin'],
              'expects': 'DENIED'}))
