"""Grant access to people in the Biobuddies GitHub organization."""

from helicopyter import resource
from stacks.base import provide

try:
    # Full membership not checked into the public repository
    from deploys.buddies.members import (  # type: ignore[import-not-found]  # pyright: ignore[reportMissingImports]
        mapping,
    )
except ImportError:
    # Example contents for GitHub Actions and readers
    mapping = {'coving.tron': ('covingtron', 'admin')}

provide('integrations/github', '6.6.0', owner='biobuddies')

for firstname_dot_lastname, (username, role) in mapping.items():
    resource.github_membership(firstname_dot_lastname.replace('.', '_'))(
        role=role, username=username
    )
