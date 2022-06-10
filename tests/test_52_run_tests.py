'''
    Test run_tests
'''
import unittest
from io import StringIO
import subprocess
import mock
import tests.context  # noqa F401 pylint: disable=unused-import
from slapaclsuite.commands import run_tests


class TestRunTests(unittest.TestCase):
    ''' Class of tests about the running of tests.  So twisty. '''

    def test_noop_run_pass(self):
        ''' Run in noop mode should tell what we would ran, but not run '''
        test_data = [('test1', {'script': ['script', 'goes', 'here'],
                                'path': ['/usr/local/sbin', '/usr/sbin'],
                                'expects': 'ALLOWED'})]
        mock_retval = subprocess.CompletedProcess(
            args=['script', 'goes', 'here'], returncode=0,
            stderr=b'authcDN: "uid=someone,dc=example"\nread access to o: ALLOWED\n')
        with mock.patch.object(subprocess, 'run', return_value=mock_retval) as mock_run, \
                mock.patch('sys.stdout', new=StringIO()) as fake_out:
            run_tests(test_data, noop=True)
        mock_run.assert_not_called()
        self.assertEqual('# test1\nscript goes here\n# expects: ALLOWED\n\n', fake_out.getvalue())

    def test_normal_run_pass(self):
        ''' normal run should run, but not print the command since we passed '''
        test_data = [('test1', {'script': ['script', 'goes', 'here'],
                                'path': ['/usr/local/sbin', '/usr/sbin'],
                                'expects': 'ALLOWED'})]
        mock_retval = subprocess.CompletedProcess(
            args=['script', 'goes', 'here'], returncode=0,
            stderr=b'authcDN: "uid=someone,dc=example"\nread access to o: ALLOWED\n')
        with mock.patch.object(subprocess, 'run', return_value=mock_retval) as mock_run, \
                mock.patch('sys.stdout', new=StringIO()) as fake_out:
            run_tests(test_data)
        mock_run.assert_called_once_with(['script', 'goes', 'here'],
                                         env={'PATH': '/usr/local/sbin:/usr/sbin'},
                                         check=True, stdout=None, stderr=subprocess.PIPE)
        self.assertEqual('', fake_out.getvalue())

    def test_verbose_run_pass(self):
        ''' verbose run should run, and do print the command even though we passed '''
        test_data = [('test1', {'script': ['script', 'goes', 'here'],
                                'path': ['/usr/local/sbin', '/usr/sbin'],
                                'expects': 'ALLOWED'})]
        mock_retval = subprocess.CompletedProcess(
            args=['script', 'goes', 'here'], returncode=0,
            stderr=b'authcDN: "uid=someone,dc=example"\nread access to o: ALLOWED\n')
        with mock.patch.object(subprocess, 'run', return_value=mock_retval) as mock_run, \
                mock.patch('sys.stdout', new=StringIO()) as fake_out:
            run_tests(test_data, verbose=True)
        mock_run.assert_called_once_with(['script', 'goes', 'here'],
                                         env={'PATH': '/usr/local/sbin:/usr/sbin'},
                                         check=True, stdout=None, stderr=subprocess.PIPE)
        self.assertEqual('PASS # test1\n', fake_out.getvalue())

    def test_normal_run_fail1(self):
        ''' failed ALLOWED should run, and do print the command because we failed '''
        test_data = [('test1', {'script': ['script', 'goes', 'here'],
                                'path': ['/usr/local/sbin', '/usr/sbin'],
                                'expects': 'ALLOWED'})]
        mock_retval = subprocess.CompletedProcess(
            args=['script', 'goes', 'here'], returncode=0,
            stderr=b'authcDN: "uid=someone,dc=example"\nread access to o: DENIED\n')
        with mock.patch.object(subprocess, 'run', return_value=mock_retval) as mock_run, \
                mock.patch('sys.stdout', new=StringIO()) as fake_out:
            run_tests(test_data)
        mock_run.assert_called_once_with(['script', 'goes', 'here'],
                                         env={'PATH': '/usr/local/sbin:/usr/sbin'},
                                         check=True, stdout=None, stderr=subprocess.PIPE)
        self.assertEqual('FAIL # test1\nscript goes here\n# expected "ALLOWED", but got "DENIED"\n',
                         fake_out.getvalue())

    def test_normal_run_fail2(self):
        ''' failed DENIED should run, and do print the command because we failed '''
        test_data = [('test1', {'script': ['script', 'goes', 'here'],
                                'path': ['/usr/local/sbin', '/usr/sbin'],
                                'expects': 'DENIED'})]
        mock_retval = subprocess.CompletedProcess(
            args=['script', 'goes', 'here'], returncode=0,
            stderr=b'authcDN: "uid=someone,dc=example"\nread access to o: ALLOWED\n')
        with mock.patch.object(subprocess, 'run', return_value=mock_retval) as mock_run, \
                mock.patch('sys.stdout', new=StringIO()) as fake_out:
            run_tests(test_data)
        mock_run.assert_called_once_with(['script', 'goes', 'here'],
                                         env={'PATH': '/usr/local/sbin:/usr/sbin'},
                                         check=True, stdout=None, stderr=subprocess.PIPE)
        self.assertEqual('FAIL # test1\nscript goes here\n# expected "DENIED", but got "ALLOWED"\n',
                         fake_out.getvalue())

    def test_normal_run_fail3(self):
        ''' errors in slapacl should stop us '''
        test_data = [('test1', {'script': ['script', 'goes', 'here'],
                                'path': ['/usr/local/sbin', '/usr/sbin'],
                                'expects': 'ALLOWED'})]

        mock_retval = subprocess.CalledProcessError(
            returncode=17, cmd=['script', 'goes', 'here'])
        with mock.patch.object(subprocess, 'run', side_effect=mock_retval) as mock_run, \
                mock.patch('sys.stdout', new=StringIO()) as fake_out:
            run_tests(test_data)
        mock_run.assert_called_once_with(['script', 'goes', 'here'],
                                         env={'PATH': '/usr/local/sbin:/usr/sbin'},
                                         check=True, stdout=None, stderr=subprocess.PIPE)
        self.assertEqual('# test1\nExecution error when running:\nscript goes here\n',
                         fake_out.getvalue())

    def test_multi_run_pass(self):
        ''' This makes sure we can handle multiple tests '''
        test_data = [('test1', {'script': ['script', 'goes', 'here'],
                                'path': ['/usr/local/sbin', '/usr/sbin'],
                                'expects': 'ALLOWED'}),
                     ('test2', {'script': ['script', 'goes', 'there'],
                                'path': ['/usr/local/sbin', '/usr/sbin'],
                                'expects': 'ALLOWED'})]
        mock_retval = subprocess.CompletedProcess(
            args=['script', 'goes', 'here'], returncode=0,
            stderr=b'authcDN: "uid=someone,dc=example"\nread access to o: ALLOWED\n')
        with mock.patch.object(subprocess, 'run', return_value=mock_retval) as mock_run, \
                mock.patch('sys.stdout', new=StringIO()) as fake_out:
            run_tests(test_data)
        self.assertEqual(mock_run.call_count, 2)
        self.assertEqual('', fake_out.getvalue())

    def test_unexpected_slapacl_response(self):
        ''' print out useful stuff if slapacl ever doesn't end in ALLOWED/DENIED '''
        test_data = [('test1', {'script': ['script', 'goes', 'here'],
                                'path': ['/usr/local/sbin', '/usr/sbin'],
                                'expects': 'ALLOWED'})]
        mock_retval = subprocess.CompletedProcess(
            args=['script', 'goes', 'here'], returncode=0,
            stderr=b'authcDN: "uid=someone,dc=example"\nsomething we never expected\n')
        with mock.patch.object(subprocess, 'run', return_value=mock_retval) as mock_run, \
                mock.patch('sys.stdout', new=StringIO()) as fake_out:
            run_tests(test_data)
        mock_run.assert_called_once_with(['script', 'goes', 'here'],
                                         env={'PATH': '/usr/local/sbin:/usr/sbin'},
                                         check=True, stdout=None, stderr=subprocess.PIPE)
        self.assertEqual(('# test1\nUnable to determine answer from `slapacl`:\n'
                          'script goes here\nauthcDN: "uid=someone,dc=example"\n'
                          'something we never expected\n\n'),
                         fake_out.getvalue())
