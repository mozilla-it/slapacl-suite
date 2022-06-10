'''

    Module to take -validated- homogenized inputs (i.e. a massaged YAML) and give back
    commands that will be run.

'''
import copy
import re
# import shlex
import subprocess


def generate_commands(config):
    '''
        Input: config hash consisting of
               { 'administrative': currently-unused administrative object,
                 'scripting':      scripting object,
                 'tests':          tests object, }

        Returns: list of tuples.
                 Each tuple is ("printable description", hash)
                 Each hash consists of
                 { 'script':  array-of-strings suitable for subprocess to run,
                   'path':    PATH to use to find the script above,
                   'expects': "ALLOWED" or "DENIED" - what we expect from the test. }

        This creates a list of the inputs needed for run_tests below:
        what we're going to run, and what we expect back from each test.
    '''
    scripting_config = config['scripting'].render()
    tests_config = config['tests'].render()

    base_script = [scripting_config['executable']]
    base_script.extend(scripting_config['default_arguments'])
    path = scripting_config['path']

    retval = list()
    for entry in tests_config:

        for peername_tuple in entry['peername']:
            (peername_label, peername_value) = peername_tuple
            for requestattr_tuple in entry['requestattr']:
                (requestattr_label, requestattr_value) = requestattr_tuple

                output_description = \
                    f'{entry["description"]} {requestattr_label} {peername_label}'

                script = copy.copy(base_script)
                for item in ['authcDN', 'fetchentry', 'requestDN', 'ssf']:
                    script.extend(entry[item])

                script.extend(peername_value)
                script.extend(requestattr_value)

                retval.append((output_description, {
                    'script': script,
                    'path': path,
                    'expects': entry['expects'],
                    }))

    return retval


def run_tests(commands, verbose=False, noop=False):
    '''
        Input:   list of commands above
        Returns: nothing

        This function accepts the command structure from `generate_commands`
        above, then iterates over them, running the command and checking the
        result for 'did the test do what we expect'

        Prints results to stdout for human interpretation.
        I did consider making a structured return that was then parsed into
        human text, but I couldn't then imagine a suitable use case to make
        it worth the design.  Feel free to adapt this if that changes.
    '''
    for tuple_entry in commands:
        (description, entry) = tuple_entry
        script = entry['script']
        expects = entry['expects']
        path = ':'.join(entry['path'])
        # use this in py3.8:
        # printable_command = shlex.join(script)
        printable_command = ' '.join(script)
        if noop:
            print(f'# {description}')
            print(printable_command)
            print(f'# expects: {expects}')
            print('')
            continue

        try:
            # Oddly enough, the answers from slapacl are on stderr.
            result = subprocess.run(script, env={'PATH': path},
                                    check=True,
                                    stdout=None,
                                    stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            print(f'# {description}')
            print('Execution error when running:')
            print(printable_command)
            continue
        match = re.search(b' (ALLOWED|DENIED)$', result.stderr, re.MULTILINE)
        if not match:
            # Maybe the format changed.  Probably coding work needed.
            print(f'# {description}')
            print('Unable to determine answer from `slapacl`:')
            print(printable_command)
            print(result.stderr.decode('utf-8'))
            continue
        result = match.group(1).decode('utf-8')
        if result == expects:
            if verbose:
                print(f'PASS # {description}')
        else:
            print(f'FAIL # {description}')
            print(printable_command)
            print(f'# expected "{expects}", but got "{result}"')
