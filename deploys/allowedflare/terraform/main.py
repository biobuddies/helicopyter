"""Codify Allowedflare infrastructure."""

from os import environ

from cdktf_cdktf_provider_cloudflare.workers_route import WorkersRoute
from cdktf_cdktf_provider_cloudflare.zero_trust_access_application import ZeroTrustAccessApplication
from cdktf_cdktf_provider_cloudflare.zero_trust_access_identity_provider import (
    ZeroTrustAccessIdentityProvider,
)
from cdktf_cdktf_provider_cloudflare.zero_trust_access_policy import (
    ZeroTrustAccessPolicy,
    ZeroTrustAccessPolicyInclude,
)

from stacks.base import BaseStack


def synth(stack: BaseStack) -> None:
    stack.provide('cloudflare')

    # If this was a private repository, I'd probably set these variables using string literals
    account_id = environ['CLOUDFLARE_ACCOUNT_ID']
    email = environ['ALLOWEDFLARE_EMAIL']
    private_domain = environ['ALLOWEDFLARE_PRIVATE_DOMAIN']
    zone_id = environ['CLOUDFLARE_ZONE_ID']

    stack.push(
        ZeroTrustAccessIdentityProvider,
        'this',
        account_id=account_id,
        name='One-time PIN',
        type='onetimepin',
    )

    stack.push(
        ZeroTrustAccessApplication,
        'this',
        domain=f'*.{private_domain}',
        session_duration='24h',
        skip_interstitial=True,
        policies=[
            stack.push(
                ZeroTrustAccessPolicy,
                'email-in',
                account_id=account_id,
                name='email-in',
                decision='allow',
                include=[ZeroTrustAccessPolicyInclude(email=[email])],
            ).id,
            stack.push(
                ZeroTrustAccessPolicy,
                'service-in',
                account_id=account_id,
                name='service-in',
                decision='non_identity',
                include=[ZeroTrustAccessPolicyInclude(any_valid_service_token=True)],
            ).id,
        ],
    )

    stack.push(
        WorkersRoute,
        'this',
        pattern=f'*.{private_domain}/x/*',
        script_name='allowedflare-proxy',  # script in v5
        zone_id=zone_id,
    )
