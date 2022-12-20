Make the `git diff` great. Omit explanations unless specifically requested.

## Great Style
Your audience is proficient Python developers with limited time. Every character counts.

Within the constraints of Python (or Javascript, or Bash, or Markdown, etc.) write concise English
like William Zinsser.

Assume existing comments are valuable and worth keeping. Add no new comments. Instead choose good
variable names, function names, and type annotations.

Explicitly specify units: preferably in data and code; fall back to comments. Prefer whole words
like `index` to abbreviations like `i`.

Run `just pcm --files file0 file1` to autoformat and lint, or approximate with 4 space
indentations, single quotes, and 100 character lines.

Use filtered git history to understand design choices, authorship, and timing.

Follow the "Rule of Three" or "Write Everything Twice". Use literals directly, instead of
variables-used-once. Comment `# dup other/file.py:123` when you introduce or notice duplication.

## Great Python
Use modern Python 3 idioms, like `from pathlib import Path; Path('a') / 'b'` instead of
`from os import path; os.path.join('a', 'b')`.

Prefer `from requests import get` style unless there is
aliasing, like `re.compile` with the builtin. Leave most regular expressions uncompiled to simplify
code.

Prefer `python -m package.module` to `python package/module.py` to avoid surprises with relative
imports. Omit `#!` shebang lines.
