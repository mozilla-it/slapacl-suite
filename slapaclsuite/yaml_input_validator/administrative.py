'''

    the validator of the administrative section of the YAML input structure.

'''
import sys
import re


class AdministrativeSectionValidator:
    ''' class that validates the 'administrative' section of the YAML config '''
    section = 'administrative'

    def _field_name(self):
        ''' What field does the calling function seek to validate? '''
        calling_func_str = sys._getframe(1).f_code.co_name  # pylint: disable=protected-access
        return self.validating_functions[calling_func_str]

    def _validate_name(self, value_in, verbose=False):
        '''
            Validate the name of the test suite
            Inputs: None or String*
            Returns: String+
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if not value_in:
            value_out = 'default-test-suite'
        elif not isinstance(value_in, str):
            raise ValueError(f'{where_am_i} must be a string.')
        else:
            value_out = value_in
        return value_out

    def _validate_dn_sub_key(self, value_in, verbose=False):
        '''
            Validate a string for indicating runtime substitutions.
            Inputs: None or String+
            Returns: None or String+
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if value_in is None:
            value_out = None
        elif not isinstance(value_in, str):
            raise ValueError(f'{where_am_i} must be a string.')
        elif not value_in:
            raise ValueError(f'{where_am_i} cannot be an empty string.')
        else:
            value_out = value_in
        return value_out

    def _validate_dn_subs(self, value_in, verbose=False):
        '''
            Validate a dict of available substitutions
            Inputs: None or dict(String+: String+)
            Returns: dict(String+: String+)
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if value_in is None:
            value_out = {}
        elif not isinstance(value_in, dict):
            raise ValueError(f'{where_am_i} must be a dict.')
        else:
            for subk, subv in value_in.items():
                if not isinstance(subk, str) or not subk:
                    raise ValueError(f'{where_am_i} "{subk}" must be a nonempty string.')
                if not isinstance(subv, str) or not subv:
                    raise ValueError(f'{where_am_i} "{subk}" / "{subv}" must be a nonempty string.')
            value_out = value_in
        return value_out

    def __init__(self):
        '''
            build a dict of functions (above) that will validate pieces of the config
        '''
        self.validating_functions = {
            '_validate_name': 'name',
            '_validate_dn_sub_key': 'DN_substitutions_key',
            '_validate_dn_subs': 'DN_substitutions',
        }
        self.inputs = None

    def possible_dn_substitutions(self, string_in):
        '''
            Substitute values from our YAML area so we can use stand-in DNs.
            This lets us know if someone is in a test case because THEY matter, or because
            anyone of a certain class will do.

            Example:
            Inputs: ('MAGIC:b', 'MAGIC:', {'a':'M', 'b':'N'}) -> 'N'
        '''
        if self.inputs is None:
            raise RuntimeError(f'Can not perform DN subs before validation.')

        if not isinstance(string_in, str):
            raise ValueError(f'input-string must be a string')

        subkey = self.inputs['DN_substitutions_key']
        subs = self.inputs['DN_substitutions']

        if not re.match(subkey, string_in):
            # We're never going to match in order to do a substitution...
            # So no sub happens: return the original.
            return string_in

        possible_key = string_in.replace(subkey, '')
        possible_value = subs.get(possible_key)
        if possible_value is None:
            return string_in
        return possible_value

    def validate(self, config_in, verbose=False):
        '''
            Given an administrative config structure,
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

        config_out['name'] = self.inputs['name']
        config_out['DN_substitutions_key'] = self.inputs['DN_substitutions_key']
        config_out['DN_substitutions'] = self.inputs['DN_substitutions']

        return config_out
