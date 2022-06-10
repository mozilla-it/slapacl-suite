'''
    Validate the AdministrativeSectionValidator class
'''

import unittest
from io import StringIO
import mock
import tests.context  # noqa F401 pylint: disable=unused-import
from slapaclsuite.yaml_input_validator.administrative import \
        AdministrativeSectionValidator


class TestAdminValidateName(unittest.TestCase):
    ''' Check AdministrativeSectionValidator _validate_name '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = AdministrativeSectionValidator()
        self.testfunc = library._validate_name

    def test_none(self):
        '''
            Send in None, get back a default name.
            We don't actually use this right now, but I could see wanting to.
        '''
        inputs = None
        result = self.testfunc(inputs)
        self.assertEqual(result, 'default-test-suite')

    def test_nullstring(self):
        '''
            An empty string is not allowed, but since we don't care, just pivot to defaults.
        '''
        inputs = ''
        result = self.testfunc(inputs)
        self.assertEqual(result, 'default-test-suite')

    def test_int(self):
        '''
            The name needs to be a string.  Basic failure test.
        '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_str(self):
        '''
            Verify that we get out what we send in.
        '''
        inputs = 'foo'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, 'foo')
        self.assertIn('## Preflighting ', fake_out.getvalue())


class TestAdminValidateDNSubKey(unittest.TestCase):
    ''' Check AdministrativeSectionValidator _validate_dn_sub_key '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = AdministrativeSectionValidator()
        self.testfunc = library._validate_dn_sub_key

    def test_none(self):
        '''
            Susbtitutions are not mandatory.  If someone doesn't specify a string,
            None is what they imply.
        '''
        inputs = None
        result = self.testfunc(inputs)
        self.assertEqual(result, None)

    def test_int(self):
        '''
            Integers (and other nonstrings) are not allowed, since the subs have to
            be a string match
        '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_nullstring(self):
        '''
            An empty string is not allowed as it would always match, and cause pain.
            Currently we're (strictly) bombing here, but I could see us pivoting to
            subbing in None as a valid response.
        '''
        inputs = ''
        with self.assertRaises(ValueError):
            self.testfunc(inputs)
        # Possible alternate future:
        # result = self.testfunc(inputs)
        # self.assertEqual(result, None)

    def test_str(self):
        '''
           Verify that we get out what we send in (if it's non-empty)
        '''
        inputs = 'foo'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, 'foo')
        self.assertIn('## Preflighting ', fake_out.getvalue())


class TestAdminValidateDNSubs(unittest.TestCase):
    ''' Check AdministrativeSectionValidator _validate_dn_subs '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = AdministrativeSectionValidator()
        self.testfunc = library._validate_dn_subs

    def test_none(self):
        '''
            Susbtitutions are not mandatory.  If someone doesn't specify a dict,
            make an empty dict for them.
        '''
        inputs = None
        result = self.testfunc(inputs)
        self.assertEqual(result, {})

    def test_int(self):
        ''' Simple bad-argument test, integers '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_str(self):
        ''' Simple bad-argument test, strings '''
        inputs = 'foo'
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_dict_empty(self):
        '''
            Susbtitutions are not mandatory.  If someone sends an empty dict, fine.
        '''
        inputs = {}
        result = self.testfunc(inputs)
        self.assertEqual(result, {})

    def test_dict_badkey(self):
        '''
            Dicts must be string: string; fail if keys are nonstring.
        '''
        inputs = {1: 'b'}
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_dict_badval(self):
        '''
            Dicts must be string: string; fail if values are nonstring.
        '''
        inputs = {'a': 1}
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_dict_null_key(self):
        '''
            Dicts must be string: string; fail if keys are empty.
            I could see changing this if there's a reason but I can't imagine one.
        '''
        inputs = {'': 'b'}
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_dict_null_val(self):
        '''
            Dicts must be string: string; fail if values are empty.
            I could see changing this if there's a reason but I can't imagine one.
        '''
        inputs = {'a': ''}
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_dict(self):
        '''
            Dicts must be string: string; verify we get back what we send in.
        '''
        inputs = {'a': 'b'}
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, {'a': 'b'})
        self.assertIn('## Preflighting ', fake_out.getvalue())


