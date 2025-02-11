#!/bin/bash
# shellcheck disable=1054,1056,1072,1073,1083
set -o errexit -o nounset -o pipefail -o xtrace
: template=hooks/post_gen_project.bash rendering=$0
{% set suffix = '{' ~ cookiecutter.languages ~ '}.gitignore' %}
curl -s https://raw.githubusercontent.com/github/gitignore/main/{{ suffix }} >.gitignore
