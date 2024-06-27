"""Grant access to people in the Biobuddies GitHub organization."""

from cdktf_cdktf_provider_github.membership import Membership

from helicopyter import HeliStack

people = {
    'christopher.covington': ('covracer', 'admin'),
    'duncan.tormey': ('DuncanTormey', 'admin'),
    'james.braza': ('jamesbraza', 'admin'),
}


def synth(stack: HeliStack) -> None:
    stack.provide('github')
    for firstname_dot_lastname, (username, role) in people.items():
        stack.push(
            Membership, firstname_dot_lastname.replace('.', '_'), username=username, role=role
        )
