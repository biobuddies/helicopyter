# Usage: bash providers/cloudflare/build.bash
# Patched Cloudflare provider zip in ${RUNNER_TEMP:-/tmp}
set -o errexit -o nounset -o pipefail -o xtrace
here=$(cd "$(dirname "$0")" && pwd)
upstream=v5.27.0
version=${upstream#v}-startup.2 # Bump the suffix whenever the patch changes
mise checkout "terraform-provider-cloudflare@$upstream"
cd ~/code/terraform-provider-cloudflare
git restore .
# Union of resources and data sources in helicopyter.cloudflare.jam() and
# the covicovey, mublog, rivertide, and other deploys
python "$here/trim.py" internal/provider.go \
    dns_record r2_bucket ruleset workers_custom_domain workers_route \
    workers_script workers_script_subdomain zero_trust_access_application \
    zero_trust_access_identity_provider zero_trust_access_policy \
    zero_trust_tunnel_cloudflared
git apply "$here/startup-time-ms.patch"
go=(mise exec "go@$(awk '$1 == "go" { print $2 }' go.mod)" --)
"${go[@]}" gofmt -w internal/provider.go
"${go[@]}" go test ./internal/services/workers_script/...
output=${RUNNER_TEMP:-/tmp}
"${go[@]}" go build -trimpath "-ldflags=-s -w -X main.version=$version" \
    "-o=$output/terraform-provider-cloudflare_v$version" .
cd "$output"
rm -f "terraform-provider-cloudflare_${version}_linux_amd64.zip"
zip -j "terraform-provider-cloudflare_${version}_linux_amd64.zip" \
    "terraform-provider-cloudflare_v$version"
sha256sum "terraform-provider-cloudflare_${version}_linux_amd64.zip"
