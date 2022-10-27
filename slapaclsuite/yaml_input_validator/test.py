'''

    the validator of a test section of the YAML input structure.

'''
import sys


class TestValidator:
    ''' class that validates the test pieces in the 'tests' section of the YAML config '''
    section = 'test'

    def _field_name(self):
        ''' What field does the calling function seek to validate? '''
        calling_func_str = sys._getframe(1).f_code.co_name  # pylint: disable=protected-access
        return self.validating_functions[calling_func_str]

    def _validate_expects(self, value_in, verbose=False, **_kwargs):
        '''
            Validate whether the test expects to be allowed or denied by slapacl
            Inputs: String+
            Returns: String+
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if value_in is None:
            # Undeterminable if this was an explicit null or a default null from being not
            # specified, but we assume the latter.
            raise ValueError(f'"{my_field}" must be present on all tests.')
        if value_in not in ['ALLOWED', 'DENIED']:
            raise ValueError(f'"{my_field}" must be a string of "ALLOWED" or "DENIED".')
        value_out = value_in
        return value_out

    def _validate_requestdn(self, value_in, admin_object=None, verbose=False):
        '''
            Validate the DN of the entry that will be queried by the test.
            Inputs: String+
            Returns: String+
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if value_in is None:
            # Undeterminable if this was an explicit null or a default null from being not
            # specified, but we assume the latter.
            raise ValueError(f'"{my_field}" must be present on all tests.')
        if not isinstance(value_in, str):
            raise ValueError(f'"{my_field}" must be a string.')
        if not value_in:
            raise ValueError(f'"{my_field}" can not be an empty string.')
        if admin_object is not None:
            value_out = admin_object.possible_dn_substitutions(value_in)
        else:
            value_out = value_in
        return value_out

    def _validate_authcdn(self, value_in, admin_object=None, verbose=False):
        '''
            Validate the DN that will do the querying
            Inputs: None or String+
            Returns: None or String+
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if value_in is None:
            # 'None' is fine, it symbolizes that the connection is anonymous.
            return None
        if not isinstance(value_in, str):
            raise ValueError(f'"{my_field}" must be null or a string.')
        if not value_in:
            raise ValueError(f'"{my_field}" can not be an empty string.')
        if admin_object is not None:
            value_out = admin_object.possible_dn_substitutions(value_in)
        else:
            value_out = value_in
        return value_out

    def _validate_requestattr(self, value_in, verbose=False, **_kwargs):
        '''
            Validate the attributes that will be evaluated
            Inputs: String+ or [String+]+
            Returns: [String+]+
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if value_in is None:
            # 'None' is not okay.  In slapacl it symbolizes to use the 'entry' pseudo-attribute
            # However, we require it to be explicit in the yaml.
            raise ValueError(f'"{my_field}" in a test must be specified.')
        if isinstance(value_in, str):
            if value_in:
                value_out = [value_in]
            else:
                raise ValueError(f'"{my_field}" can not be an empty string.')
        elif isinstance(value_in, list):
            if not value_in:
                raise ValueError(f'"{my_field}" in a test can not be empty.')
            for item in value_in:
                if not isinstance(item, str):
                    raise ValueError(f'"{my_field}" in a test must be a string.')
                if not item:
                    raise ValueError(f'"{my_field}" can not be an empty string.')
            value_out = value_in
        else:
            raise ValueError(f'"{my_field}" in a test must be a string or list of strings.')
        return value_out

    def _validate_fetchentry(self, value_in, verbose=False, **_kwargs):
        '''
            Validate whether the requestDN is real (true/default) or simulated (explicit false)
            Inputs: None or Bool
            Returns: Bool
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if value_in is None:
            # 'None' is fine, it symbolizes that the requestDN is accurate
            # We add it to the output to make sure it's explicit, not implicit.
            value_out = True
        elif not isinstance(value_in, bool):
            raise ValueError(f'"{my_field}" in a test must be a boolean.')
        else:
            value_out = value_in
        return value_out

    def _validate_ssf(self, value_in, verbose=False, **_kwargs):
        '''
            Validate the ssf setting
            Inputs: None or Integer
            Returns: None or Integer
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if value_in is None:
            # 'None' is fine, it symbolizes that we are not checking security levels
            value_out = None
        elif not isinstance(value_in, int):
            raise ValueError(f'"{my_field}" in a test must be an integer.')
        elif value_in < 0:
            raise ValueError(f'"{my_field}" in a test must be 0 or greater.')
        else:
            value_out = value_in
        return value_out

    def _validate_peername(self, value_in, admin_object=None, verbose=False):
        '''
            Validate the peername that we will simulate as 'the query came from'
            Inputs: None or String+ or [String+]+
            Returns: None or [String+]+
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if value_in is None:
            # 'None' is fine, it symbolizes that we don't care what IP is here.
            # We add it to the output to make sure it's explicit, not implicit.
            value_out = None
        elif isinstance(value_in, str):
            if value_in:
                if admin_object is not None:
                    value_out = [admin_object.possible_peername_substitutions(value_in)]
                else:
                    value_out = [value_in]
            else:
                raise ValueError(f'"{my_field}" can not be an empty string.')
        elif isinstance(value_in, list):
            if not value_in:
                raise ValueError(f'"{my_field}" should not be an empty list.')
            value_out = []
            for item in value_in:
                if not isinstance(item, str):
                    raise ValueError(f'"{my_field}" in a test must be a string.')
                if not item:
                    raise ValueError(f'"{my_field}" can not be an empty string.')
                if admin_object is not None:
                    value_out.append(admin_object.possible_peername_substitutions(item))
                else:
                    value_out.append(item)
        else:
            raise ValueError(f'"{my_field}" in a test must be a string or list of strings.')
        return value_out

    def _validate_description(self, value_in, verbose=False, **_kwargs):
        '''
            Validate the description field of a test
            Inputs: None or String*
            Returns: String*
        '''
        my_field = self._field_name()
        where_am_i = f'{self.section} / {my_field}'
        if verbose:
            print(f'## Preflighting {where_am_i}.')
        if value_in is None:
            # Let's cook up a description so there is one.
            value_out = 'undescribed test'
        elif not isinstance(value_in, str):
            raise ValueError(f'"{my_field}" must be a string.')
        else:
            value_out = value_in
        return value_out

    def __init__(self):
        '''
            build a dict of functions (above) that will validate pieces of the config
        '''
        self.validating_functions = {
            '_validate_expects': 'expects',
            '_validate_requestdn': 'requestDN',
            '_validate_authcdn': 'authcDN',
            '_validate_requestattr': 'requestattr',
            '_validate_fetchentry': 'fetchentry',
            '_validate_ssf': 'ssf',
            '_validate_peername': 'peername',
            '_validate_description': 'description',
        }
        self.inputs = None

    def validate(self, config_in, admin_object=None, verbose=False):
        '''
            Given a test config structure,
            validate that it is in good enough shape for us to run against.
            Inputs: None or dict
            Returns: True
        '''
        if verbose:
            print(f'# Preflighting {self.section}.')

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
            config_out[section_name] = call_func(config_in.get(section_name),
                                                 admin_object=admin_object)

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

        config_out['description'] = self.inputs['description']
        config_out['expects'] = self.inputs['expects']
        config_out['requestDN'] = ['-b', self.inputs['requestDN']]
        if self.inputs['authcDN'] is None:
            config_out['authcDN'] = []
        else:
            config_out['authcDN'] = ['-D', self.inputs['authcDN']]
        config_out['requestattr'] = [(x, [x]) for x in self.inputs['requestattr']]
        if self.inputs['fetchentry']:
            config_out['fetchentry'] = []
        else:
            config_out['fetchentry'] = ['-u']
        if self.inputs['ssf'] is None:
            config_out['ssf'] = []
        else:
            config_out['ssf'] = ['-o', f'ssf={self.inputs["ssf"]}']
        if self.inputs['peername'] is None:
            config_out['peername'] = [('any-IP', [])]
        else:
            config_out['peername'] = [(x, ['-o', f'peername=IP={x}'])
                                      for x in self.inputs['peername']]

        return config_out
