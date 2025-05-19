# shellcheck shell=bash
if [[ -f /.biobuddies/includes.bash ]]; then
    source /.biobuddies/includes.bash
else
    echo includes.sh has moved to .biobuddies/includes.bash to better accomodate downstream
    echo extensions and share a single popular fetch mechanism with files like .gitignore.
    echo Please update your .pre-commit-config.yaml to include the cookiecutter hook
    echo '- repo: https://github.com/biobuddies/helicopyter'
    echo '  rev: v2025.17.01  # or newer'
    echo '  hooks:'
    echo '      - id: cookiecutter'
    echo
    echo and run
    echo 'pre-commit run --all-files --hook-stage manual cookiecutter'
fi
