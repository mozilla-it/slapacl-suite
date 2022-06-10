'''
    Read a file and return its YAML contents as pythonic data.
'''
import os
import yaml


def ingest_yaml_file(filename):
    '''
        Given a filename, read in the file and return the YAML contents.
        Inputs: str    filename of a YAML-containing file to read
        Return: dict   parsed contents of the file

        Raise: IOError on failed file reads, yaml.YAMLError on parse failures
    '''
    full_path = os.path.abspath(os.path.expanduser(filename))
    with open(full_path, 'r') as input_fh:
        file_contents = input_fh.read()
    yaml_contents = yaml.safe_load(file_contents)

    return yaml_contents
