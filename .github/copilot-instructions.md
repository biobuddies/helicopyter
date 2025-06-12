Explicitly specify units: preferably in data and code; fall back to comments. Prefer whole words
like `index` to abbreviations like `i`. Prefer `from requests import get` style unless there is
aliasing like `re.compile` with the builtin. Name variables well so that most code is easy for
proficient programmer to understand. Do not comment on rote execution. Inline variables used once.
Prefer `python -m package.module` to `python package/module.py` to avoid relative import surprises.
Prefer modern Python 3 idioms, like `from pathlib import Path; Path('a') / 'b'` instead of
`from os import path; path.join('a', 'b')`.

Run `just pcm $FILES` to autoformat and lint, or approximate with 4 space indentations, single
quotes, and 100 character lines.

Use git history to understand design choices. Follow the Rule of Three for writing new abstractions.
Comment "# same as other/file.py:123" when there are exactly two duplicates.