'''
    Test main
'''

import unittest
from io import StringIO
import mock
import tests.context  # noqa F401 pylint: disable=unused-import
import slapaclsuite.__main__


class TestMain(unittest.TestCase):
    ''' Class of tests about the main function. '''

    def test_00_noargs(self):
        ''' Since we have mandatory parameters, this should dump us to 'usage' '''
        with mock.patch('sys.stderr', new=StringIO()) as fake_out, \
                self.assertRaises(SystemExit) as callreturn:
            slapaclsuite.__main__.main()
        self.assertEqual(callreturn.exception.code, 2)
        self.assertIn('usage: ', fake_out.getvalue())

    def test_08_junk_file(self):
        ''' Test a basic run '''
        with mock.patch.object(slapaclsuite, 'ingest_yaml_file',
                               side_effect=IOError) as mock_ingest_yaml_file, \
                mock.patch.object(slapaclsuite, 'validate_input',
                                  return_value='some2') as mock_validate_input, \
                mock.patch.object(slapaclsuite, 'generate_commands',
                                  return_value='some3') as mock_generate_commands, \
                mock.patch.object(slapaclsuite, 'run_tests') as mock_run_tests:
            retval = slapaclsuite.__main__.main(['scriptname', 'notafile.yaml'])
        mock_ingest_yaml_file.assert_called_once_with('notafile.yaml')
        mock_validate_input.assert_not_called()
        mock_generate_commands.assert_not_called()
        mock_run_tests.assert_not_called()
        self.assertFalse(retval)

    def test_10_some_file(self):
        ''' Test a basic run '''
        with mock.patch.object(slapaclsuite, 'ingest_yaml_file',
                               return_value='some1') as mock_ingest_yaml_file, \
                mock.patch.object(slapaclsuite, 'validate_input',
                                  return_value='some2') as mock_validate_input, \
                mock.patch.object(slapaclsuite, 'generate_commands',
                                  return_value='some3') as mock_generate_commands, \
                mock.patch.object(slapaclsuite, 'run_tests') as mock_run_tests:
            retval = slapaclsuite.__main__.main(['scriptname', 'somefile.yaml'])
        mock_ingest_yaml_file.assert_called_once_with('somefile.yaml')
        mock_validate_input.assert_called_once_with('some1', verbose=False)
        mock_generate_commands.assert_called_once_with('some2')
        mock_run_tests.assert_called_once_with('some3', verbose=False, noop=False)
        self.assertTrue(retval)

    def test_11_noop(self):
        ''' Test a basic noop run '''
        with mock.patch.object(slapaclsuite, 'ingest_yaml_file',
                               return_value='some1') as mock_ingest_yaml_file, \
                mock.patch.object(slapaclsuite, 'validate_input',
                                  return_value='some2') as mock_validate_input, \
                mock.patch.object(slapaclsuite, 'generate_commands',
                                  return_value='some3') as mock_generate_commands, \
                mock.patch.object(slapaclsuite, 'run_tests') as mock_run_tests:
            retval = slapaclsuite.__main__.main(['scriptname', '--noop', 'somefile.yaml'])
        mock_ingest_yaml_file.assert_called_once_with('somefile.yaml')
        mock_validate_input.assert_called_once_with('some1', verbose=False)
        mock_generate_commands.assert_called_once_with('some2')
        mock_run_tests.assert_called_once_with('some3', verbose=False, noop=True)
        self.assertTrue(retval)

    def test_12_verbose(self):
        ''' Test a basic verbose run '''
        with mock.patch.object(slapaclsuite, 'ingest_yaml_file',
                               return_value='some1') as mock_ingest_yaml_file, \
                mock.patch.object(slapaclsuite, 'validate_input',
                                  return_value='some2') as mock_validate_input, \
                mock.patch.object(slapaclsuite, 'generate_commands',
                                  return_value='some3') as mock_generate_commands, \
                mock.patch.object(slapaclsuite, 'run_tests') as mock_run_tests:
            retval = slapaclsuite.__main__.main(['scriptname', '--verbose', 'somefile.yaml'])
        mock_ingest_yaml_file.assert_called_once_with('somefile.yaml')
        mock_validate_input.assert_called_once_with('some1', verbose=True)
        mock_generate_commands.assert_called_once_with('some2')
        mock_run_tests.assert_called_once_with('some3', verbose=True, noop=False)
        self.assertTrue(retval)
