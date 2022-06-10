#!/usr/bin/python3
'''

    Script to run through a set of tests and make sure that your
    ldap servers are allowing/denying the correct things.

    Consult slapacl(1), slapd.access(5), and
    https://www.openldap.org/doc/admin24/access-control.html

'''
import sys
import argparse
import slapaclsuite


def main(prog_args=None):
    ''' main function '''
    if prog_args is None:
        prog_args = sys.argv
    parser = argparse.ArgumentParser()
    parser.description = 'Script to run batches of slapacl checks'
    parser.add_argument('--noop',
                        action='store_true',
                        default=False,
                        dest='noop',
                        help='print commands without running')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        default=False,
                        dest='verbose',
                        help='explain what we are doing')
    parser.add_argument('test_yaml_file',
                        metavar='your_test_file.yaml',
                        help='YAML file that defines our tests')
    options = parser.parse_args(prog_args[1:])

    try:
        yaml_config = slapaclsuite.ingest_yaml_file(options.test_yaml_file)
    except Exception as fileread_err:  # pylint: disable=broad-except
        print(fileread_err, file=sys.stderr)
        return False
    config_objects = slapaclsuite.validate_input(yaml_config, verbose=options.verbose)
    commands = slapaclsuite.generate_commands(config_objects)
    slapaclsuite.run_tests(commands, verbose=options.verbose, noop=options.noop)
    return True


if __name__ == '__main__':  # pragma: no cover
    if main():
        sys.exit(0)
    sys.exit(1)
