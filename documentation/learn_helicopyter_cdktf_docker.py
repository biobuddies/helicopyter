"""Docker example using Helicopyter with legacy CDKTF syntax."""

from cdktf_cdktf_provider_docker.container import Container
from cdktf_cdktf_provider_docker.image import Image

from helicopyter.cdktf import HeliStack


def synth(stack: HeliStack) -> None:
    stack.provide('docker')

    stack.push(
        Container,
        'nginxContainer',
        name='tutorial',
        image=stack.push(Image, 'nginxImage', name='nginx:latest', keep_locally=False).name,
        ports=[{'internal': 80, 'external': 8000}],
    )
