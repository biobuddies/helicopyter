#!/bin/bash
set -euxo pipefail
{% set suffix = '{' ~ cookiecutter.languages ~ '}.gitignore' %}
curl -s https://raw.githubusercontent.com/github/gitignore/main/{{ suffix }} >.gitignore
