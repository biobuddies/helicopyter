"""Upstream CDKTF example to compare with Helicopyter."""

from cdktf import App, TerraformStack
from cdktf_cdktf_provider_docker.container import Container
from cdktf_cdktf_provider_docker.image import Image
from cdktf_cdktf_provider_docker.provider import DockerProvider
from constructs import Construct


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str) -> None:
        super().__init__(scope, ns)

        DockerProvider(self, 'docker')

        docker_image = Image(self, 'nginxImage', name='nginx:latest', keep_locally=False)

        Container(
            self,
            'nginxContainer',
            name='tutorial',
            image=docker_image.name,
            ports=[{'internal': 80, 'external': 8000}],
        )


app = App()
MyStack(app, 'learn-cdktf-docker')

app.synth()
