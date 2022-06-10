'''
    Validate the TestsSectionValidator class
'''

import unittest
from io import StringIO
import mock
import tests.context  # noqa F401 pylint: disable=unused-import
from slapaclsuite.yaml_input_validator.tests import \
        TestsSectionValidator
from slapaclsuite.yaml_input_validator.test import \
        TestValidator


class TestTestsSectionValidate(unittest.TestCase):
    ''' Check TestsSectionValidator validate '''

    def setUp(self):
        ''' define our library and testfunc for simple reading '''
        self.library = TestsSectionValidator()
        self.testfunc = self.library.validate

    def test_none(self):
        '''
            Test with None as an input / missing section altogether.
            Tests being all missing is stupid and we print a message about this, but since
            making the tests is nothing we can assume, we return an empty list.  Oh well.
        '''
        inputs = None
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=False)
        self.assertEqual(result, [])
        self.assertIn('No tests defined', fake_out.getvalue())

    def test_int(self):
        ''' Test with a non-list, which is a simple failure test '''
        inputs = 123
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_minimums(self):
        '''
            Test with an empty list as an input.
            This is effectively the same as test_none above.
        '''
        inputs = []
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.testfunc(inputs, verbose=False)
        self.assertEqual(result, [])
        self.assertIn('No tests defined', fake_out.getvalue())

    def test_badlist(self):
        '''
            This is a failure test for 'we received YAML-valid config but one we know nothing
            about how to process', which we fail out on.
        '''
        inputs = [123]
        with self.assertRaises(ValueError):
            self.testfunc(inputs)

    def test_list(self):
        '''
            THIS test just ensures we call our subsections.  The values expressed in here do not
            necessarily reflect any sort of good test.  Those are tested over in
            the test(singular) section.
            Here we just want to make sure they're all passed as arguments and used.
        '''
        inputs = [{'test1': 1}, {'test2': 2}, {'test2': 3}]
        mock_new = mock.Mock()
        mock_new.validate.return_value = True
        with \
                mock.patch('sys.stdout', new=StringIO()) as fake_out, \
                mock.patch.object(TestValidator, '__new__', return_value=mock_new) as fake_test:
            result = self.testfunc(inputs, verbose=True)
        self.assertEqual(fake_test.call_count, len(inputs))
        self.assertEqual(result, True)
        self.assertEqual(self.library.inputs, [mock_new, mock_new, mock_new])
        self.assertIn('# Preflighting ', fake_out.getvalue())


class TestRenderTests(unittest.TestCase):
    ''' Check TestsSectionValidator render '''

    def setUp(self):
        ''' define our library and testfunc for simple reading '''
        self.library = TestsSectionValidator()
        self.testfunc = self.library.render

    def test_notready(self):
        ''' Test without validation having happened '''
        with self.assertRaises(RuntimeError):
            self.testfunc()

    def test_ready_quiet(self):
        '''
            This test checks that, if .validate did its job and loaded in some validators
            then we call off to .render on each of those objects, and pass back what they say.
            This is essentially "do we build lists?"
        '''
        tst1 = TestValidator()
        tst2 = TestValidator()
        inputs = [tst1, tst2]
        self.library.inputs = inputs
        # we skip loading with .validate because it gets complex dealing with deep classes.
        with \
                mock.patch('sys.stdout', new=StringIO()) as fake_out, \
                mock.patch.object(TestValidator, 'render', return_value='XX') as fake_test:
            result = self.testfunc(verbose=False)
        self.assertEqual(fake_test.call_count, len(inputs))
        self.assertEqual(result, ['XX', 'XX'])
        self.assertEqual('', fake_out.getvalue())

    def test_ready_noisy(self):
        ''' Test render passes back good values, not-silently '''
        tst1 = TestValidator()
        inputs = [tst1]
        self.library.inputs = inputs
        # we skip loading with .validate because it gets complex dealing with deep classes.
        with \
                mock.patch('sys.stdout', new=StringIO()) as fake_out, \
                mock.patch.object(TestValidator, 'render', return_value='XX') as fake_test:
            result = self.testfunc(verbose=True)
        self.assertEqual(fake_test.call_count, len(inputs))
        self.assertEqual(result, ['XX'])
        self.assertIn(f'# Rendering ', fake_out.getvalue())
