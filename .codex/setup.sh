#!/bin/bash
set -o errexit -o nounset -o pipefail
exec "$(dirname "$0")/../.config/setup.bash"
