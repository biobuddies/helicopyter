"""Codify Allowedflare infrastructure."""

from os import environ

from helicopyter import Block, cona, provider, resource, terraform
from stacks.base import r2_backend

# If this was a private repository, I'd probably set these variables using string literals
account_id = environ['CLOUDFLARE_ACCOUNT_ID']
email = environ['ALLOWEDFLARE_EMAIL']
private_domain = environ['ALLOWEDFLARE_PRIVATE_DOMAIN']
zone_id = environ['CLOUDFLARE_ZONE_ID']

terraform.required_providers(
    cloudflare={'source': 'cloudflare/cloudflare', 'version': '4.52.0'},
)
r2_backend(cona, terraform)
provider.cloudflare()

resource.cloudflare_zero_trust_access_identity_provider('this')(
    account_id=account_id,
    name='One-time PIN',
    type='onetimepin',
)

email_policy = resource.cloudflare_zero_trust_access_policy('email-in')(
    account_id=account_id,
    decision='allow',
    include=Block('include')(email=[email]),
    name='email-in',
)

service_policy = resource.cloudflare_zero_trust_access_policy('service-in')(
    account_id=account_id,
    decision='non_identity',
    include=Block('include')(any_valid_service_token=True),
    name='service-in',
)

resource.cloudflare_zero_trust_access_application('this')(
    domain=f'*.{private_domain}',
    policies=[
        '${cloudflare_zero_trust_access_policy.email-in.id}',
        '${cloudflare_zero_trust_access_policy.service-in.id}',
    ],
    session_duration='24h',
    skip_interstitial=True,
)

resource.cloudflare_workers_route('this')(
    pattern=f'*.{private_domain}/x/*',
    script_name='allowedflare-proxy',
    zone_id=zone_id,
)
