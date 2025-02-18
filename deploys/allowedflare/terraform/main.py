"""Codify Allowedflare infrastructure."""

from ast import literal_eval
from os import environ

from cdktf_cdktf_provider_cloudflare.zero_trust_access_application import ZeroTrustAccessApplication
from cdktf_cdktf_provider_cloudflare.zero_trust_access_identity_provider import ZeroTrustAccessIdentityProvider
from cdktf_cdktf_provider_cloudflare.zero_trust_access_policy import ZeroTrustAccessPolicy, ZeroTrustAccessPolicyInclude
from cdktf_cdktf_provider_cloudflare.worker_route import WorkerRoute

from stacks.base import BaseStack


def synth(stack: BaseStack) -> None:
    stack.provide('cloudflare')

    # If this was a private repository, I'd probably set these variables using string literals
    account_id = environ['CLOUDFLARE_ACCOUNT_ID']
    emails = literal_eval(environ['ALLOWEDFLARE_EMAILS'])
    private_domain = environ['ALLOWEDFLARE_PRIVATE_DOMAIN']
    zone_id = environ['CLOUDFLARE_ZONE_ID']

    stack.push(
        ZeroTrustAccessIdentityProvider,
        'this',
        account_id=account_id,
        name='One-time PIN',
        type='onetimepin',
    )

    application = stack.push(
        ZeroTrustAccessApplication,
        'this',
        domain=f'*.{private_domain}',
        session_duration='24h',
        skip_interstitial=True,
    )

    stack.push(
        ZeroTrustAccessPolicy,
        'email-in',
        name='email-in',
        application_id=application.id,
        decision='allow',
        precedence=1,
        include=[ZeroTrustAccessPolicyInclude(email=emails)],
    )

    stack.push(
        ZeroTrustAccessPolicy,
        'service-in',
        name='service-in',
        application_id=application.id,
        decision='non_identity',
        precedence=2,
        include=[ZeroTrustAccessPolicyInclude(any_valid_service_token=True)],
    )

    stack.push(
        WorkerRoute,
        'this',
        pattern=f'*.{private_domain}/x/*',
        script_name='allowedflare-proxy',
        zone_id=zone_id,
    )
