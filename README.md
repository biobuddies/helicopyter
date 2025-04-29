# Helicopyter

Helicopyter allows people to conveniently describe infrastructure using Python.

Perhaps like a helicopter hovering between the clouds and the ground, it allows this in a way that's
less like the AWS Cloud Development Kit (CDK) and more like Terraform.

## Background
Helicopyter uses [CDKTF](https://github.com/hashicorp/terraform-cdk) and is inspired by
[Configerator](https://research.facebook.com/file/877841159827226/holistic-configuration-management-at-facebook.pdf) and
[Terraformpy](https://github.com/NerdWalletOSS/terraformpy).

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
--- documentation/learn_cdktf_docker.py   2024-08-05 08:47:30
+++ documentation/learn_helicopyter_docker.py     2024-08-05 08:47:25
@@ -1,28 +1,18 @@
-from cdktf import App, TerraformStack
 from cdktf_cdktf_provider_docker.container import Container
 from cdktf_cdktf_provider_docker.image import Image
-from cdktf_cdktf_provider_docker.provider import DockerProvider
-from constructs import Construct
+from helicopyter import HeliStack
 
-class MyStack(TerraformStack):
-    def __init__(self, scope: Construct, ns: str):
-        super().__init__(scope, ns)
+def synth(stack: HeliStack):
- 
-        DockerProvider(self, 'docker')
+    stack.provide('docker')
 
-        docker_image = Image(self, 'nginxImage', name='nginx:latest', keep_locally=False)
+    docker_image = stack.push(Image, 'nginxImage', name='nginx:latest', keep_locally=False)
 
-        Container(
-            self,
-            'nginxContainer',
-            name='tutorial',
-            image=docker_image.name,
-            ports=[{'internal': 80, 'external': 8000}],
-        )
+    stack.push(
+        Container,
+        'nginxContainer',
+        name='tutorial',
+        image=docker_image.name,
+        ports=[{'internal': 80, 'external': 8000}],
+    )
-
-
-app = App()
-MyStack(app, 'learn-cdktf-docker')
-
-app.synth()
```
- Enable hand-written and auto-generated Hashicorp Configuration Language (HCL) files to
  co-exist, allowing incremental adoption.
- Separate object instantiation from synthesis, allowing Python script to import the objects/data
  and do completely different things with them.
- Golang Terraform has a pretty good command line interface. The `ht[aip]` recipes in
  `.biobuddies/justfile` try to wrap it very lightly.

### Importing and Renaming
Out of ignorance, early versions of Helicopyter carried custom support for generating `import`
blocks. The upstream CDKTF project [added support in fall of 2023](
https://www.hashicorp.com/en/blog/cdktf-0-19-adds-support-for-config-driven-import-and-refactoring
), although the documentation [1](
https://developer.hashicorp.com/terraform/cdktf/concepts/resources#refactoring-renaming-resources
) [2](
https://developer.hashicorp.com/terraform/cdktf/examples-and-guides/refactoring#moving-renaming-resources-within-a-stack
) unfortunately focuses on Javascript and its camelCase function names rather than Python and its
snake_case method names.

## Import Existing Resource Into Terraform State
```python
    stack.push(
        Resource,
        'new_name',
        ...,
    ).import_from('provider_resource.old_name')
```

## Rename or Move Within Terraform State
```python
    stack.push(
        Resource,
        'new_name',
        ...
    ).move_from_id('provider_resource.old_name')
```

## What Helicopyter will probably never do (non-goals)
- Support languages other than Python
- Use CDKTF's command line interface. Integration with it is untested and not recommended.

## What Helicopyter might do in the future
- Support multiple backend configurations per codename
- Iterate on supported directory structures. For hysterical raisins, the currently supported
  directory structure is `f'deploys/{cona}/terraform'`, grouping
    * Primarily by COdeNAme (CONA), which is probably synonymous with application, deployment, and service
    * Secondarily by tool, such as `ansible`, `docker`, `terraform`, `python`
- `__str__()` for `to_string()`, etc.
- Why do we need a Node.js server? Can we build dataclasses or Pydantic models out of the type annotations already being
  generated?
- Provide helper classes or functions for useful but annoyingly verbose patterns such as local-exec provisioner command
- Backend / state file linter such as: prod must exist, and region/bucket/workspace_key_prefix/key must follow pattern
