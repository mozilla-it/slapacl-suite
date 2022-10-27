'''
    Validate the TestValidator class
'''

import unittest
from io import StringIO
import mock
import tests.context  # noqa F401 pylint: disable=unused-import
from slapaclsuite.yaml_input_validator.test import \
        TestValidator
from slapaclsuite.yaml_input_validator.administrative import \
        AdministrativeSectionValidator


class TestTestValidateExpects(unittest.TestCase):
    ''' Check TestValidator _validate_expects '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = TestValidator()
        self.testfunc = library._validate_expects

    def test_none(self):
        ''' Every test must specifiy what they expect to get '''
        inputs = None
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_int(self):
        '''
            expects needs to be a string.  Basic failure test.
        '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_bad_str(self):
        '''
            expects needs to be 'ALLOWED' or 'DENIED' only.  Basic failure test.
        '''
        inputs = 'foo'
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_good_str(self):
        '''
            Verify that we get out what we send in.
        '''
        inputs = 'ALLOWED'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, 'ALLOWED')
        self.assertIn('## Preflighting ', fake_out.getvalue())

        inputs = 'DENIED'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=False)
        self.assertEqual(result, 'DENIED')
        self.assertEqual('', fake_out.getvalue())


class TestTestValidateRequestDN(unittest.TestCase):
    ''' Check TestValidator _validate_requestdn '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = TestValidator()
        self.testfunc = library._validate_requestdn

    def test_none(self):
        '''
            requestDN is mandatory - we have to be evaluating SOMETHING
        '''
        inputs = None
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_int(self):
        '''
            requestDN is always a string.  Basic failure test.
        '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_null_string(self):
        '''
            requestDN must exist.
        '''
        inputs = ''
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_str(self):
        '''
            requestDN is always a string.  We should get back what we send in.
        '''
        inputs = 'foo'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, inputs)
        self.assertIn('## Preflighting ', fake_out.getvalue())

    def test_subs(self):
        '''
            substitutions are acceptable for requestDN.
        '''
        admin_obj = AdministrativeSectionValidator()
        admin_obj.validate({
            'DN_substitutions_key': 'SUB:',
            'DN_substitutions': {'somebody': 'joe'}})
        inputs = 'SUB:somebody'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, admin_object=admin_obj, verbose=False)
        self.assertEqual(result, 'joe')
        self.assertEqual('', fake_out.getvalue())

    def test_no_subs(self):
        '''
            substitutions could be not-declared
        '''
        admin_obj = AdministrativeSectionValidator()
        admin_obj.validate({
            'DN_substitutions_key': None,
            'DN_substitutions': {'somebody': 'joe'}})
        inputs = 'somebody'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, admin_object=admin_obj, verbose=False)
        self.assertEqual(result, 'somebody')
        self.assertEqual('', fake_out.getvalue())


class TestTestValidateAuthcDN(unittest.TestCase):
    ''' Check TestValidator _validate_authcdn '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = TestValidator()
        self.testfunc = library._validate_authcdn

    def test_none(self):
        '''
            authcDN is not mandatory; None is acceptable.
        '''
        inputs = None
        result = self.testfunc(inputs)
        self.assertEqual(result, None)

    def test_int(self):
        '''
            authcDN is always a string.  Basic failure test.
        '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_null_string(self):
        '''
            requestDN must exist if it's a string.
        '''
        inputs = ''
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_str(self):
        '''
            authcDN is always a string.  We should get back what we send in.
        '''
        inputs = 'foo'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, inputs)
        self.assertIn('## Preflighting ', fake_out.getvalue())


class TestTestValidateRequestattr(unittest.TestCase):
    ''' Check TestValidator _validate_requestattr '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = TestValidator()
        self.testfunc = library._validate_requestattr

    def test_none(self):
        '''
            requestattr is mandatory; we have to have some attrs to evaluate.
            TECHNICALLY in slapacl requestattr can be null and it'll test 'entry'.
            For our purposes we've decided to require it, since 'entry' is boring.
        '''
        inputs = None
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_int(self):
        '''
            requestattr is always a string (or list of strings).  Basic failure test.
        '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_null_string(self):
        '''
            requestattr strings can't be empty, because, then what are we evaluating?
        '''
        inputs = ''
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_str(self):
        '''
            requestattr strings should get back what we send in.
        '''
        inputs = 'foo/bar'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=False)
        self.assertEqual(result, [inputs])
        self.assertEqual('', fake_out.getvalue())

    def test_badlist(self):
        '''
            requestattr lists must be lists of strings.
        '''
        inputs = [123]
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_empty_list(self):
        '''
            requestattr lists can not be empty
        '''
        inputs = []
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_list_null_string(self):
        '''
            requestattr lists must be nonempty strings.
        '''
        inputs = ['']
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_list(self):
        '''
            requestattr of a list of strings should get back what we send in.
        '''
        inputs = ['foo/bar']
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, inputs)
        self.assertIn('## Preflighting ', fake_out.getvalue())


