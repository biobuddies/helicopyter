Make every character count, so `git log -p` clearly and concisely explains changes to an expert
programmer. Never waste time as Captain Obvious.

Write self-documenting code as simply as possible. Functional, rule-of-three style is often
simplest:
* Define before use, close to use
* Inline single-use literals
* For twice-used literals:
    - Reuse single definition when diverging values would cause critical failure
    - Duplicate and inline otherwise, commenting `# dup other/file.py:123` in both places
    - Search for duplicates when adjusting
* Choose good names for classes, functions, and variables:
    - Use whole words like `index` and `--long-command-line-arguments`
    - Verbs over nouns
    - Avoid abbreviations like `i`
    - Avoid substring matches
* Chain function calls
* Use the ternary operator
* Use comprehensions and generator expressions
* Splat/unpack and slice
* Use for and while loops sparingly
    - Avoid the 1 + N query problem
    - For loops may be needed to append to collections under complex conditions
* Unless requested, never add new comments:
    - Except to cite or summarize surprising context
    - Keep existing comments
* Explicitly specify units: preferably in code and data; fall back to comments
* Approximate autoformatting and linting with
    - 4 space indentations
    - Simplest quotes and minimal escapes
        * Where equivalent, use 'single quotes' instead/outside of "double quotes"
        * """Triple double quote docstrings."""
        * Prefer '{f}-strings' until curly braces show up, then minimize escapes with percent
    - 100 character lines
    - Add fewer than 500 lines per commit/pull request
    - Split files around 500 lines
* Alphabetize, sometimes within sections (header worth a comment)
* Use Python 3.12+ idioms like:
    - `from pytest import parametrize`
    - `from pathlib import Path; Path('a') / 'b'`
    - `from subprocess import check_call, check_output; check_call(...); check_output(...)`
    - Usually easiest to not `re.compile` at all than worry about aliasing the builtin
    - Omit `#!` shebang and explicit encoding lines
* `git` well:
    - Avoid committing unrelated files by avoiding `git add -a`, `git add --all`, `git add .`, etc.
    - If asked to clobber uncommitted changes, copy to /tmp/ first
    - Avoid train-of-thought and bisect-breaking commits
    - Answer authorship and timing questions with evidence from the appropriately filtered git log
    - Branches should almost always track `origin/main`
    - Create new branches with `git checkout -b noslash-kebab-branch-name origin/main`
    - Set upstream for existing branches with `git branch --set-upstream-to=origin/main`
    - Use `git commit --all --amend --no-edit` and squash/fixup to iterate on commits
    - `GIT_SEQUENCE_EDITOR=:` or similar to avoid interactive commands; stdin is unreliable
    - Follow .github/pull_request_template.md for commit messages / top Pull Request comments
    - Given a stack of local commits
        * Fan each local commit out to its own remote branch
        * Base each Pull Request on the previous branch
* Favorite tools: `curl`, `gh`, `git`, `mise`, `npm`, `uv`
