'''
    This library is for us to validate all the things that should appear in
    the YAML that we use to define tests.  While there may be a way to do
    this with some imported library, I think this is just edge-case enough
    to make our own.
'''
from .all import validate_input

__all__ = ['validate_input']
