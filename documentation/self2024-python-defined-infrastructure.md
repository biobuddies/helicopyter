# Python Defined Infrastructure

## Simplicity

* Low distance between definition and usage (jump-to reduces)
* The right abstractions (declarative? imperative?)
* Ahead-of-time (build-time) is generally preferred but certain decisions must be just-in-time (run-time)

## Hashicorp Configuration Language (HCL) for Terraform

> [Hashicorp Configuration Language (HCL)] is a rich language designed to be relatively easy for
> humans to read and write. The constructs in the Terraform language can also be expressed in JSON
> syntax, which is harder for humans to read and edit but easier to generate and parse
> programmatically.

> ~~[Hashicorp Configuration Language (HCL)] is~~ a ~~rich~~ [good] language ~~designed to be~~ [that is] relatively easy for
> humans to read and write. ~~The constructs in the Terraform language can also be expressed in JSON~~
> ~~syntax, which is harder for humans to read and edit but easier to generate and parse~~
> ~~programmatically.~~

## YAML for Ansible

> Ansible is a radically simple IT automation platform that makes your applications and systems
> easier to deploy and maintain. Automate everything from code deployment to network configuration to
> cloud management, in a language that approaches plain English, using SSH, with no agents to install
> on remote systems.

> ~~Ansible is a radically~~ simple ~~IT~~ automation ~~platform~~ that makes your applications and systems
> easier to deploy and maintain. Automate [many] ~~every~~thing[s] from code deployment to network configuration to
> cloud management, in a [good] language ~~that approaches plain English, using SSH, with no agents to install~~
> ~~on remote systems~~.

## Python
People are likely to already know Python (positive past experience)

If someone learns Python, they will likely find opportunities to re-apply and
extend their knowledge (positive future experience)

I have learned and used several languages. I like Python.

## TerraformPy: 2016 -> 2021
> Terraform is an amazing tool. Like, really amazing. When working with code that is managing third-party service definitions, and actually applying changes to those definitions by invoking APIs, a high-degree of confidence in the change process is a must-have, and that's where Terraform excels. The work flow it empowers allow teams to quickly make changes across a large (and ever growing) footprint in multiple providers/regions/technologies/etc.
>
> But as your definitions grow the HCL syntax very quickly leaves a lot to be desired, and is it ever verbose... So many definitions of variables and outputs need to be repeated, over and over, as you compose more modules that use each other.

https://github.com/NerdWalletOSS/terraformpy

## CDKTF: 2020 -> Now
Reuses code from the Amazon Web Services (AWS) Cloud Development Kit (CDK).

https://github.com/hashicorp/terraform-cdk/tree/main?tab=readme-ov-file#cdk-for-terraform

## Helicopyter: 2024 -> Now
Smooths over CDKTF's rough edges.

> ### What Helicopyter does (goals)
> Fix the CDKTF naming mess. Meaningful names make review easy. Terraform's resource prefix style results in meaningful names and aligns with "Namespaces are one honking great idea -- let's do more of those!" The AWS CDK style of suffixing hashes generates difficult-to-review terraform plan output and ignores the existing namespaces.
> Provide a directory structure that groups primarily by "codename" (could be called application, service) and secondarily by tool. For now it assumes f'deploys/{codename}/terraform'.
> ### What Helicopyter will probably never do (non-goals)
> Terraform has a pretty good command line interface. Helicopyter focuses on generating JSON for it. Helicopyter does not try to wrap the terraform command line interface itself and using CDKTF's wrapper is untested and not recommended.

https://github.com/biobuddies/helicopyter

https://github.com/biobuddies/helicopyter/blob/main/deploys/demo/terraform/main.py

https://github.com/biobuddies/helicopyter/blob/main/deploys/allowedflare/terraform/main.py

## Extension Example
* `deploys/people/terraform/main.{py,tf.json}` creates accounts and sets permissions across multiple providers
* `deploys/people/python/crosscheck.py` lists all accounts for each provider and compares to `../terraform/main.py`

