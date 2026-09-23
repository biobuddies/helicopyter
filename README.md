# Helicopyter

Helicopyter generates Hashicorp Configuration Language (HCL) syntax Terraform from Python. The new
**Python Syntax for Terraform** has minimal dependencies. Support for CDKTF sources moved to
`helicopyter.cdktf`. List `cdktf` as a dependency if you need it.

## 1. New deploy using Python Syntax for Terraform

With Python 3.12+, Helicopyter, and OpenTofu (or Terraform), create
`deploys/example/terraform/main.py`:

```python
from helicopyter import provider, resource, terraform

terraform.required_providers(null={'source': 'hashicorp/null', 'version': '~> 3.2'})
provider.null()
resource.null_resource.example(triggers={'message': 'Hello from Python'})
```

Run from the project root:

```sh
python -m helicopyter example
```

Helicopyter writes `deploys/example/terraform/main.tf` and autoformats it with OpenTofu. Use
`--format_with cat` to skip autoformatting, or `--format_with terraform` to format with Terraform.

`resource`, `data`, `provider`, and `variable` build blocks; attribute access supplies their labels.
Use `tlocals` for a `locals` block, `local` and `var` for references, and `Block` for other HCL blocks
or expressions. Use Terraform attribute names, Python dictionaries for maps, and `Block` instances
for nested blocks.

Each deployment lives at `deploys/<codename>/terraform/main.py`. Pass multiple codenames, or `all`,
to generate multiple deployments. Additional hand-written `.tf` files can coexist with `main.tf`.

Compare the Docker examples using [Python Syntax for Terraform](documentation/learn_helicopyter_pst_docker.py)
and [legacy CDKTF syntax](documentation/learn_helicopyter_cdktf_docker.py).

## 2. Migrate existing CDKTF to Python Syntax for Terraform

Migrate one deployment at a time. Before editing, synthesize its existing configuration and save
it for comparison. Keep its backend, workspace, provider versions, resource labels, and instance
keys unchanged so Terraform continues to address the same state objects.

Replace CDKTF imports and the `synth(stack: HeliStack)` function with module-level block builders.
For example, this legacy deployment:

```python
from cdktf_cdktf_provider_null.resource import Resource
from helicopyter.cdktf import HeliStack


def synth(stack: HeliStack):
    stack.provide('null')
    stack.push(Resource, 'example', triggers={'message': 'Hello from Python'})
```

becomes the null-provider example above.

Use the provider version constraint from your existing configuration instead of adopting the example
constraint during migration. The resource address remains `null_resource.example`.

| Legacy CDKTF | Python Syntax for Terraform |
| --- | --- |
| `stack.provide('github', owner='example')` | `provider.github(owner='example')` |
| `stack.push(Resource, 'example', ...)` | `resource.<terraform_resource_type>.example(...)` |
| `stack.push(TerraformVariable, 'message', ...)` | `variable.message(...)` |
| `stack.push(TerraformLocal, 'name', value)` | `tlocals(name=value)` |
| Variable/local token | `var.message` / `local.name` |
| Resource attribute token | `resource.<terraform_resource_type>.example.id` |
| `stack.cona` | `from helicopyter import cona` |

Translate CDKTF-specific properties and nested structures to the provider's Terraform schema.
Python strings are quoted; use references such as `var.message` or `Block('length(var.items)')`
when you need an unquoted Terraform expression. Use `Block('output', 'name')(value=...)` for outputs.
Preserve any `count`, `for_each`, lifecycle, import, or moved blocks used by the old configuration.
Raw CDKTF configurations may have generated resource IDs; preserve their actual Terraform addresses,
not just their Python construct names.

Regenerate with `python -m helicopyter <codename>` and compare `main.tf` with the saved configuration.
If the old generator produced `main.tf.json`, move that file out of the Terraform directory so both
versions do not declare the same resources. Compare the plan in the existing workspace without
upgrading providers, and investigate unexpected changes before applying.

After every deployment and shared helper has stopped importing CDKTF, remove `cdktf` and
generated Python provider packages from your dependencies. Node.js is no longer needed for
synthesis, though other project tools may still use it.

## 3. Continue using legacy CDKTF syntax

Install Node.js for CDKTF's JSII runtime. Declare `cdktf` and the Python provider packages your
configuration imports directly in your project's dependencies. The legacy example above needs
`helicopyter`, `cdktf`, and `cdktf-cdktf-provider-null`.

Change `from helicopyter import HeliStack` to `from helicopyter.cdktf import HeliStack`.
`synth(stack: HeliStack)`, `stack.provide`, and `stack.push` continue to work. `HeliStack` removes
CDKTF's `App` boilerplate and allocates logical IDs in Terraform's resource-prefix style instead
of CDK's hash-suffix style. Custom `HeliStack` subclasses remain supported; the example R2 subclass
now lives at `stacks.cdktf.BaseStack`. The CDKTF CLI and an npm installation of CDKTF are not required
by Helicopyter; Node.js itself must be available to JSII.

