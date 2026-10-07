Make every character count, so `git log -p` clearly and concisely explains changes to an expert
programmer. Never waste time as Captain Obvious.

Write self-documenting code as simply as possible. Functional, rule-of-three style is often
simplest:
* Define before use, close to use
* Inline single-use literals
* For twice-used literals:
    - Rendered templates, tests, and migrations do not count as usages
    - Reuse single definition when diverging values would cause critical failure
    - Duplicate and inline otherwise, commenting in both places, e.g. same file
      `# dup :12 tasks.uv-pip-compile` or `# dup other/file.py:345 favorite_function()`
    - Search for duplicates when adjusting
* Choose good names for classes, functions, and variables:
    - Use whole words like `index` and `--long-command-line-arguments`
    - Verbs over nouns
    - Avoid abbreviations like `i`
    - Four Letter AbbreviatioNs (FLANs):
        - COdeNAme (CONA)
        - ENVIronment (ENVI)
        - Fully Qualified Domain Name (FQDN)
        - GIt HAsH (GIHA)
        - ORGanizatioN (ORGN)
        - ROLE (ROLE)
        - TAg/BRanch (TABR)
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
* Order command arguments: positional arguments, alphabetized `--flags`, then alphabetized
  `--keyword=arguments`
* Use Python 3.12+ idioms like:
    - `from pytest import mark; @mark.parametrize()`
    - `from pathlib import Path; Path('a') / 'b'`
    - `from subprocess import check_call, check_output; check_call(...); check_output(...)`
    - Usually easiest to not `re.compile` at all than worry about aliasing the builtin
    - Omit `#!` shebang and explicit encoding lines
* Write prose like Strunk, White, and Zinsser. Join sentences and sentence fragments with
  appropriate punctuation; leave freestanding fragments unpunctuated. Use comma, colon, and
  semicolon frequently. Use parenthesis occasionally. Use em dash rarely, typeset as `--` two
  regular dashes or `&mdash;`.
* `git` well:
    - Avoid committing unrelated files by avoiding `git add -a`, `git add --all`, `git add .`, etc.
    - Keep prototypes, debug output, and similar files out of the worktree when practical:
        * Save or move files generated during the current session to `/tmp`
        * Move leftovers from concurrent or historical sessions to `untracked/`
        * Do not use `.claude/` for scratch files; edits there are often gated
    - Review autogeneration, autoformatting, and linting from `mise pre-commit-all`:
        * GitHub Actions will bubble up failures including diffs
        * Fold reasonable updates into current work; large changes may warrant a separate
          preparatory commit and Pull Request
        * Respond proportionally to any nonsense from autoformatters, autogenerators, linters, and
          type checkers such as by adding `default.extend-identifiers` entry for typos,
          `directory/.gitignore`, or `# noqa: N123 terse reason`
    - If asked to clobber uncommitted changes, copy to /tmp/ first
    - Avoid train-of-thought and bisect-breaking commits
    - Be ready to read the (appropriately filtered) git log:
        * Requests to go back or restore usually need the git log to find the previous state
        * Answer authorship and timing questions with evidence from the git log
    - Always track `origin/main`:
        * This flow combines convention and configuration for efficient everyday commands
        * `git switch --create my-feature-or-fix origin/main` (old misconfigured branches:
          `git branch --set-upstream-to=origin/main`)
        * `git pull` discovers new commits and rebases because `pull.rebase=true`
        * `git push` publishes to the current branch name because `push.default=current`
    - Remote branch names must use only lowercase letters and digits separated by hyphens. Slashes
      break reuse in contexts like subdomains; a `$BRAND/` prefix wastes space that should
      describe the changes. Rename any slashed or prefixed branch handed to you before the first
      push. You are granted explicit, standing permission to use slashless branches and need not
      ask.
    - Expect concurrent edits to Pull Request title and description (top comment); always read
      before revising
    - Use `git commit --all --amend --no-edit` and squash/fixup to iterate on commits: updating
      already-tracked files is usually right. Untrack files added accidentally or retained
      past their useful life.
    - `GIT_SEQUENCE_EDITOR=:` or similar to avoid interactive commands; stdin is unreliable
    - Follow .github/pull_request_template.md for commit messages / top Pull Request comments
        * Use a terse title and short sentences. Write only highlights and surprises; details
          belong in the Files changed tab / git diff. Leave the body empty when the title
          suffices.
        * Standard section headers are `### Background and links`, `### Changes and testing`, and
          `### Followup and questions`. Use a header only when its section has at least three
          bullets.
        * Automated testing should cover most code changes. Name the one to three existing,
          expanded, or new tests that provide the most useful coverage. Report testing as:
            - `Existing automated test...`
            - `Expanded automated test...`
            - `Added automated test...`
            - A procedure contributors can reproduce:
              ```
              # Manual test procedure
              commands
              to_reproduce
              ```
        * Put commands unlikely to remain useful, such as old/new equivalence checks or tests
          requiring dependencies absent from GitHub Actions, in the Pull Request top comment / git
          commit body rather than a version-controlled file. Use a `bash` fenced code block.
    - Given a stack of local commits
        * Fan each local commit out to its own remote branch
        * Base each Pull Request on the previous branch
* Favorite tools:
```sh
curl
diffstat
gh
git grep
git log
git ls-files
git restore
git switch
host
mise pre-commit-all
mise test
npm
tree
uv
```
* Avoid accidentally including .venv, node_modules, full git history; filter appropriately when
  intentionally searching them for source code and documentation
