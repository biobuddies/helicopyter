"""Compose Cloudflare building blocks."""

from os import environ
from pathlib import Path
from urllib.parse import urlsplit

import helicopyter
from helicopyter import Block, data, resource, terraform


def jam(
    url: str, *, account_id: str = '', compatibility_date: str = '2026-08-28', zone_id: str = ''
) -> Block:
    """Route `site/` assets to a Worker named after the codename, with an `/api/` placeholder.

    The main workspace routes `url`, such as `rivertide.biobuddi.es/` or `cov.ing/covey/`; other
    workspaces route siblings, such as `rivertide-branch.biobuddi.es/`, or apex subdomains, such
    as `branch.cov.ing/covey/`. Foundational networking, which changes less often, owns the
    proxied DNS records, such as apex and `*` `100::`, that routes require.

    `staff@admin.cov.ing/` requires Access to `*.cov.ing`, which covers previews and production;
    wildcards skip apexes, so apexes stay public. Other users raise.

    Private repositories should pass literal IDs; public ones may fall back to environment
    variables for obscurity.
    """
    parts = urlsplit(url if '//' in url else f'//{url}')
    hostname = parts.hostname or ''
    first, _, parent = hostname.partition('.')
    # Wildcards cover subdomains but not apexes
    subdomain = '.' in parent
    if parts.username not in {None, 'staff'} or (parts.username and not subdomain):
        raise ValueError(f'Expected no user, or staff@ on a subdomain, not {url}')
    account_id = account_id or environ['CLOUDFLARE_ACCOUNT_ID']
    zone_id = zone_id or environ['CLOUDFLARE_ZONE_ID']
    label, apex = (f'{first}-', parent) if subdomain else ('', hostname)
    preview = '%s${%s}.%s' % (label, terraform.workspace, apex)

    # Routes only see proxied traffic
    wildcard = f'"*.{apex}"'
    names = f'["{hostname}", {wildcard}]' if subdomain else f'["{hostname}"]'
    data.cloudflare_dns_records.this(
        lifecycle=Block('lifecycle')(
            postcondition=Block('postcondition')(
                condition=Block(
                    f'anytrue([for record in self.result : contains({terraform.workspace} == "main"'
                    f' ? {names} : [{wildcard}], record.name)])'
                ),
                error_message=f'Proxied DNS record for {hostname} or its previews not found',
            )
        ),
        name={'endswith': apex},
        proxied=True,
        zone_id=zone_id,
    )

    staff = {}
    if parts.username:
        # Look up, never manage, Allowedflare-style wildcard Access with an allow policy, plus a
        # tunnel; bind the audience, so the Worker can validate Access JSON Web Tokens itself
        domain = f'*.{apex}'
        application = data.cloudflare_zero_trust_access_application.this(
            account_id=account_id,
            filter={'domain': domain, 'exact': True},
            lifecycle=Block('lifecycle')(
                postcondition=Block('postcondition')(
                    condition=Block(
                        'try(anytrue([for policy in self.policies : policy.decision == "allow"]),'
                        ' false)'
                    ),
                    error_message=f'Access application {domain} needs an allow policy',
                )
            ),
        )
        data.cloudflare_zero_trust_tunnel_cloudflared.this(
            account_id=account_id,
            filter={'is_deleted': False, 'name': apex},
            lifecycle=Block('lifecycle')(
                postcondition=Block('postcondition')(
                    condition=Block('self.id != null'), error_message=f'Tunnel {apex} not found'
                )
            ),
        )
        staff = {
            'bindings': [
                {'name': 'ALLOWEDFLARE_AUDIENCE', 'text': application.aud, 'type': 'plain_text'}
            ]
        }
    script = resource.cloudflare_workers_script.this(
        account_id=account_id,
        assets={
            'config': {
                # Misses load index.html, as client-side routers need; static sites don't care
                'not_found_handling': 'single-page-application',
                'run_worker_first': ['/api/*'],
            },
            'directory': '../../../site',
        },
        **staff,
        compatibility_date=compatibility_date,
        content=(Path(__file__).parent / 'worker.js').read_text(),
        main_module='worker.js',
        script_name='%s-${%s}' % (helicopyter.cona, terraform.workspace),
    )
    # Focus on the custom domain because workers.dev URLs might require additional Access
    # configuration or duplicate content from SEO perspective
    resource.cloudflare_workers_script_subdomain.this(
        account_id=account_id, enabled=False, previews_enabled=False, script_name=script.script_name
    )
    resource.cloudflare_workers_route.this(
        pattern=Block(
            f'{terraform.workspace} == "main" ? "{hostname}{parts.path}*"'
            f' : "{preview}{parts.path}*"'
        ),
        script=script.script_name,
        zone_id=zone_id,
    )
    return script
