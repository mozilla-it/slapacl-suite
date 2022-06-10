'''
    This function validates 'all' sections of the YAML.  Currently that's
    - administrative
    - scripting
    - tests
    This is just so we don't get too dense in any one file.
'''
import sys
from .administrative import AdministrativeSectionValidator
from .scripting import ScriptingSectionValidator
from .tests import TestsSectionValidator


def validate_input(config_in, verbose=False):
    '''
        Given a config structure, validate that it is in good enough shape for us to run against.
    '''

    if not isinstance(config_in, dict):
        raise ValueError(f'validation structure must be a dict.')

    config_out = {}

    validators = {
        'administrative': AdministrativeSectionValidator(),
        'scripting': ScriptingSectionValidator(),
        'tests': TestsSectionValidator(),
    }

    try:
        for section_name, validator in validators.items():
            validation_kwargs = {'verbose': verbose}
            if section_name == 'tests':
                validation_kwargs['admin_object'] = config_out['administrative']
            if validator.validate(config_in.get(section_name), **validation_kwargs):
                config_out[section_name] = validator
            else:
                raise ValueError(f'Unexpected validation return in {section_name}')

    except ValueError as validation_err:
        print(validation_err, file=sys.stderr)
        sys.exit(1)

    return config_out
