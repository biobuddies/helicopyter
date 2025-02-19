"""Grant access to people in the Biobuddies GitHub organization."""

from cdktf_cdktf_provider_github.membership import Membership

from stacks.base import BaseStack

buddies = {
    'christopher.covington': ('covracer', 'admin'),
    'darren.pham': ('darpham', 'admin'),
    'duncan.tormey': ('DuncanTormey', 'admin'),
    'james.braza': ('jamesbraza', 'admin'),
    'matt.fowler': ('mattefowler', 'admin'),
    'nadia.wallace': ('16NWallace', 'admin'),
}


def synth(stack: BaseStack) -> None:
    stack.provide('github', owner='biobuddies')
    for firstname_dot_lastname, (username, role) in buddies.items():
        stack.push(
            Membership, firstname_dot_lastname.replace('.', '_'), role=role, username=username
        )
