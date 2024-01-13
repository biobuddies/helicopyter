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
### Begin as you mean to go on (people edition)
Choose default values that will work, out-of-the-box, for most people, most of the time. Even if the machines outnumber the people, reconfiguring the development systems of people is probably harder than reconfiguring many hosted production and pre-production machines (pets versus cattle).

### Make use of tooling
Allow the jump-to-definition features of editors to find the good default values you have chosen.

### 'off' sentinel value
For loosely coupled systems, support a sentinel value of 'off', such as `CODENAME_OTHER_SERVICE_URL=off`. (Are there similar existing conventions? If not perhaps there's an opportunity to register the off URI schema with the IANA.) 

### Assign unique port numbers
This allows multiple codenames to run concurrently on a developer laptop.

## See Also
* https://12factor.net/
* https://peps.python.org/pep-0008/
