"""Pyinfra reimplementation of devready/forceready shell functions.

Usage:
    pyinfra @local .biobuddies/forceready.py       # apply changes (forceready)
    pyinfra @local --dry .biobuddies/forceready.py  # dry run (devready)

Carried forward from includes.bash; ASDF bootstrapping intentionally dropped (use mise).
"""

from os import getenv
from pathlib import Path

from pyinfra import host
from pyinfra.facts.server import Os, User
from pyinfra.operations import apt, brew, files, git

# Git configuration matching expected_git_configuration in includes.bash
EXPECTED_GIT_CONFIG = {
    'advice.skippedCherryPicks': 'false',
    'core.commentChar': ';',
    'diff.colormoved': 'zebra',
    'init.defaultBranch': 'main',
    'pull.rebase': 'true',
    'push.default': 'current',
    'rebase.autosquash': 'true',
}

# Defined for all operating systems to support Linux containers from macOS
DEBS = [
    'bash', 'bind9-host', 'ca-certificates', 'curl', 'file', 'fping', 'git', 'less',
    'procps', 'tmux', 'tree',
]

# Pre-installed on Sonoma — skip upgrades: host, file, less, ps
# asdf intentionally dropped in favor of mise
BRWS = ['bash', 'curl', 'fping', 'git', 'gnu-sed', 'tmux', 'tree']

MACOS_GITIGNORE_URL = (
    'https://raw.githubusercontent.com/github/gitignore/master/Global/macOS.gitignore'
)

home = Path.home()
operating_system = host.get_fact(Os)
user = host.get_fact(User)

# -- Directories -------------------------------------------------------------------------

for directory in ('.config/git', '.local/bin', 'code'):
    files.directory(path=str(home / directory))

# -- Git configuration -------------------------------------------------------------------

for key, value in EXPECTED_GIT_CONFIG.items():
    git.config(key=key, value=value)

insh_name = getenv('INSH_NAME')
if insh_name:
    git.config(key='user.name', value=insh_name)

insh_email = getenv('INSH_EMAIL')
if insh_email:
    git.config(key='user.email', value=insh_email)

# -- Platform-specific packages ----------------------------------------------------------

if operating_system == 'Darwin':
    brew.packages(packages=BRWS)
    files.download(
        name='Download macOS gitignore',
        src=MACOS_GITIGNORE_URL,
        dest=str(home / '.config/git/ignore'),
    )

elif operating_system == 'Linux':
    use_sudo = user != 'root'
    apt.update(_sudo=use_sudo)
    apt.packages(
        packages=DEBS,
        no_recommends=True,
        _sudo=use_sudo,
    )
