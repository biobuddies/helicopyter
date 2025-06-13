Explicitly specify units: preferably in data and code; fall back to comments. Prefer whole words
like `index` to abbreviations like `i`. Prefer `from requests import get` style unless there is
aliasing, like `re.compile` with the builtin. Name variables well so that most code is easy for
proficient programmers to understand. Do not comment on rote execution. Inline variables used once.
Prefer `python -m package.module` to `python package/module.py` to avoid surprises with relative
imports. Prefer modern Python 3 idioms, like `from pathlib import Path; Path('a') / 'b'` instead of
`from os import path; os.path.join('a', 'b')`.

Run `just pcm file0 file1` to autoformat and lint, or approximate with 4 space indentations, single
quotes, and 100 character lines.

Use git history to understand design choices, variance, and timing. Follow the Rule of Three for
writing new abstractions. Comment `# SAMEAS other/file.py:123` when there are two exact or nearly
exact copies.