class TestValidateAdministrative(unittest.TestCase):
    ''' Check AdministrativeSectionValidator validate '''

    def setUp(self):
        ''' define our library and testfunc for simple reading '''
        self.library = AdministrativeSectionValidator()
        self.testfunc = self.library.validate

    def test_none(self):
        '''
            Test with None as an input / missing section altogether.
            THIS test just ensures we call our subsections.  The values expressed in here do not
            necessarily reflect any sort of match with the subtasks.  Those are tested above.
            Here we just want to make sure they're all called and used.
        '''
        inputs = None
        with \
                mock.patch.object(AdministrativeSectionValidator,
                                  '_validate_name', return_value='foo') as fake_name, \
                mock.patch.object(AdministrativeSectionValidator,
                                  '_validate_dn_sub_key', return_value='bar') as fake_dskey, \
                mock.patch.object(AdministrativeSectionValidator,
                                  '_validate_dn_subs', return_value={}) as fake_ds:
            result = self.testfunc(inputs)
        fake_name.assert_called_once_with(None)
        fake_dskey.assert_called_once_with(None)
        fake_ds.assert_called_once_with(None)
        self.assertEqual(result, True)
        self.assertEqual(self.library.inputs,
                         {'name': 'foo',
                          'DN_substitutions_key': 'bar',
                          'DN_substitutions': {}})

    def test_int(self):
        ''' Test with a non-dict, which is a simple failure test '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_minimums(self):
        '''
            Test with an empty dict as an input.
            This is effectively the same as test_none above.
        '''
        inputs = {}
        with \
                mock.patch.object(AdministrativeSectionValidator,
                                  '_validate_name', return_value='foo') as fake_name, \
                mock.patch.object(AdministrativeSectionValidator,
                                  '_validate_dn_sub_key', return_value='bar') as fake_dskey, \
                mock.patch.object(AdministrativeSectionValidator,
                                  '_validate_dn_subs', return_value={}) as fake_ds:
            result = self.testfunc(inputs)
        fake_name.assert_called_once_with(None)
        fake_dskey.assert_called_once_with(None)
        fake_ds.assert_called_once_with(None)
        self.assertEqual(result, True)
        self.assertEqual(self.library.inputs,
                         {'name': 'foo',
                          'DN_substitutions_key': 'bar',
                          'DN_substitutions': {}})

    def test_dict_badval(self):
        '''
            This is a failure test for 'we received YAML-valid config but one we know nothing
            about how to process', which we fail out on.
        '''
        inputs = {'a': 'b'}
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_dict(self):
        '''
            A simple success test when we pass in acceptable inputs.
        '''
        inputs = {'name': 'something',
                  'DN_substitutions_key': 'SUB:',
                  'DN_substitutions': {'a': 'b'}}
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, True)
        self.assertEqual(self.library.inputs, inputs)
        self.assertIn('# Preflighting ', fake_out.getvalue())

    def test_anti_hacking(self):
        '''
            This test is awkward, so needs explaining.
            We have a dict that is {funcstring: attributestring}
            If somehow that dict gets altered (never should happen) then one can add weird
            values that aren't method calls.  If that happens, we should die off.
        '''
        inputs = {}
        self.library.validating_functions = {'not_a_method': 'a'}
        with self.assertRaises(ValueError):
            self.testfunc(inputs)


class TestRenderAdministrative(unittest.TestCase):
    ''' Check AdministrativeSectionValidator render '''

    def setUp(self):
        ''' define our library and testfunc for simple reading '''
        self.library = AdministrativeSectionValidator()
        self.testfunc = self.library.render

    def test_notready(self):
        ''' Test without validation having happened '''
        with self.assertRaises(RuntimeError):
            self.testfunc()

    def test_ready_quiet(self):
        ''' Test render passes back good values, silently '''
        inputs = {'name': 'something',
                  'DN_substitutions_key': 'SUB:',
                  'DN_substitutions': {'a': 'b'}}
        self.library.validate(inputs)
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(verbose=False)
        self.assertEqual(result, inputs)
        self.assertEqual('', fake_out.getvalue())

    def test_ready_noisy(self):
        ''' Test render passes back good values, not-silently '''
        inputs = {'name': 'something',
                  'DN_substitutions_key': 'SUB:',
                  'DN_substitutions': {'a': 'b'}}
        self.library.validate(inputs)
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(verbose=True)
        self.assertEqual(result, inputs)
        self.assertIn('# Rendering ', fake_out.getvalue())
