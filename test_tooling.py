"""Integration tests for tools and configuration."""

from json import loads
from os import environ, getenv
from pathlib import Path
from re import match
from subprocess import check_output

from pytest import mark


def test_just():
    assert check_output(['.venv/bin/just', 'cona']) == b'helicopyter\n'  # noqa: S603

    assert (
        check_output(['.venv/bin/just', 'envi']) == b'github\n'  # noqa: S603
        if getenv('GITHUB_ACTIONS')
        else b'local\n'
    )

    giha = check_output(['.venv/bin/just', 'giha'])  # noqa: S603
    assert match(rb'^[0-9a-f]{40}(-dirty)?\n$', giha)
    if check_output(['git', 'status', '--porcelain', '--untracked-files=no']):  # noqa: S603
        assert giha.endswith(b'-dirty\n')
    else:
        assert not giha.endswith(b'-dirty\n')

    assert check_output(['.venv/bin/just', 'orgn']) == b'biobuddies\n'  # noqa: S603


def test_mise():
    assert check_output(['mise', 'cona']) == b'helicopyter\n'  # noqa: S603

    assert (
        check_output(['mise', 'envi']) == b'github\n'  # noqa: S603
        if getenv('GITHUB_ACTIONS')
        else b'local\n'
    )

    giha = check_output(['mise', 'giha'])  # noqa: S603
    assert match(rb'^[0-9a-f]{40}(-dirty)?\n$', giha)
    is_dirty = bool(check_output(['git', 'status', '--porcelain', '--untracked-files=no']))  # noqa: S603
    assert giha.endswith(b'-dirty\n') == is_dirty

    assert check_output(['mise', 'orgn']) == b'biobuddies\n'  # noqa: S603

    tabr_env = {
        'MISE_TRUSTED_CONFIG_PATHS': getenv('MISE_TRUSTED_CONFIG_PATHS', ''),
        'PATH': environ['PATH'],
    }
    assert check_output(['mise', 'tabr'], env=tabr_env) == (  # noqa: S603
        b''
        if is_dirty
        else check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip() + b'\n'  # noqa: S603
    )


def test_prettier():
    test_path = Path('tmp-test-prettier.j2.html')
    test_path.write_text(
        '<html><body>\n{% for item in items %}<div>{{item}}</div>{% endfor %}\n</body></html>\n'
    )
    check_output(['git', 'add', str(test_path)])  # noqa: S603
    try:
        check_output(['mise', 'prettier-write'])  # noqa: S603
        assert test_path.read_text() == (
            '<html>\n'
            '    <body>\n'
            '        {% for item in items %}<div>{{ item }}</div>{% endfor %}\n'
            '    </body>\n'
            '</html>\n'
        )
    finally:
        check_output(['git', 'rm', '--force', '--quiet', str(test_path)])  # noqa: S603


def test_typos():
    input_path = Path('wxperiment-\xb5.yml')  # noqa: RUF100  # noqa: typos
    input_path.write_text('wxperiment:\n  - \xb5\n  yml')  # noqa: RUF100  # noqa: typos
    output_path = Path('experiment-\u03bc.yaml')
    check_output(['git', 'add', str(input_path)])  # noqa: S603
    try:
        check_output(['mise', 'typos'])  # noqa: S603  # noqa: typos
        assert output_path.read_text() == 'experiment:\n  - \u03bc\n  yaml'
    finally:
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)
        check_output(['git', 'rm', '--force', '--quiet', str(input_path)])  # noqa: S603
    # TODO also the html escape sequence &micro; -> &mu;


@mark.parametrize(
    ('git_describe', 'tabr'),
    (
        ('remotes/origin/mybranch', 'mybranch'),
        ('heads/mybranch', 'mybranch'),
        ('tags/v2025.02.03', 'v2025.02.03'),
        ('heads/mybranch-dirty', ''),
    ),
)
def test_tabr_git_describe_mocked(git_describe: str, tabr: str):
    original = loads(
        check_output(['mise', 'tasks', 'info', 'tabr', '--json'])  # noqa: S603
    )['run'][0].replace('\\n', '\n')
    target = 'git describe --all --dirty --exact-match'
    assert target in original
    mocked = original.replace(target, f'echo "{git_describe}"')
    output = (
        check_output(  # noqa: S603
            ['/usr/bin/env', 'bash', '-c', mocked], env={}
        )
        .decode()
        .strip()
    )
    assert output == tabr
