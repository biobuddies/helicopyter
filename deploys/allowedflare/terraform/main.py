"""Codify Allowedflare infrastructure."""

from os import environ

from cdktf_cdktf_provider_cloudflare.workers_route import WorkersRoute
from cdktf_cdktf_provider_cloudflare.zero_trust_access_application import (
    ZeroTrustAccessApplication,
    ZeroTrustAccessApplicationPolicies,
)
from cdktf_cdktf_provider_cloudflare.zero_trust_access_identity_provider import (
    ZeroTrustAccessIdentityProvider,
    ZeroTrustAccessIdentityProviderConfigA,
)
from cdktf_cdktf_provider_cloudflare.zero_trust_access_policy import (
    ZeroTrustAccessPolicy,
    ZeroTrustAccessPolicyInclude,
    ZeroTrustAccessPolicyIncludeAnyValidServiceToken,
    ZeroTrustAccessPolicyIncludeEmail,
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
        config=ZeroTrustAccessIdentityProviderConfigA(),
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
            ZeroTrustAccessApplicationPolicies(
                id=stack.push(
                    ZeroTrustAccessPolicy,
                    'email-in',
                    account_id=account_id,
                    name='email-in',
                    decision='allow',
                    include=[
                        ZeroTrustAccessPolicyInclude(
                            email=ZeroTrustAccessPolicyIncludeEmail(email=email)
                        )
                    ],
                ).id,
                precedence=1,
            ),
            # includes=ZeroTrustAccessApplicationPoliciesInclude(
            #    email=ZeroTrustAccessApplicationPoliciesIncludeEmail(email=email),
            ZeroTrustAccessApplicationPolicies(
                id=stack.push(
                    ZeroTrustAccessPolicy,
                    'service-in',
                    account_id=account_id,
                    name='service-in',
                    decision='non_identity',
                    include=[
                        ZeroTrustAccessPolicyInclude(
                            any_valid_service_token=ZeroTrustAccessPolicyIncludeAnyValidServiceToken()
                        )
                    ],
                ).id,
                precedence=2,
            ),
        ],
    )

    stack.push(
        WorkersRoute,
        'this',
        pattern=f'*.{private_domain}/x/*',
        script='allowedflare-proxy',
        zone_id=zone_id,
    )
