"""Grant access to people in the Biobuddies GitHub organization."""

from cdktf_cdktf_provider_github.membership import Membership

from stacks.base import BaseStack

try:
    # Full membership not checked into the public repository
    from deploys.buddies import mapping  # type: ignore[attr-defined]
except ImportError:
    # Example contents for GitHub Actions and readers
    mapping = {'christopher.covington': ('covracer', 'admin')}


def synth(stack: BaseStack) -> None:
    stack.provide('github', owner='biobuddies')
    for firstname_dot_lastname, (username, role) in mapping.items():
        stack.push(
            Membership, firstname_dot_lastname.replace('.', '_'), role=role, username=username
        )
