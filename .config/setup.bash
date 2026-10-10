#!/bin/bash
# Bootstrap mise and this repository's tools in agent sandboxes lacking both. Hosts discard
# session start hook output, so append everything to a log reviewable afterwards.
set -o errexit -o nounset -o pipefail -o xtrace
log=/tmp/setup.log
exec > >(tee -a "$log") 2>&1
datetimez() { date -u '+%F %TZ'; }
trap 'echo "ERROR $(datetimez) $PWD"' ERR
toplevel=$(git -C "$(dirname "${BASH_SOURCE[0]:?requires BASH}")" rev-parse --show-toplevel)
cd "$toplevel"
echo "Start $(datetimez) $PWD"
# See also mise check-branch and CONTRIBUTING.md
branch=$(git branch --show-current)
[[ $branch == "${branch##*/}" ]] || git branch --move "${branch##*/}"
export PATH="$HOME/.local/bin:$PATH"
command -v mise >/dev/null || curl https://mise.run | sh
# Trust the parent so sibling checkouts of a multi-repository session need no second visit.
mise settings add trusted_config_paths "$(dirname "$toplevel")"
mise trust --yes
mise install
# mise install exits 0 when postinstall fails
# dup .config/mise.toml tasks.actionlint
proxy_ca=/root/.ccr/agent-proxy-ca.crt
if [[ -f $proxy_ca ]] \
    && ! openssl x509 -in $proxy_ca -noout -ext keyUsage 2>/dev/null | grep -q 'Key Usage'; then
    # Claude Code on the web's proxy CA lacks the key usage extension Python 3.13 requires, so
    # sdists downloading binaries while building fail:
    # https://gist.github.com/mdehling/350fc63d286a31b2653aef1362c6b0f5
    grep -vE '^(actionlint|hadolint)-py' requirements.txt | mise exec -- uv pip sync -
else
    mise exec -- uv pip sync requirements.txt
fi
mise exec -- npm clean-install --no-audit --no-fund
if [ -n "${CLAUDE_ENV_FILE-}" ]; then
    # Claude Code sources this file before each Bash command, activating mise for its directory
    mise activate bash >>"$CLAUDE_ENV_FILE"
else
    # Environment setup scripts run before Claude Code snapshots a login shell; shims choose tools
    # by directory when run
    # shellcheck disable=SC2016
    mise_shims='export PATH="$HOME/.local/share/mise/shims:$PATH"'
    grep -qsxF "$mise_shims" ~/.profile || echo "$mise_shims" >>~/.profile
fi
if [ "${CLAUDE_CODE_REMOTE:-}" = true ]; then
    mkdir --parents ~/.claude
    ln --force --symbolic "$toplevel/.claude/settings.json" ~/.claude/settings.json
fi
echo "Complete $(datetimez) $PWD"
