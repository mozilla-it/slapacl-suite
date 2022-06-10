'''

    the validator of the scripting section of the YAML input structure.

'''
import sys
import re


class ScriptingSectionValidator:
    ''' class that validates the 'scripting' section of the YAML config '''
    section = 'scripting'

    def _field_name(self):
        ''' What field does the calling function seek to validate? '''
        calling_func_str = sys._getframe(1).f_code.co_name  # pylint: disable=protected-access
        return self.validating_functions[calling_func_str]

    def _validate_executable(self, value_in, verbose=False):
        '''
            Validate the executable string
            Inputs: None or String+
            Prints a complaint if None
            Returns: String+
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if not value_in:
            value_out = 'slapacl'
            print(f'Defaulting to using "{value_out}" as the {my_field}')
            print(f'Suppress this warning by defining "{where_am_i}"')
        elif not isinstance(value_in, str):
            raise ValueError(f'{where_am_i} must be a string.')
        else:
            value_out = value_in
        return value_out

    def _validate_path(self, value_in, verbose=False):
        '''
            Validate the path specifier
            Inputs: None or [String+]*
            Returns: [String+]*
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if value_in is None:
            value_out = []
        elif not isinstance(value_in, list):
            raise ValueError(f'{where_am_i} must be a list.')
        else:
            for item in value_in:
                if not isinstance(item, str) or not re.match(r'^/(?:[^\/\0]+\/*)*$', item):
                    raise ValueError(f'{where_am_i} "{item}" must be a path element.')
            value_out = value_in
        return value_out

    def _validate_default_arguments(self, value_in, verbose=False):
        '''
            Validate the path specifier
            Inputs: None or [String+]*
            Returns: [String+]*
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if value_in is None:
            value_out = []
        elif not isinstance(value_in, list):
            raise ValueError(f'{where_am_i} must be a list.')
        else:
            for item in value_in:
                if not isinstance(item, str):
                    raise ValueError(f'{where_am_i} "{item}" must be a string.')
                if not item:
                    raise ValueError(f'{where_am_i} "{item}" can not be an empty string.')
            value_out = value_in
        return value_out

    def __init__(self):
        '''
            build a dict of functions (above) that will validate pieces of the config
        '''
        self.validating_functions = {
            '_validate_executable': 'executable',
            '_validate_path': 'path',
            '_validate_default_arguments': 'default_arguments',
        }
        self.inputs = None

    def validate(self, config_in, verbose=False):
        '''
            Given a scripting config structure,
            validate that it is in good enough shape for us to run against.
            Inputs: None or dict
            Returns: True
        '''
        if verbose:
            print(f'# Preflighting "{self.section}" section.')

        if config_in is None:
            config_in = {}
        if not isinstance(config_in, dict):
            raise ValueError(f'{self.section} section must be a dict.')

        input_sections = set(config_in.keys())
        allowable_sections = set(self.validating_functions.values())
        disallowed_sections = input_sections - allowable_sections
        if disallowed_sections:
            raise ValueError(f'{self.section} contains unexpected fields {disallowed_sections}')

        config_out = {}

        for funcname_str, section_name in self.validating_functions.items():
            try:
                call_func = getattr(self, funcname_str)
            except AttributeError as exc_getattr:
                raise ValueError from exc_getattr
            config_out[section_name] = call_func(config_in.get(section_name))

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

        config_out = {}

        config_out['executable'] = self.inputs['executable']
        config_out['path'] = self.inputs['path']
        config_out['default_arguments'] = self.inputs['default_arguments']

        return config_out
