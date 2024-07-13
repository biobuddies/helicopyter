"""Grant access to people in the Biobuddies GitHub organization."""

from cdktf_cdktf_provider_github.membership import Membership

from helicopyter import HeliStack

buddies = {
    'christopher.covington': ('covracer', 'admin'),
    'darren.pham': ('darpham', 'admin'),
    'duncan.tormey': ('DuncanTormey', 'admin'),
    'james.braza': ('jamesbraza', 'admin'),
    'matt.fowler': ('mattefowler', 'admin'),
}


def synth(stack: HeliStack) -> None:
    stack.provide('github')
    for firstname_dot_lastname, (username, role) in buddies.items():
        stack.push(
            Membership, firstname_dot_lastname.replace('.', '_'), username=username, role=role
        )
