Make the `git show` great. Omit explanations unless specifically requested.

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

Prefer --long-arguments for easier human review.

Define before use. Alphabetize peers unless otherwise directed. Longer collections may be sectioned
first, then alphabetized within each section.

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

## Great Git
Avoid `git add --all` to focus commits and prevent accidentally including temporary files.

Branches should almost always track `origin/main`. Create new branches with
`git checkout -b branch-name origin/main` (or set upstream for existing branches with
`git branch --set-upstream-to=origin/main`).

Use `git commit --all --amend --no-edit` and squash/fixup to iterate on commits without causing a
train-of-thought git history.

When rebasing, avoid interactive commands as stdin might be wired up wrong.

Use `gh` command line interface (usually installed by github-cli asdf plugin) for GitHub operations.

Use filtered git history to understand design choices, authorship, and timing.
