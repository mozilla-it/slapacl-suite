'''
    possible_peername_substitutions
'''

import unittest
import tests.context  # noqa F401 pylint: disable=unused-import
from slapaclsuite.yaml_input_validator.administrative import \
        AdministrativeSectionValidator


class TestPossiblePeernameSubs(unittest.TestCase):
    ''' Class of tests about possible_peername_substitutions. '''

    def setUp(self):
        ''' prepare a testfunction for simplicity '''
        self.library = AdministrativeSectionValidator()
        self.testfunc = self.library.possible_peername_substitutions

    def test_01_no_prevalidation(self):
        ''' Test that we bomb out when we don't prep the object '''
        with self.assertRaises(RuntimeError):
            self.testfunc('foo')

    def test_02_junk_inputs(self):
        ''' Test that not-a-string input is handled well '''
        self.library.validate({
            'peername_substitutions_key': 'SUB:',
            'peername_substitutions': {'person1': 'jdoe'}})
        with self.assertRaises(ValueError):
            self.testfunc(None)

    def test_03_no_overlap(self):
        ''' Test that non-substitutions are handled well '''
        self.library.validate({
            'peername_substitutions_key': 'SUB:',
            'peername_substitutions': {'person1': 'jdoe'}})
        result = self.testfunc('bar')
        self.assertEqual(result, 'bar')

    def test_04_incorrect_overlap(self):
        ''' Test that non-substitutions that look like subs are handled well: no sub '''
        self.library.validate({
            'peername_substitutions_key': 'SUB:',
            'peername_substitutions': {'person1': 'jdoe'}})
        result = self.testfunc('person1')
        self.assertEqual(result, 'person1')

    def test_05_incomplete_overlap(self):
        ''' Test that no-value subs are handled well: no sub '''
        self.library.validate({
            'peername_substitutions_key': 'SUB:',
            'peername_substitutions': {'person1': 'jdoe'}})
        result = self.testfunc('SUB:')
        self.assertEqual(result, 'SUB:')

    def test_06_unspecified_sub(self):
        ''' Test that unfound entries are not sub'ed '''
        self.library.validate({
            'peername_substitutions_key': 'SUB:',
            'peername_substitutions': {'person1': 'jdoe'}})
        result = self.testfunc('SUB:person2')
        self.assertEqual(result, 'SUB:person2')

    def test_10_success(self):
        ''' Test that found entries are sub'ed '''
        self.library.validate({
            'peername_substitutions_key': 'SUB:',
            'peername_substitutions': {'person1': 'jdoe'}})
        result = self.testfunc('SUB:person1')
        self.assertEqual(result, 'jdoe')
