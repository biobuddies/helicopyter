"""
Modified try-repo subcommand.

Sets cookiecutter hook args to ['.'] to use local repository instead of remote.
"""

import argparse
import logging
import tempfile
from pathlib import Path
from sys import argv

import pre_commit.main  # type: ignore[import-untyped]
from pre_commit import constants, output  # type: ignore[import-untyped]
from pre_commit.clientlib import load_manifest  # type: ignore[import-untyped]
from pre_commit.commands.run import run  # type: ignore[import-untyped]
from pre_commit.commands.try_repo import _repo_ref  # type: ignore[import-untyped]
from pre_commit.store import Store  # type: ignore[import-untyped]
from pre_commit.yaml import yaml_dump  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


def try_repo(args: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory() as tempdir:
        repo, ref = _repo_ref(tempdir, '.', args.ref)

        store = Store(tempdir)
        repo_path = store.clone(repo, ref)
        manifest = sorted(
            load_manifest(Path(repo_path) / constants.MANIFEST_FILE), key=lambda hook: hook['id']
        )

        config = yaml_dump(
            {
                'repos': [
                    {
                        'repo': repo,
                        'rev': ref,
                        'hooks': [
                            {
                                'id': hook['id'],
                                **({'args': ['.']} if hook['id'] == 'cookiecutter' else {}),
                            }
                            for hook in manifest
                        ],
                    }
                ]
            }
        )
        config_file = Path(tempdir) / constants.CONFIG_FILE
        config_file.write_text(config)

        output.write_line('=' * 79)
        output.write_line('Using config:')
        output.write_line('=' * 79)
        output.write(config)
        output.write_line('=' * 79)

        return run(str(config_file), store, args)


pre_commit.main.try_repo = try_repo

if __name__ == '__main__':
    raise SystemExit(pre_commit.main.main(('try-repo', '.', *argv[1:])))
