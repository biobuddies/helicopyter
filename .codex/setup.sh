#!/bin/bash
set -o errexit -o nounset -o pipefail
exec "$(git rev-parse --show-toplevel)/.biobuddies/setup.bash"
