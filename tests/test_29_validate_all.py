'''
    Validate the validate_input non-class function that hides all the classes
'''
import unittest
from io import StringIO
import mock
import tests.context  # noqa F401 pylint: disable=unused-import
from slapaclsuite.yaml_input_validator.all import validate_input
from slapaclsuite.yaml_input_validator.administrative import \
        AdministrativeSectionValidator
from slapaclsuite.yaml_input_validator.scripting import \
        ScriptingSectionValidator
from slapaclsuite.yaml_input_validator.tests import \
        TestsSectionValidator


class TestYAMLValidatorAll(unittest.TestCase):
    ''' Class of tests about validate_input. '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        self.testfunc = validate_input

    def test_none(self):
        '''
            This function is aboout validating input.  So, uh, have inputs.
        '''
        inputs = None
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_int(self):
        '''
            The YAML has to be a dictionary, simple failure test.
        '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_minimums(self):
        '''
            This isn't a very interesting test, it just exists to make sure that all our
            subclasses are called.  The results are fake, just verifying that we use
            what the subtests provide.  Quality of those responses are not our job.
        '''
        inputs = {}
        mock_adm = mock.Mock()
        mock_adm.validate.return_value = 'ad'
        mock_scripting = mock.Mock()
        mock_scripting.validate.return_value = 'sc'
        mock_tester = mock.Mock()
        mock_tester.validate.return_value = 'ts'
        with \
                mock.patch.object(AdministrativeSectionValidator, '__new__',
                                  return_value=mock_adm), \
                mock.patch.object(ScriptingSectionValidator, '__new__',
                                  return_value=mock_scripting), \
                mock.patch.object(TestsSectionValidator, '__new__',
                                  return_value=mock_tester):
            result = self.testfunc(inputs, verbose=False)
        self.assertEqual(result, {'administrative': mock_adm,
                                  'scripting': mock_scripting,
                                  'tests': mock_tester})
        mock_adm.validate.assert_called_once_with(None, verbose=False)
        mock_scripting.validate.assert_called_once_with(None, verbose=False)
        mock_tester.validate.assert_called_once_with(None, admin_object=mock_adm, verbose=False)

    def test_dict(self):
        '''
            This test validates that we use values sent in, send them to subclasses, and
            pass along the results.  The results are fake, just verifying that we use
            what the subtests provide.  Quality of those responses are not our job.
        '''
        inputs = {'administrative': 'inad', 'scripting': 'insc', 'tests': 'ints'}
        mock_adm = mock.Mock()
        mock_adm.validate.return_value = 'ad'
        mock_scripting = mock.Mock()
        mock_scripting.validate.return_value = 'sc'
        mock_tester = mock.Mock()
        mock_tester.validate.return_value = 'ts'
        with \
                mock.patch.object(AdministrativeSectionValidator, '__new__',
                                  return_value=mock_adm), \
                mock.patch.object(ScriptingSectionValidator, '__new__',
                                  return_value=mock_scripting), \
                mock.patch.object(TestsSectionValidator, '__new__',
                                  return_value=mock_tester):
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, {'administrative': mock_adm,
                                  'scripting': mock_scripting,
                                  'tests': mock_tester})
        mock_adm.validate.assert_called_once_with('inad', verbose=True)
        mock_scripting.validate.assert_called_once_with('insc', verbose=True)
        mock_tester.validate.assert_called_once_with('ints', admin_object=mock_adm, verbose=True)

    def test_dict_with_false(self):
        '''
            Verify that this function terminates the execution if a subclass doesn't return True.
        '''
        inputs = {'administrative': 'inad', 'scripting': 'insc', 'tests': 'ints'}

        mock_adm = mock.Mock()
        mock_adm.validate.return_value = True
        mock_scripting = mock.Mock()
        mock_scripting.validate.return_value = True
        mock_tester = mock.Mock()
        mock_tester.validate.return_value = False
        with \
                mock.patch.object(AdministrativeSectionValidator, '__new__',
                                  return_value=mock_adm), \
                mock.patch.object(ScriptingSectionValidator, '__new__',
                                  return_value=mock_scripting), \
                mock.patch.object(TestsSectionValidator, '__new__',
                                  return_value=mock_tester), \
                mock.patch('sys.stderr', new=StringIO()) as fake_err, \
                self.assertRaises(SystemExit):
            self.testfunc(inputs, verbose=False)
        mock_adm.validate.assert_called_once_with('inad', verbose=False)
        mock_scripting.validate.assert_called_once_with('insc', verbose=False)
        mock_tester.validate.assert_called_once_with('ints', admin_object=mock_adm, verbose=False)
        self.assertIn('Unexpected validation return ', fake_err.getvalue())

    def test_dict_with_failure(self):
        '''
            Verify that this function terminates the execution if a subclass raises an error.
        '''
        inputs = {'administrative': 'inad', 'scripting': 'insc', 'tests': 'ints'}

        mock_adm = mock.Mock()
        mock_adm.validate.return_value = True
        mock_scripting = mock.Mock()
        mock_scripting.validate.return_value = True
        mock_tester = mock.Mock()
        mock_tester.validate.side_effect = ValueError('oops')
        with \
                mock.patch.object(AdministrativeSectionValidator, '__new__',
                                  return_value=mock_adm), \
                mock.patch.object(ScriptingSectionValidator, '__new__',
                                  return_value=mock_scripting), \
                mock.patch.object(TestsSectionValidator, '__new__',
                                  return_value=mock_tester), \
                mock.patch('sys.stderr', new=StringIO()) as fake_err, \
                self.assertRaises(SystemExit):
            self.testfunc(inputs, verbose=False)
        mock_adm.validate.assert_called_once_with('inad', verbose=False)
        mock_scripting.validate.assert_called_once_with('insc', verbose=False)
        mock_tester.validate.assert_called_once_with('ints', admin_object=mock_adm, verbose=False)
        self.assertIn('oops', fake_err.getvalue())
