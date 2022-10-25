# slapaclsuite
slapaclsuite is a scripting framework to turn a YAML file into a suite of tests against slapacl(8), the openldap utility that checks if certain parts of your LDAP tree can be accessed (or not) in a given situation.

slapacl itself is very human oriented, and it's often hard to realize if a change in one part of your LDAP ACLs will affect something else, so this exists to let you build as robust of a test suite as your install requires, and be able to verify in staging that a change has the desired impact.

## The YAML
There is an `example.yaml` file included, and there are [docs for its structure](example.yaml.md "example.yaml docs").

## The script
`setup.py` will build a `slapaclsuite` executable.

`usage: slapaclsuite [-h] [--noop] [-v] your_test_file.yaml`

The script will preflight the YAML file for validity, and then run the tests.  `--noop` will print the commands rather than run them.