Legacy deployments can keep CDKTF's `import_from` and `move_from_id` methods. The `demos` extra
installs the Python provider packages used by this repository's legacy examples. Repository
contributors can use `mise install` to install the development dependencies and npm tooling;
the repository's `cdktf` optional dependency group feeds `requirements.txt` through
`uv pip compile --all-extras`. Consumers declare `cdktf` themselves.

Pure-Python and legacy deployments can coexist. The CLI selects legacy synthesis when a deployment
exports `synth`; otherwise it emits HCL from the registered Python blocks. A command selecting a
legacy deployment still needs its CDKTF and Node.js dependencies.

## Background

Helicopyter began as a wrapper around [CDKTF](https://github.com/hashicorp/terraform-cdk), inspired by
[Configerator](https://research.facebook.com/file/877841159827226/holistic-configuration-management-at-facebook.pdf)
and [Terraformpy](https://github.com/NerdWalletOSS/terraformpy). It keeps infrastructure descriptions
in Python while leaving planning, state management, and application to OpenTofu (or Terraform).

## What Helicopyter does (goals)

- Name in the resource-prefix Terraform style, instead of the hash-suffix CDK style. This makes
  reviewing plan output easier, and aligns with "Namespaces are one honking great idea -- let's do
  more of those!"
- Simplify `main.py` files by
    * Removing the `App` class, which does not correspond to a Terraform concept. Instead
        - A string attribute provides name information
        - Resource-specific scopes are provided by `HeliStack.push()`
        - The `synth` method is replaced by a module-level function, and called from a central
          location instead of distributed boilerplate.
    * Making custom TerraformStack/HeliStack subclasses optional instead of required. Defining a
      subclass only to instantiate one instance of it is more complicated than instantiating the
      base class and modifying the instance.
```diff
--- documentation/learn_cdktf_docker.py
+++ documentation/learn_helicopyter_cdktf_docker.py
@@ -1,30 +1,18 @@
-"""Upstream CDKTF example to compare with Helicopyter."""
+"""Docker example using Helicopyter with legacy CDKTF syntax."""
 
-from cdktf import App, TerraformStack
 from cdktf_cdktf_provider_docker.container import Container
 from cdktf_cdktf_provider_docker.image import Image
-from cdktf_cdktf_provider_docker.provider import DockerProvider
-from constructs import Construct
+
+from helicopyter.cdktf import HeliStack
 
 
-class MyStack(TerraformStack):
-    def __init__(self, scope: Construct, ns: str) -> None:
-        super().__init__(scope, ns)
+def synth(stack: HeliStack) -> None:
+    stack.provide('docker')
 
-        DockerProvider(self, 'docker')
-
-        docker_image = Image(self, 'nginxImage', name='nginx:latest', keep_locally=False)
-
-        Container(
-            self,
-            'nginxContainer',
-            name='tutorial',
-            image=docker_image.name,
-            ports=[{'internal': 80, 'external': 8000}],
-        )
-
-
-app = App()
-MyStack(app, 'learn-cdktf-docker')
-
-app.synth()
+    stack.push(
+        Container,
+        'nginxContainer',
+        name='tutorial',
+        image=stack.push(Image, 'nginxImage', name='nginx:latest', keep_locally=False).name,
+        ports=[{'internal': 80, 'external': 8000}],
+    )
```
- Enable hand-written and auto-generated Hashicorp Configuration Language (HCL) files to
  co-exist, allowing incremental adoption.
- Separate object instantiation from synthesis, allowing Python script to import the objects/data
  and do completely different things with them.
- Golang Terraform has a pretty good command line interface. The `ht[aip]` recipes in
  `.biobuddies/justfile` try to wrap it very lightly.

## What Helicopyter will probably never do (non-goals)

- Support languages other than Python
- Use CDKTF's command line interface. Integration with it is untested and not recommended.

## What Helicopyter might do in the future

- Support multiple backend configurations per codename
- Iterate on supported directory structures. For hysterical raisins, the currently supported
  directory structure is `f'deploys/{cona}/terraform'`, grouping
    * Primarily by COdeNAme (CONA), which is probably synonymous with application, deployment, and service
    * Secondarily by tool, such as `ansible`, `docker`, `terraform`, `python`
- Why do we need a Node.js server? Can we build dataclasses or Pydantic models out of the type annotations already being
  generated?
- Provide helper classes or functions for useful but annoyingly verbose patterns such as local-exec provisioner command
- Backend / state file linter such as: prod must exist, and region/bucket/workspace_key_prefix/key must follow pattern
