'''
    This export set covers the basic flow of a run.
    ingest_yaml_file  - read in the test cases
    validate_input    - validate the user-defined test cases are good, and slightly massage them
                        into a form where they will be consistent.
    generate_commands - make the commands that we will run.
    run_tests         - run those commands.
'''
from .readfile import ingest_yaml_file
from .yaml_input_validator import validate_input
from .commands import generate_commands, run_tests

__all__ = ['ingest_yaml_file', 'validate_input', 'generate_commands', 'run_tests']
