"""Docker example using Python Syntax for Terraform."""

from helicopyter import Block, provider, resource, terraform

terraform.required_providers(docker={'source': 'kreuzwerker/docker', 'version': '3.4.0'})
provider.docker()

resource.docker_container.nginxContainer(
    name='tutorial',
    image=resource.docker_image.nginxImage(name='nginx:latest', keep_locally=False).name,
    ports=Block('ports')(internal=80, external=8000),
)
