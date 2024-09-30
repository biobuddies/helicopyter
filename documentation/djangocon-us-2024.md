## Why Write Down Infrastructure?
* Reproducibility
* Automation
* Disaster recovery

## Why Use Terraform?
* Simplicity
* Wealth of providers
* Good diffing

## Original CDKTF
```python
#!/usr/bin/env python

from constructs import Construct
from cdktf import App, TerraformStack
from cdktf_cdktf_provider_docker.image import Image
from cdktf_cdktf_provider_docker.container import Container
from cdktf_cdktf_provider_docker.provider import DockerProvider


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        DockerProvider(self, 'docker')

        docker_image = Image(self, 'nginxImage',
            name='nginx:latest',
            keep_locally=False)

        Container(self, 'nginxContainer',
            name='tutorial',
            image=docker_image.name,
            ports=[{
                'internal': 80,
                'external': 8000
            }])


app = App()
MyStack(app, "learn-cdktf-docker")

app.synth()
```

## Diff from CDKTF to Helicopyter
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

## Helicopyter
```python
from cdktf_cdktf_provider_docker.container import Container
from cdktf_cdktf_provider_docker.image import Image
from helicopyter import HeliStack
 
def synth(stack: HeliStack):
    stack.provide('docker')
 
    docker_image = stack.push(Image, 'nginxImage', name='nginx:latest', keep_locally=False)
 
    stack.push(
        Container,
        'nginxContainer',
        name='tutorial',
        image=docker_image.name,
        ports=[{'internal': 80, 'external': 8000}],
    )
```

## Uses
* Containers for Gunicorn web servers and Celery workers
* PostgreSQL database
* Load balancers
* Intranetworking (authenticating proxy)
* Git repository configuration
* Accounts and access to service providers
