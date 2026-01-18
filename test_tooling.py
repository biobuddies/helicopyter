"""Integration tests for tools and configuration."""

from os import getenv
from pathlib import Path
from re import match
from subprocess import check_output
from tempfile import NamedTemporaryFile

import try_repo


def test_just():
    assert check_output(['.venv/bin/just', 'cona']) == b'helicopyter\n'  # noqa:S603

    assert (
        check_output(['.venv/bin/just', 'envi']) == b'github\n'  # noqa:S603
        if getenv('GITHUB_ACTIONS')
        else b'local\n'
    )

    giha = check_output(['.venv/bin/just', 'giha'])  # noqa:S603
    assert match(rb'^[0-9a-f]{40}(-dirty)?\n$', giha)
    if check_output(['git', 'status', '--porcelain']):  # noqa:S603
        assert giha.endswith(b'-dirty\n')
    else:
        assert not giha.endswith(b'-dirty\n')

    assert check_output(['.venv/bin/just', 'orgn']) == b'biobuddies\n'  # noqa:S603


def test_prettier():
    with NamedTemporaryFile('w+', delete_on_close=False, dir='.', suffix='.j2.html') as test_file:
        test_file.write(
            '<html><body>\n{% for item in items %}<div>{{item}}</div>{% endfor %}\n</body></html>\n'
        )
        test_file.close()
        try_repo.pre_commit.main.main(
            ('try-repo', '.', 'prettier-write', '--files', str(test_file.name), '--verbose')
        )
        assert Path(test_file.name).read_text() == (
            '<html>\n'
            '    <body>\n'
            '        {% for item in items %}<div>{{ item }}</div>{% endfor %}\n'
            '    </body>\n'
            '</html>\n'
        )


def test_typos(tmp_path: Path):
    input_path = tmp_path / 'wxperiment-\xb5.yml'  # noqa: typos
    input_path.write_text('wxperiment:\n  - \xb5\n  yml')  # noqa: typos
    try_repo.pre_commit.main.main(('try-repo', '.', 'typos', '--files', str(input_path)))
    assert (tmp_path / 'experiment-\u03bc.yaml').read_text() == 'experiment:\n  - \u03bc\n  yaml'
    # TODO also the html escape sequence &micro; -> &mu;
