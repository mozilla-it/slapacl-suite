'''
    Adjustments to allow the tests to be run against the local module
'''
import os
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
