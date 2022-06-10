'''
    Validate the ScriptingSectionValidator class
'''

import unittest
from io import StringIO
import mock
import tests.context  # noqa F401 pylint: disable=unused-import
from slapaclsuite.yaml_input_validator.scripting import \
        ScriptingSectionValidator


class TestScriptValidateExec(unittest.TestCase):
    ''' Check ScriptingSectionValidator _validate_executable '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = ScriptingSectionValidator()
        self.testfunc = library._validate_executable

    def test_none(self):
        '''
            If we send in None, get back a default answer of the executable 'slapacl'
            Comes with a warning because we really should have a config that tells explicitly how
            the tests should be called on this host.
        '''
        inputs = None
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=False)
        self.assertEqual(result, 'slapacl')
        self.assertIn('Defaulting to using "slapacl" as the executable', fake_out.getvalue())

    def test_int(self):
        '''
            The executable must be a string.  Basic failure test.
        '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_nullstring(self):
        '''
            An empty string is not allowed, but since we don't care, just pivot to defaults.
        '''
        inputs = ''
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=False)
        self.assertEqual(result, 'slapacl')
        self.assertIn('Defaulting to using "slapacl" as the executable', fake_out.getvalue())

    def test_str(self):
        '''
           Verify that we get out what we send in (if it's non-empty)
        '''
        inputs = 'foo'
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, 'foo')
        self.assertIn('## Preflighting ', fake_out.getvalue())


class TestScriptValidatePath(unittest.TestCase):
    ''' Check ScriptingSectionValidator _validate_path '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = ScriptingSectionValidator()
        self.testfunc = library._validate_path

    def test_none(self):
        '''
            Specifying a PATH is a good idea but I can't say it's absolutely necessary.
            Maybe someone made their executable fully pathed.  Give back an empty list.
        '''
        inputs = None
        result = self.testfunc(inputs)
        self.assertEqual(result, [])

    def test_int(self):
        '''
            Bad input, don't accept this.
        '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_str(self):
        '''
            TECHNICALLY we could accept this, but PATH is 'always' multiples so force people
            to make it look right.
        '''
        inputs = 'foo'
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_nonpath(self):
        '''
            PATH entries should be /some/path; don't accept it if it's not.
            Might be an IMPROVEME here for windows pathing, but I don't care right now.
        '''
        inputs = ['not-a-path']
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_list(self):
        '''
            PATHs passed in should be passed back out unchanged.
        '''
        inputs = ['/usr/bin']
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, ['/usr/bin'])
        self.assertIn('## Preflighting ', fake_out.getvalue())


class TestScriptValidateDefArgs(unittest.TestCase):
    ''' Check ScriptingSectionValidator _validate_default_arguments '''

    def setUp(self):
        ''' define our testfunc for simple reading '''
        library = ScriptingSectionValidator()
        self.testfunc = library._validate_default_arguments

    def test_none(self):
        '''
            default arguments are not mandatory at all.
        '''
        inputs = None
        result = self.testfunc(inputs)
        self.assertEqual(result, [])

    def test_int(self):
        '''
            default arguments DO have to be a list of strings.  basic failure test.
        '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_str(self):
        '''
            default arguments DO have to be a list of strings.  basic failure test.
        '''
        inputs = 'foo'
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_list_empty(self):
        '''
            default arguments have to be a list of strings.  An empty list is fine.
        '''
        inputs = []
        result = self.testfunc(inputs)
        self.assertEqual(result, [])

    def test_nonstring(self):
        '''
            default arguments have to be a list of strings.  testing internal contents.
        '''
        inputs = [123]
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_nullstring(self):
        '''
            default arguments have to be a list of strings.  empty is weird, don't allow it.
        '''
        inputs = ['']
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_list(self):
        '''
            default arguments can be ['-foo'] or maybe ['-o', 'something']
        '''
        inputs = ['-foo']
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(result, ['-foo'])
        self.assertIn('## Preflighting ', fake_out.getvalue())


class TestValidateScripting(unittest.TestCase):
    ''' Check ScriptingSectionValidator validate '''

    def setUp(self):
        ''' define our library and testfunc for simple reading '''
        self.library = ScriptingSectionValidator()
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
                mock.patch.object(ScriptingSectionValidator,
                                  '_validate_executable', return_value='foo') as fake_executable, \
                mock.patch.object(ScriptingSectionValidator,
                                  '_validate_path', return_value=[]) as fake_path, \
                mock.patch.object(ScriptingSectionValidator,
                                  '_validate_default_arguments', return_value=[]) as fake_defargs:
            result = self.testfunc(inputs)
        fake_executable.assert_called_once_with(None)
        fake_path.assert_called_once_with(None)
        fake_defargs.assert_called_once_with(None)
        self.assertEqual(result, True)
        self.assertEqual(self.library.inputs,
                         {'executable': 'foo',
                          'path': [],
                          'default_arguments': []})

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
                mock.patch.object(ScriptingSectionValidator,
                                  '_validate_executable', return_value='foo') as fake_executable, \
                mock.patch.object(ScriptingSectionValidator,
                                  '_validate_path', return_value=[]) as fake_path, \
                mock.patch.object(ScriptingSectionValidator,
                                  '_validate_default_arguments', return_value=[]) as fake_defargs:
            result = self.testfunc(inputs)
        fake_executable.assert_called_once_with(None)
        fake_path.assert_called_once_with(None)
        fake_defargs.assert_called_once_with(None)
        self.assertEqual(result, True)
        self.assertEqual(self.library.inputs,
                         {'executable': 'foo',
                          'path': [],
                          'default_arguments': []})

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
        inputs = {'executable': 'slapacl',
                  'path': [],
                  'default_arguments': []}
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


class TestRenderScripting(unittest.TestCase):
    ''' Check ScriptingSectionValidator render '''

    def setUp(self):
        ''' define our library and testfunc for simple reading '''
        self.library = ScriptingSectionValidator()
        self.testfunc = self.library.render

    def test_notready(self):
        ''' Test without validation having happened '''
        with self.assertRaises(RuntimeError):
            self.testfunc()

    def test_ready_quiet(self):
        ''' Test render passes back good values, silently '''
        inputs = {'executable': 'slapacl',
                  'path': ['/usr/bin'],
                  'default_arguments': ['-F']}
        self.library.validate(inputs)
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(verbose=False)
        self.assertEqual(result, inputs)
        self.assertEqual('', fake_out.getvalue())

    def test_ready_noisy(self):
        ''' Test render passes back good values, not-silently '''
        inputs = {'executable': 'slapacl',
                  'path': ['/usr/bin'],
                  'default_arguments': ['-F']}
        self.library.validate(inputs)
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(verbose=True)
        self.assertEqual(result, inputs)
        self.assertIn('# Rendering ', fake_out.getvalue())