## YAML Ain't Markup Language
(&Anchors, *aliases, and `x-prefixes`)[https://medium.com/@kinghuang/docker-compose-anchors-aliases-extensions-a1e4105d70bd] allow simple reuse.

## YAML Tooling
```yaml
- id: dot-yaml
  description: Require four letter suffix http://www.yaml.org/faq.html
  entry: dot-yaml
  files: .*\.yml$
  language: fail
  name: dot-yaml

- id: prettier-write
  entry: node_modules/.bin/prettier --write
  language: system
  name: prettier-write
  types_or:
      - json
      - yaml
      - toml
      - ts

- id: yamllint
  entry: yamllint
  language: system
  name: yamllint
  types:
      - file
      - yaml
```
https://github.com/biobuddies/helicopyter/blob/main/.pre-commit-hooks.yaml

```yaml
extends: default

rules:
    comments:
        min-spaces-from-content: 1 # Unfortunate difference between prettier and black
    document-start: disable
    indentation:
        spaces: 4
    line-length:
        max: 100
    truthy:
        level: error
```
https://github.com/biobuddies/helicopyter/blob/main/.yamllint.yaml

## Jinja Setup
```python
from jinja2.nativetypes import NativeEnvironment

environment = NativeEnvironment()
environment.filters['ord'] = ord
```

## Tidy Jinja: Strip
```python
template="""
[
    {% for well in wells %}
        ({{ well[0] | upper | ord - 'A' | ord }}, {{ well[1:] | int - 1 }}),
    {% endfor %}
]
"""
```

```python
In : template
Out: "\n[\n    {% for well in wells %}\n        ({{ well[0] | upper | ord - 'A' | ord }}, {{ well[1:] | int - 1 }}),\n    {% endfor %}\n]\n"
```

```python
In : template.strip()
Out: "[\n    {% for well in wells %}\n        ({{ well[0] | upper | ord - 'A' | ord }}, {{ well[1:] | int - 1 }}),\n    {% endfor %}\n]"
```

## Tidy Jinja: Dedent
```python
from textwrap import dedent

if True:
    template = """
    [
        {% for well in wells %}
            ({{ (well[0] | ord) - ('A' | ord) }}, {{ (well[1:] | int) - 1 }}),
        {% endfor %}
    ]
    """
```

```python
In : template
Out: "\n    [\n        {% for well in wells %}\n            ({{ (well[0] | ord) - ('A' | ord) }}, {{ (well[1:] | int) - 1 }}),\n        {% endfor %}\n    ]\n    "
```

```python
In : dedent(template).strip()
Out: "[\n    {% for well in wells %}\n        ({{ (well[0] | ord) - ('A' | ord) }}, {{ (well[1:] | int) - 1 }}),\n    {% endfor %}\n]"
```

## Tidy Jinja: Curlies
```python
f_string_style = f"""
{{{{ action.name }}}} ({action_type})
{{% if action.status in ('completed', 'canceled') %}}
Duration (minutes): {{{{ '{{0:.2f}}'.format(action.duration_seconds / 60) }}}}
Completed by: {{{{ action.completed_by.username }}}}
{{% else %}}
Created at: {{{{ action.created }}}}
{{% endif %}}
""".strip()
```

```python
printf_style = dedent(
    """
    {{ action.name }} (%s)
    {%% if action.status in ('completed', 'canceled') %%}
    Duration (minutes): {{ '%%.2f' %% (action.duration_seconds / 60) }}
    Completed by: {{ action.completed_by.username }}
    {%% else %%}
    Created at: {{ action.created }}
    {%% endif %%}
    """ % action_type
).strip()
```

## Tidy Jinja: Curlies and Fragment Reuse
```python
action = Strinja('action')
strinja_style = (
    f'{action.name} ({action_type})\n'
    '{% if action.status in ("completed", "canceled") %}\n'
    f"""Duration (minutes): {Strinja('"%.2f"') % '(action.duration_seconds / 60)'}\n"""
    f'Completed by: {action.completed_by.username}\n'
    '{% else %}\n'
    f'Created at: {action.created}\n'
    '{% endif %}'
)
```

```python
In : print(strinja_style)
{{ action.name }} (User Action)
{% if action.status in ("completed", "canceled") %}
Duration (minutes): {{ "%.2f" % (action.duration_seconds / 60) }}
Completed by: {{ action.completed_by.username }}
{% else %}
Created at: {{ action.created }}
{% endif %}
```

```python
for action in (in_progress, completed):
    results = [
        environment.from_string(template).render(action=action)
        for template in (f_string_style, printf_style, strinja_style)
    ]
    assert results[0] == results[1] == results[2]
```

## Python Ansible Playbook
```diff
diff --git a/lib/ansible/parsing/dataloader.py b/lib/ansible/parsing/dataloader.py
index 17fc534296..fb6312b025 100644
--- a/lib/ansible/parsing/dataloader.py
+++ b/lib/ansible/parsing/dataloader.py
@@ -11,6 +11,8 @@ import re
 import tempfile
 import typing as t
 
+from importlib.util import module_from_spec, spec_from_file_location
+
 from ansible import constants as C
 from ansible.errors import AnsibleFileNotFound, AnsibleParserError
 from ansible.module_utils.basic import is_executable
@@ -79,7 +81,7 @@ class DataLoader:
 
     def load_from_file(self, file_name: str, cache: str = 'all', unsafe: bool = False, json
_only: bool = False) -> t.Any:
         '''
-        Loads data from a file, which can contain either JSON or YAML.
+        Loads data from a file, which can contain JSON, Python, or YAML.
 
         :param file_name: The name of the file to load data from.
         :param cache: Options for caching: none|all|vaulted
@@ -94,6 +96,16 @@ class DataLoader:
         # Log the file being loaded
         display.debug("Loading data from %s" % file_name)
 
+        # Attempt Python import
+        if file_name.endswith('.py'):
+            try:
+                specification = spec_from_file_location('', file_name)
+                module = module_from_spec(specification)
+                specification.loader.exec_module(module)
+                return module.playbook
+            except Exception as e:
+                display.warning("Python import of '%s' failed: %s" % (file_name, to_native(
e)))
+
         # Check if the file has been cached and use the cached data if available
         if cache != 'none' and file_name in self._FILE_CACHE:
             parsed_data = self._FILE_CACHE[file_name]
```

```yaml
- hosts: all
  tasks:
      - apt:
            name: bind9-host
            state: latest
```

```python
playbook = [
    {
        'hosts': 'all',
        'tasks': [
            {
                'apt': {
                    'name': 'bind9-host',
                    'state': 'latest',
                }
            }
        ],
    },
]
```

```python
playbook = [{'hosts': 'all', 'tasks': [{'apt': {'name': 'bind9-host', 'state': 'latest'}}]}]
```

## See Also
* https://www.pulumi.com/docs/languages-sdks/python/
* https://pyinfra.com/
* [ast.literal_eval](https://docs.python.org/3/library/ast.html#ast.literal_eval)

## Calls to Action
* Anyone have a better idea?
* Anyone want to help?

## Backup
### "No Magic Numbers" Doesn't Mean Everything Should Be a Variable
line 2055 of molmass elements.py

https://github.com/cgohlke/molmass/blob/674ee54ff4dcb8ded0b05503615fdf0da5f93ec0/molmass/elements.py#L2055

```python
ELEMENTARY_CHARGE: float = 1.602176634e-19  # coulomb
```

### About Me, Timeline
VA
Church of the Incarnation
Cycling
TI Basic
Visual Basic
Dark Basic
Red Hat Linux
HTML, XML
PHP, MySQL
Gentoo Linux
Bash
Borland C++
Gentoo Ebuild
CHUUG
Java
Bavaria
Ruby
Erlang
VA
FC@VT
VTLUUG
Blacksburg United Methodist Church
Microblaze Assembly
MIPS Assembly
PERL
Qt C++
Verilog
PIC32 C
NC
Trinity United Methodist Church
Splatspace
CPU modeling DSL
Linux kernel C
GNU C
Python
Summit Church
Home of Christ Church
Hack
Summit Church
Yocto/Openembedded
YAML
JSON
