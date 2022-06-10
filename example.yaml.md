# slapaclsuite
slapaclsuite is a scripting framework to turn a YAML file into a suite of tests against slapacl(8), the openldap utility that checks if certain parts of your LDAP tree can be accessed (or not) in a given situation.

slapacl itself is very human oriented, and it's often hard to realize if a change in one part of your LDAP ACLs will affect something else, so this exists to let you build as robust of a test suite as your install requires, and be able to verify in staging that a change has the desired impact.

## The YAML
There is an `example.yaml` file included, which we'll walk through here

### The `administrative` section
The `name` field is in case you have multiple test suites and want to describe what this suite is.
There is also a pair of optional fields, `DN_substitutions_key` and `DN_substitutions`.  This exists so that you can do substitutions of DNs in your tests with placeholder names.  For example:

```yaml
administrative:
  DN_substitutions_key: 'SUB:'
  DN_substitutions:
    sysadmin: 'uid=jdoe,ou=logins,dc=example'
tests:
  - description: 'sysadmins may edit passwords'
    requestDN: 'SUB:sysadmin'
    requestattr: 'userPassword/manage'
    expects: 'ALLOWED'
```
You may know that jdoe is a privileged user, but it's not obvious to an outsider, and this also makes it easier to edit later when jdoe switches roles.

### The `scripting` section
The `executable` field defines which binary to execute, and the `path` field is a list of shell `$PATH` entries to use.  You can pick whatever style works with your security posture:

```yaml
scripting:
  executable: /usr/bin/slapacl
  # path not provided, default to an empty PATH
```
or
```yaml
scripting:
  executable: slapacl
  path:
  - /usr/local/bin
  - /usr/bin
```

### The `tests` section
`tests` is a list containing structural elements for each possible test you want to run:

* Each test SHOULD have a `description` string.  It's not required, but when you have many tests, you'll want this.
* `authcDN` is the DN of the requestor.  This can be:
  * a DN string `uid=someone,ou=logins,dc=example`
  * a substitution string.  So if `administrative` / `DN_substitutions_key` is `SUBST` then you can use `SUBSTsysadmin` to substitute in whatever DN is defined by `sysadmin` in `administrative` / `DN_substitutions`.
  * nothing, if you wish to test an anonymous bind.
* `requestDN` is the DN of the thing you wish to test.  This can be a DN string or a substitution string in the same manner as `authcDN`, but is a mandatory field, since it is the thing you're inspecting.
* `requestattr` is either a single string or a list of strings.  The strings are of the form `attr[/access][:value]`. `slapacl(8)` has more details.  This field is mandatory in `slapaclsuite`.  `slapacl` makes it optional and defaults to `entry`.  That isn't a very interesting check and as such `slapaclsuite` requires you to define what attributes you wish to test.
* `peername` is either a single string or a list of strings.  The strings are IPs that the client is able to connect from.  This lets you verify things like "server A can do a thing, but server B can't".  This field is optional.  If you have a list of `N` IPs, the same test will be run `N` times, once for each IP.
* `ssf` is an optional integer field for the Security Strength Factor - how secure is your connection.  If missing then the default of 0 implies "this can run on any connection", if present, "your SASL must be of this strength."  Consult the man page for `slapd.access(5)` for details.
* `fetchentry` is an optional boolean.  Its default is `true`, meaning that your `requestDN` must exist in order to be tested.  It's possible to set `fetchentry` to `false` and test against an LDAP entry that doesn't exist.  This is not a well-used path in `slapacl` and I found it to be segfault levels of busted in `slapacl` itself.  If you use this, be careful and be ready for disappointment.
* `expects` is a string that must be either `ALLOWED` or `DENIED`, and expresses whether you want the test to allow or deny access to the attributes in the given test.  You must specify this field.
