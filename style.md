## As simple as possible
* Choose good words; differentiate when necessary
    - Verbs over nouns
    - Simple and common over fancy and rare
    - Avoid substring matches
    - Prefer whole words to abbreviations
* Three strikes and you refactor
    - Copy/paste once is okay, preferably with a comment on the duplicatation
    - Three examples should ease choosing the right abstraction
    - Avoid overshooting on the journey from specific to generic

Inspired by https://blog.cleancoder.com/uncle-bob/2013/05/27/TheTransformationPriorityPremise.html
1. No operation: `pass`
2. Unconditionally executed code
3. If
4. While

1. Literal
2. Variable
3. Function

1. Scalar: bool, float, int, str
2. Vector: list, set, tuple
3. Multidimensional: dict, Counter

## Three strikes and you automate (manual, barely codified, mostly codified)
1. Processes should usually begin as manual steps
2. When some repetition is necessary, take a first pass at code/automation
    * The low hanging fruit steps which are trivial to codify/automate
    * The most tedious or annoying steps
    * The most error-prone steps
    * Only 1% to 33% of the steps should be codified/automated at this point
3. When continued repetition is evident, take a second pass at code/automation
    * Prioritize steps similarly
    * Leave 10% or more of the steps as manual
        - "Done is better than perfect."
        - "The perfect is the enemey of the good."
4. Monitor and make "continuous" improvements
5. Instigate fire drills of rare "black swan" events

## Version control, manual review, automated checks
Use version control, code review, and automated tests/checks for most changes. Exceptions to consider:

* URLs and other environment variables https://12factor.net/config
* Some deploys/$cona/terraform/main.tf.json files are omitted from this public repository because of
  account-specific values. Checking in generated JSON into internal repositories is recommended.
  Doing so keeps the files ready for commands like `terraform plan` and `terraform apply` and allows
  `git bisect` to help solve JSON level issues (hopefully rare).

## Formatting
### Dates
Following ISO 8601/[RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339), join the following fields with a dash `-`:
1. Four-digit, zero-padded year, starting from 0
2. Two-digit, zero-padded month, starting from 1
3. Two-digit, zero-padded day, starting from 1

Appending the timezone abbreviation after a space ` ` is recommended. Prefer `Z` to `UTC`, because of the popularity 

```shell
$ date +%Y-%m-%d\ %Z | sed s/UTC/Z/
2024-04-19 EDT
$ date -u +%Y-%m-%d\ %Z | sed s/UTC/Z/
2024-04-19 Z
```

## Code
### Indent by four spaces
This aligns with PEP-8. Consistent indentation across file types makes editor configuration easier.

### Wrap lines around 100 characters
A maximized iterm2 window on a 13" 2020 MacBook Pro with the default font is 203 characters wide.
A maximized gnome-terminal window on a ThinkPad X1 Carbon Gen 9 running Ubuntu 20.04 with the default font is also 203 characters wide.
Using 100 characters allows two side-by-side files to be displayed with tmux, etc.

### Prefer single quotes
Double quotes are visually noisier than single quotes. Black made the wrong choice; double-quote-fixer from pre-commit or `ruff format` can help.

## Settings
### Standard environment variables
* `cona`: Unique COdeNAme (or plain language name, but the good ones tend to get used up) to tell deployments apart. Must be set at build time and run time. Should match one main git repository. Should be baked into container images. Not called CODE because that would have a lot of search hits.
* `envi`: ENVIronment to tell pre-production environments from `prod`. Must be set at run time. Should be set to `prod` if there's only one. Not called ENV to avoid colliding with the `env` shell command. Should not be baked into container images.
* `gash`: `git describe --abbrev=40 --always --dirty --match=-`. So people can see what version of code is used. Must be set at build time and run time. Should be baked into container images. Not called HASH to avoid colliding with the Python built-in function and to clarify that this is the Git hash, not the Docker image hash.
* `role`: `web` is a good choice for web servers. Must be set at run time. Different executables should get different `role` values. Not called EXEC for executable to avoid colliding with the shell built-in. Should not be baked into container images.
* `tabr`: TAg or BRanch `git describe --all --exact-match`. Must be set at run time in `prod`. May be unset or null when running in pre-production, especially `local` development. Should not be baked into a container images. Use this to name preview environments and present nice version numbers to users.

### Begin as you mean to go on (people edition)
Choose default values that will work, out-of-the-box, for most people, most of the time. Even if the machines outnumber the people, reconfiguring the development systems of people is probably harder than reconfiguring many hosted production and pre-production machines (pets versus cattle).

### Single static assignment
Try not to mutate variables, except in obvious ways like appending an element to a list for each iteration of a for loop.
Prefer multiple, specific variable names over a general variable name with shifting values.

### Single static assignment
Try not to mutate variables, except in obvious ways like appending an element to a list for each iteration of a for loop.
Prefer multiple, specific variable names over a general variable name with shifting values.

### Make use of tooling
Allow the jump-to-definition features of editors to find the good default values you have chosen.

### 'off' sentinel value
For loosely coupled systems, support a sentinel value of 'off', such as `CODENAME_OTHER_SERVICE_URL=off`. (Are there similar existing conventions? If not perhaps there's an opportunity to register the off URI schema with the IANA.) 

### Assign unique port numbers
This allows multiple codenames to run concurrently, such as in the `local` developer laptop environment. For easy debugging, use the unique port number as much as possible. For a webserver, this probably means using it both inside and outside the container, only proxying from/to 443 at the TLS-terminating load balancer.

### Clearly differentiate between Internet and Intranet
Allow people to tell at a glance whether a system is supposed to be Internet-accessible by its DNS domain or subdomain.

This can be blended with additional subdomain organizational approaches such as:
* Physical location like `.rdu` for Raleigh-DUrham and `.sfo` for San FranciscO
* Type of IP address like `.ten` for the 10.x.y.z class A private range or `.c` for the 192.168.x.y class C private range

### Only cancel, never delete
In operational data systems, do not delete. Set a status field to `canceled` instead. To avoid unchecked growth, graduating data from availability through operational systems to availability through warehouse/archive systems seems reasonable, following steps such as:
1. Expand (copy)
2. Check correctness and completeness
3. Contract (delete)

### Avoid State Secrets
1. Collaborators (many) should be able to (re)view Infrastructure-as-Code (IaC) files.
2. Using individual credentials, Developers (many) should be able to `terraform apply` to
   pre-production and `terraform plan` for production, with or without local changes. Specific
   `terraform apply` to production may also be appropriate, like to deploy/rollback container
   images built from properly reviewed code.
3. Using individual credentials, Automation and Administrators (few) should be able to `terraform apply` to production.

First, writing usernames and passwords into IaC or state files breaks the individual credentials pattern. Second, allowing secrets into state files means you can't use access controls appropriate for code any more, but must instead apply password manager level access controls. Remember, the target is Infrastructure-as-Code, not Infrastructure-as-a-Password-Manager.

1. Supply provider credentials via environment variables.
2. Unless they're encrypted like aws_iam_user passwords, set passwords in resources to a placeholder
   value like `SEE-PASSWORD-MANAGER` and configure lifecycle ignore.
3. Check git and state files to ensure secrets have not leaked into them.

TODO patch OpenTofu to help with this. TODO find or develop a good approach to 1. securely storing secrets from newly created resources, like `cloudflare_access_service_token`, and 2. rotating secrets.

## See Also
* https://12factor.net/
* https://peps.python.org/pep-0008/
