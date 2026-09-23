"""Compare example synthesis with fixed HCL expectations."""

from os import environ, pathsep
from pathlib import Path
from subprocess import check_output
from sys import executable

from pytest import importorskip, mark


@mark.parametrize(
    ('example', 'source'),
    (
        ('demo', 'deploys/demo/terraform/main.py'),
        ('docker_pst', 'documentation/learn_helicopyter_pst_docker.py'),
        ('docker_cdktf', 'documentation/learn_helicopyter_cdktf_docker.py'),
    ),
)
def test_example_hcl(tmp_path: Path, example: str, source: str) -> None:
    root = Path(__file__).parent
    if example == 'docker_cdktf':
        importorskip('cdktf_cdktf_provider_docker')
    else:
        (tmp_path / 'sitecustomize.py').write_text(
            "import sys\nsys.modules.update(dict.fromkeys(('cdktf', 'constructs', 'jsii')))\n"
        )
    deploy = tmp_path / 'deploys' / 'demo' / 'terraform'
    deploy.mkdir(parents=True)
    (tmp_path / 'deploys' / '__init__.py').touch()
    (deploy / 'main.py').write_text((root / source).read_text())
    check_output(
        [executable, '-m', 'helicopyter', 'demo', '--format_with', 'cat'],
        cwd=tmp_path,
        env={
            **environ,
            'PATH': environ['PATH'] if example == 'docker_cdktf' else '/usr/bin:/bin',
            'PYTHONPATH': f'{tmp_path}{pathsep}{root}',
        },
    )
    assert (deploy / 'main.tf').read_text().split() == (
        root / 'tests' / 'fixtures' / f'{example}.tf'
    ).read_text().split()
