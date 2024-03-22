## Formatting
### Indent by four spaces
This aligns with PEP-8. Consistent indentation across file types makes editor configuration easier.

### Wrap lines around 100 characters
A maximized iterm2 window on a 13" 2020 MacBook Pro with the default font is 203 characters wide.
A maximized gnome-terminal window on a ThinkPad X1 Carbon Gen 9 running Ubuntu 20.04 with the default font is also 203 characters wide.
Using 100 characters allows two side-by-side files to be displayed with tmux, etc.

### Prefer single quotes
This reduces visual noise. Black made the wrong choice; double-quote-fixer can help.

## Settings
### Standard environment variables
- `cona`: Unique COdeNAme (or plain language name, but the good ones tend to get used up) to tell deployments apart. Must be set at build time and run time. Should match one main git repository. Should be baked into container images. Not called CODE because that would have a lot of search hits.
- `envi`: ENVIronment to tell pre-production environments from `prod`. Must be set at run time. Should be set to `prod` if there's only one. Not called ENV to avoid colliding with the `env` shell command. Should not be baked into container images.
- `gash`: `git describe --abbrev=40 --always --dirty --match=-`. So people can see what version of code is used. Must be set at build time and run time. Should be baked into container images. Not called HASH to avoid colliding with the Python built-in function and to clarify that this is the Git hash, not the Docker image hash.
- `role`: `web` is a good choice for web servers. Must be set at run time. Different executables should get different `role` values. Not called EXEC for executable to avoid colliding with the shell built-in. Should not be baked into container images.
- `tabr`: TAg or BRanch `git describe --all --exact-match`. Must be set at run time in `prod`. May be unset or null when running in pre-production, especially `local` development. Should not be baked into a container images. Use this to name preview environments and present nice version numbers to users.

### Begin as you mean to go on (people edition)
Choose default values that will work, out-of-the-box, for most people, most of the time. Even if the machines outnumber the people, reconfiguring the development systems of people is probably harder than reconfiguring many hosted production and pre-production machines (pets versus cattle).

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

## See Also
* https://12factor.net/
* https://peps.python.org/pep-0008/
