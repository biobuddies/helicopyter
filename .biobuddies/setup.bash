#!/bin/bash
# Bootstrap mise and this repository's tools in agent sandboxes lacking both. Hosts discard
# session start hook output, so append everything to a log reviewable afterwards.
set -o errexit -o nounset -o pipefail
log=/tmp/setup.log
exec > >(tee -a "$log") 2>&1
datetimez() { date -u '+%F %TZ'; }
trap 'echo "ERROR $(datetimez) $PWD"' ERR
# cd "$(git rev-parse --show-toplevel)" would stay put on the empty string outside a repository
toplevel=$(git rev-parse --show-toplevel)
cd "$toplevel"
echo "Start $(datetimez) $PWD"
export PATH="$HOME/.local/bin:$PATH"
command -v mise >/dev/null || curl https://mise.run | sh
# Trust the parent so sibling checkouts of a multi-repository session need no second visit.
mise settings add trusted_config_paths "$(dirname "$toplevel")"
mise trust --yes
version=''
for config in .config/mise.toml mise.toml; do
    [ -f "$config" ] || continue
    version=$(sed -nE "s|^'aqua:tofuutils/tenv' = '([^']+)'.*|\1|p" "$config")
    [ -n "$version" ] && break
done
# GitHub release downloads are firewalled in Claude Code on the web, blocking mise's aqua
# backend from fetching tenv. Build tenv from source via mise's go backend instead.
if [ -n "$version" ] && [ "${CLAUDE_CODE_REMOTE:-}" = true ]; then
    mise settings add disable_tools aqua:tofuutils/tenv
    mise use --global "go:github.com/tofuutils/tenv/v${version%%.*}/cmd/tenv@$version"
fi
mise install
# Multi-repository sessions start in the parent directory, so activate per directory instead of
# exporting one repository's paths.
grep -q 'mise activate' ~/.bashrc || echo 'eval "$(mise activate bash)"' >>~/.bashrc
echo "Complete $(datetimez) $PWD"
