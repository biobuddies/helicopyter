Explicitly specify units: preferably in data and code; fall back to comments. Prefer whole words
like `index` to abbreviations like `i`. Prefer `from requests import get` style unless there is
aliasing like `re.compile` with the builtin.

Run `just pcm $FILES` to autoformat and lint, or approximate with 4 space indentations, single
quotes, and 100 character lines.