"""Tests for the inline_single_use_assignment GritQL pattern."""

from pathlib import Path
from shutil import which
from subprocess import run

GRIT = which('grit') or 'grit'
PATTERN = Path('.grit/patterns/inline_single_use_assignment.grit')


def apply(tmp_path: Path, source: str) -> str:
    test_file = tmp_path / 'subject.py'
    test_file.write_text(source)
    run(
        [GRIT, 'apply', '--force', str(PATTERN), str(test_file)],  # noqa:S603
        check=True,
        capture_output=True,
    )
    return test_file.read_text()


def test_positive_two_assignments(tmp_path: Path) -> None:
    result = apply(
        tmp_path,
        'x = foo()\nbar(x)\n\ny = baz()\nqux(y)\n',
    )
    assert 'bar(foo())' in result
    assert 'qux(baz())' in result
    assert 'x = foo()' not in result
    assert 'y = baz()' not in result


def test_negative_no_assignment(tmp_path: Path) -> None:
    source = 'foo()\nbar()\n'
    assert apply(tmp_path, source) == source


def test_negative_assignment_unused(tmp_path: Path) -> None:
    source = 'x = foo()\nbar()\n'
    assert apply(tmp_path, source) == source


def test_negative_assignment_used_twice(tmp_path: Path) -> None:
    source = 'x = foo()\nbar(x)\nbaz(x)\n'
    assert apply(tmp_path, source) == source
