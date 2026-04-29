"""Grant access to people in the Biobuddies GitHub organization."""

from helicopyter import cona, provider, resource, terraform
from stacks.base import r2_backend

try:
    # Full membership not checked into the public repository
    from deploys.buddies.members import (  # type: ignore[import-not-found]  # pyright: ignore[reportMissingImports]
        mapping,
    )
except ImportError:
    # Example contents for GitHub Actions and readers
    mapping = {'coving.tron': ('covingtron', 'admin')}

terraform.required_providers(
    github={'source': 'integrations/github', 'version': '6.6.0'},
)
r2_backend(cona, terraform)
provider.github(owner='biobuddies')

for firstname_dot_lastname, (username, role) in mapping.items():
    resource.github_membership(firstname_dot_lastname.replace('.', '_'))(
        role=role,
        username=username,
    )