class TestTestValidateFetchEntry(unittest.TestCase):
    ''' Check TestValidator _validate_fetchentry '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = TestValidator()
        self.testfunc = library._validate_fetchentry

    def test_none(self):
        '''
            fetchentry is a flag and defaults to True if nothing is specified.
        '''
        inputs = None
        result = self.testfunc(inputs)
        self.assertEqual(result, True)

    def test_int(self):
        '''
            fetchentry must be a bool.  We refuse to get fancy and eval non-bools as bools.
        '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_str(self):
        '''
            fetchentry must be a bool.  We refuse to get fancy and eval non-bools as bools.
        '''
        inputs = 'foo'
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_bool(self):
        '''
            fetchentry must be a bool.  Verify we get back what we expect.
        '''
        inputs = True
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, True)
        self.assertIn('## Preflighting ', fake_out.getvalue())

        inputs = False
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=False)
        self.assertEqual(result, False)
        self.assertEqual('', fake_out.getvalue())


class TestTestValidateSSF(unittest.TestCase):
    ''' Check TestValidator _validate_ssf '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = TestValidator()
        self.testfunc = library._validate_ssf

    def test_none(self):
        '''
            ssf is not mandatory, so a None is allowed.
        '''
        inputs = None
        result = self.testfunc(inputs)
        self.assertEqual(result, None)

    def test_int(self):
        '''
            ssf, when present, needs to be an integer
        '''
        inputs = 128
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, inputs)
        self.assertIn('## Preflighting ', fake_out.getvalue())

        inputs = 0
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=False)
        self.assertEqual(result, inputs)
        self.assertEqual('', fake_out.getvalue())

    def test_negative(self):
        '''
            ssf can't be a negative number
        '''
        inputs = -1
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_str(self):
        '''
            ssf, when present, needs to be an integer - deny strings
        '''
        inputs = '128'
        with self.assertRaises(ValueError):
            self.testfunc(inputs)


class TestTestValidatePeername(unittest.TestCase):
    ''' Check TestValidator _validate_peername '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = TestValidator()
        self.testfunc = library._validate_peername

    def test_none(self):
        '''
            peername is not mandatory, so a None is allowed.
        '''
        inputs = None
        result = self.testfunc(inputs)
        self.assertEqual(result, None)

    def test_int(self):
        '''
            peername, when present, needs to be a string (or list of strings)
            representing some kind of IP/host.  So ints are failure cases.
        '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_null_string(self):
        '''
            peername, when present, needs to be a string representing some kind of IP/host.
        '''
        inputs = ''
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_str(self):
        '''
            peername, when present, needs to be a string representing some kind of IP/host.
        '''
        inputs = '192.168.0.1'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=False)
        self.assertEqual(result, [inputs])
        self.assertEqual('', fake_out.getvalue())

    def test_null_list(self):
        '''
            lists are acceptable for peername, but they still must be strings
        '''
        inputs = []
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_badlist(self):
        '''
            lists are acceptable for peername, but they still must be strings
        '''
        inputs = [123]
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_list_null_string(self):
        '''
            lists are acceptable for peername, but they still must be strings
        '''
        inputs = ['']
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_list(self):
        '''
            lists of strings are acceptable for peername.
        '''
        inputs = ['192.168.0.1', '192.168.0.2']
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, inputs)
        self.assertIn('## Preflighting ', fake_out.getvalue())

    def test_subs(self):
        '''
            substitutions are acceptable for peername.
        '''
        admin_obj = AdministrativeSectionValidator()
        admin_obj.validate({
            'peername_substitutions_key': 'SUBME:',
            'peername_substitutions': {'somehost': '10.20.30.40'}})
        inputs = 'SUBME:somehost'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, admin_object=admin_obj, verbose=False)
        self.assertEqual(result, ['10.20.30.40'])
        self.assertEqual('', fake_out.getvalue())

    def test_no_subs(self):
        '''
            substitutions could be not-declared
        '''
        admin_obj = AdministrativeSectionValidator()
        admin_obj.validate({
            'peername_substitutions_key': None,
            'peername_substitutions': {'somehost': '10.20.30.40'}})
        inputs = 'somehost'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, admin_object=admin_obj, verbose=False)
        self.assertEqual(result, ['somehost'])
        self.assertEqual('', fake_out.getvalue())


class TestTestValidateDescription(unittest.TestCase):
    ''' Check TestValidator _validate_description '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = TestValidator()
        self.testfunc = library._validate_description

    def test_none(self):
        '''
            Every test needs a description.  We COULD require it but it technically doesn't
            matter, so just shove one in.
        '''
        inputs = None
        result = self.testfunc(inputs)
        self.assertEqual(result, 'undescribed test')

    def test_int(self):
        '''
            We need descriptions to be strings.
        '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_null_str(self):
        '''
            We don't care about null strings.  If someone provides one, that's okay.
            Change this if you ever care.
        '''
        inputs = ''
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=False)
        self.assertEqual(result, inputs)
        self.assertEqual('', fake_out.getvalue())

    def test_str(self):
        '''
            description needs to be a string.  Pass back what we are given.
        '''
        inputs = 'foo'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, inputs)
        self.assertIn('## Preflighting ', fake_out.getvalue())


class TestValidateTest(unittest.TestCase):
    ''' Check TestValidator validate '''

    def setUp(self):
        ''' define our library and testfunc for simple reading '''
        self.library = TestValidator()
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
                mock.patch.object(TestValidator,
                                  '_validate_expects', return_value='ALLOWED') as fake_expects, \
                mock.patch.object(TestValidator,
                                  '_validate_requestdn', return_value='bar') as fake_requestdn, \
                mock.patch.object(TestValidator,
                                  '_validate_authcdn', return_value='baz') as fake_authcdn, \
                mock.patch.object(TestValidator,
                                  '_validate_requestattr', return_value=[]) as fake_requestattr, \
                mock.patch.object(TestValidator,
                                  '_validate_fetchentry', return_value=True) as fake_fetchentry, \
                mock.patch.object(TestValidator,
                                  '_validate_peername', return_value=None) as fake_peername, \
                mock.patch.object(TestValidator,
                                  '_validate_description', return_value='tst') as fake_description:
            result = self.testfunc(inputs)
        fake_expects.assert_called_once_with(None, admin_object=None)
        fake_requestdn.assert_called_once_with(None, admin_object=None)
        fake_authcdn.assert_called_once_with(None, admin_object=None)
        fake_requestattr.assert_called_once_with(None, admin_object=None)
        fake_fetchentry.assert_called_once_with(None, admin_object=None)
        fake_peername.assert_called_once_with(None, admin_object=None)
        fake_description.assert_called_once_with(None, admin_object=None)
        self.assertEqual(result, True)
        self.assertEqual(self.library.inputs,
                         {'expects': 'ALLOWED',
                          'requestDN': 'bar',
                          'authcDN': 'baz',
                          'requestattr': [],
                          'fetchentry': True,
                          'peername': None,
                          'ssf': None,
                          'description': 'tst'})

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
                mock.patch.object(TestValidator, '_validate_expects',
                                  return_value='DENIED') as fake_expects, \
                mock.patch.object(TestValidator, '_validate_requestdn',
                                  return_value='bar') as fake_requestdn, \
                mock.patch.object(TestValidator, '_validate_authcdn',
                                  return_value='baz') as fake_authcdn, \
                mock.patch.object(TestValidator, '_validate_requestattr',
                                  return_value=['s']) as fake_requestattr, \
                mock.patch.object(TestValidator, '_validate_fetchentry',
                                  return_value=True) as fake_fetchentry, \
                mock.patch.object(TestValidator, '_validate_peername',
                                  return_value=None) as fake_peername, \
                mock.patch.object(TestValidator, '_validate_description',
                                  return_value='tst') as fake_description:
            result = self.testfunc(inputs)
        fake_expects.assert_called_once_with(None, admin_object=None)
        fake_requestdn.assert_called_once_with(None, admin_object=None)
        fake_authcdn.assert_called_once_with(None, admin_object=None)
        fake_requestattr.assert_called_once_with(None, admin_object=None)
        fake_fetchentry.assert_called_once_with(None, admin_object=None)
        fake_peername.assert_called_once_with(None, admin_object=None)
        fake_description.assert_called_once_with(None, admin_object=None)
        self.assertEqual(result, True)
        self.assertEqual(self.library.inputs,
                         {'expects': 'DENIED',
                          'requestDN': 'bar',
                          'authcDN': 'baz',
                          'requestattr': ['s'],
                          'fetchentry': True,
                          'peername': None,
                          'ssf': None,
                          'description': 'tst'})

    def test_dict_badval(self):
        '''
            This is a failure test for 'we received YAML-valid config but one we know nothing
            about how to process', which we fail out on.
        '''
        inputs = {'a': 1}
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_dict(self):
        '''
            A simple success test when we pass in acceptable inputs.
        '''
        inputs = {'expects': 'ALLOWED',
                  'requestDN': 'bar',
                  'authcDN': 'baz',
                  'requestattr': ['someattr'],
                  'fetchentry': True,
                  'peername': None,
                  'ssf': None,
                  'description': 'something'}
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, True)
        self.assertEqual(self.library.inputs, inputs)
        self.assertIn('# Preflighting ', fake_out.getvalue())

    def test_subs(self):
        '''
            A success test when substitutions are needed
        '''
        admin_obj = AdministrativeSectionValidator()
        admin_obj.validate({
            'DN_substitutions_key': 'SUB:',
            'DN_substitutions': {'jdoe': 'john.doe'}})
        inputs = {'expects': 'ALLOWED',
                  'requestDN': 'SUB:jdoe',
                  'authcDN': 'SUB:jdoe',
                  'requestattr': ['someattr'],
                  'fetchentry': True,
                  'peername': None,
                  'ssf': None,
                  'description': 'something'}
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, admin_object=admin_obj, verbose=False)
        self.assertEqual(result, True)
        self.assertNotEqual(self.library.inputs, inputs)
        self.assertEqual(self.library.inputs['requestDN'], 'john.doe')
        self.assertEqual(self.library.inputs['authcDN'], 'john.doe')
        self.assertEqual('', fake_out.getvalue())

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


class TestRenderTest(unittest.TestCase):
    ''' Check TestValidator render '''

    def setUp(self):
        ''' define our library and testfunc for simple reading '''
        self.library = TestValidator()
        self.testfunc = self.library.render

    def test_notready(self):
        ''' Test without validation having happened '''
        with self.assertRaises(RuntimeError):
            self.testfunc()

    def test_ready_quiet(self):
        ''' Test render passes back good values, silently '''
        inputs = {'expects': 'ALLOWED',
                  'requestDN': 'bar',
                  'authcDN': 'baz',
                  'requestattr': ['someattr'],
                  'fetchentry': True,
                  'peername': None,
                  'ssf': None,
                  'description': 'something'}
        outputs = {'expects': 'ALLOWED',
                   'requestDN': ['-b', 'bar'],
                   'authcDN': ['-D', 'baz'],
                   'requestattr': [('someattr', ['someattr'])],
                   'fetchentry': [],
                   'peername': [('any-IP', [])],
                   'ssf': [],
                   'description': 'something'}
        self.library.validate(inputs)
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(verbose=False)
        self.assertEqual(result, outputs)
        self.assertEqual('', fake_out.getvalue())

    def test_ready_noisy(self):
        ''' Test render passes back good values, not-silently '''
        inputs = {'expects': 'ALLOWED',
                  'requestDN': 'bar',
                  'authcDN': None,
                  'requestattr': ['someattr'],
                  'fetchentry': False,
                  'peername': 'someip',
                  'ssf': 128,
                  'description': 'something'}
        outputs = {'expects': 'ALLOWED',
                   'requestDN': ['-b', 'bar'],
                   'authcDN': [],
                   'requestattr': [('someattr', ['someattr'])],
                   'fetchentry': ['-u'],
                   'peername': [('someip', ['-o', 'peername=IP=someip'])],
                   'ssf': ['-o', 'ssf=128'],
                   'description': 'something'}
        self.library.validate(inputs)
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(verbose=True)
        self.assertEqual(result, outputs)
        self.assertIn('# Rendering ', fake_out.getvalue())
