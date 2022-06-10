'''

    the validator of a test section of the YAML input structure.
    We only have validate/render since we are a list holder.
    Note that we are also 'odd' in that our .inputs is a list of instance objects
    instead of dict

'''
from .test import TestValidator


class TestsSectionValidator:
    ''' class that validates the 'tests' section of the YAML config '''
    section = 'tests'

    def __init__(self):
        '''
            Parameter to capture the validated input
        '''
        self.inputs = None

    def validate(self, config_in, admin_object=None, verbose=False):
        '''
            Given a tests config structure,
            validate that it is in good enough shape for us to run against.
            Inputs: None or [dict]*
            Prints a complaint if None or []
            Returns: True
        '''
        if verbose:
            print(f'# Preflighting {self.section}.')

        if config_in is None or config_in == []:
            print('No tests defined.  You almost certainly have a poor yaml defined.')
            print('Suppress this warning by defining a \'tests\' section.')
            return []
        if not isinstance(config_in, list):
            raise ValueError(f'{self.section} section must be a list.')

        config_out = []

        for test_in in config_in:

            if not isinstance(test_in, dict):
                raise ValueError(f'Test {test_in} is not a k/v test.  Check example.yaml')

            tester = TestValidator()
            tester.validate(test_in, admin_object=admin_object, verbose=verbose)
            config_out.append(tester)

        self.inputs = config_out
        return True

    def render(self, verbose=False):
        '''
            Returns a structure useable by the methods that will build the runtime commands.
            Presumes/requires that valid input has been sent in already.
            Inputs: None
            Returns: dict
        '''
        if verbose:
            print(f'# Rendering {self.section}.')

        if self.inputs is None:
            raise RuntimeError(f'Can not render unvalidated {self.section} instance')

        config_out = []

        for test_in in self.inputs:
            config_out.append(test_in.render(verbose=verbose))

        return config_out
