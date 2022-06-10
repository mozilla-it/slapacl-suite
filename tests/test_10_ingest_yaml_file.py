'''
    Test ingest_yaml_file
'''

import unittest
import yaml
import mock
import tests.context  # noqa F401 pylint: disable=unused-import
from slapaclsuite.readfile import ingest_yaml_file


class TestIngestYamlFile(unittest.TestCase):
    ''' Class of tests about ingesting a yaml file. '''

    def test_00_terrible_call(self):
        ''' Make sure we bomb out if we send a non-string 'filename' '''
        with self.assertRaises(TypeError):
            ingest_yaml_file([])

    def test_01_dont_read_directories(self):
        ''' Make sure we bomb out if we try to read a directory '''
        with self.assertRaises(IOError):
            ingest_yaml_file('/')

    def test_02_dont_read_nonsense(self):
        ''' Make sure we bomb out if we read a nonexistant file '''
        with self.assertRaises(IOError):
            ingest_yaml_file('/no-such-file-I-hope')

    def test_10_read_nonyaml(self):
        ''' Make sure we bomb out if we try ingesting non-yaml '''
        read_data = '"a": "b"}'
        with mock.patch('builtins.open', mock.mock_open(read_data=read_data)), \
                self.assertRaises(yaml.YAMLError):
            ingest_yaml_file('/does_not_matter')

    def test_20_read_nonyaml(self):
        ''' Make sure we get a mapping of yaml that matches what we send in '''
        read_data = '---\nalist:\n  - 1\n  - 2\nastring: "123"\n'
        with mock.patch('builtins.open', mock.mock_open(read_data=read_data)):
            retval = ingest_yaml_file('/does_not_matter')
        self.assertEqual(retval, {'alist': [1, 2], 'astring': '123'})
