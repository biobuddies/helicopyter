#!/bin/bash
set -euxo pipefail

curl -s https://raw.githubusercontent.com/github/gitignore/main/{Node,Python,Terraform}.gitignore >.gitignore
