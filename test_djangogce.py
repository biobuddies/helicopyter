"""Check VM example synthesis and propagation of remote deployment failures."""

from os import environ
from pathlib import Path
from shutil import copytree, ignore_patterns
from subprocess import check_output, run
from sys import executable

from pytest import mark


def test_djangogce_synthesis(tmp_path: Path) -> None:
    root = Path(__file__).parent
    destination = tmp_path / 'deploys' / 'djangogce'
    copytree(root / 'deploys' / 'djangogce', destination, ignore=ignore_patterns('.terraform'))
    (tmp_path / 'deploys' / '__init__.py').touch()
    check_output(
        [executable, '-m', 'helicopyter', 'djangogce', '--format_with', 'cat'],
        cwd=tmp_path,
        env={**environ, 'PYTHONPATH': str(root)},
    )
    assert (destination / 'terraform' / 'main.tf').read_text().split() == (
        root / 'deploys' / 'djangogce' / 'terraform' / 'main.tf'
    ).read_text().split()


@mark.parametrize('deployment_status', (0, 1))
def test_djangogce_deployment_status(tmp_path: Path, deployment_status: int) -> None:
    gcloud = tmp_path / 'gcloud'
    gcloud.write_text(
        '#!/usr/bin/env bash\n'
        'printf "%s\\n" "$*" >> "$CALLS"\n'
        '[[ $* == *--command=true ]] && exit 0\n'
        f'exit {deployment_status}\n'
    )
    gcloud.chmod(0o755)
    calls = tmp_path / 'calls'
    result = run(
        ['bash', str(Path(__file__).parent / 'deploys' / 'djangogce' / 'redeploy.bash')],
        check=False,
        env={
            **environ,
            'CALLS': str(calls),
            'INSTANCE': 'django',
            'PATH': f'{tmp_path}:{environ["PATH"]}',
            'PROJECT': 'example',
            'ZONE': 'us-central1-a',
        },
    )
    assert result.returncode == deployment_status
    assert len(calls.read_text().split('--tunnel-through-iap')) == 3
    assert 'cloud-init status --wait &&' in calls.read_text()
    assert 'restart django-deploy.service &&' in calls.read_text()
