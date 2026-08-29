#!/bin/bash
# Single repository sessions run this automatically. Multi repository sessions start in the
# parent directory, finding no .claude, so their environment setup script must run setup.bash.
set -o errexit -o nounset -o pipefail
# Laptops already have mise and its tools installed.
[ "${CLAUDE_CODE_REMOTE:-}" = true ] || exit 0
exec "$CLAUDE_PROJECT_DIR/.biobuddies/setup.bash"
