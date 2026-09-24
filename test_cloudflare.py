"""Test Cloudflare building blocks."""

from collections.abc import Callable

from pytest import MonkeyPatch, fixture, mark, raises

import helicopyter
from helicopyter import Block, registry
from helicopyter.cloudflare import jam


@fixture
def render(monkeypatch: MonkeyPatch) -> Callable[[str], dict[str, str]]:
    """Call jam for codename `site`; return top-level blocks keyed by address."""
    monkeypatch.setattr(helicopyter, 'cona', 'site')

    def inner(url: str) -> dict[str, str]:
        jam(url, account_id='account', zone_id='zone')
        children = {
            id(value)
            for block in registry
            for value in block.attributes.values()
            if isinstance(value, Block) and value.attributes
        }
        blocks = {str(block): block.to_hcl() for block in registry if id(block) not in children}
        registry.clear()
        return blocks

    return inner


def test_jam_sibling_preview(render: Callable[[str], dict[str, str]]) -> None:
    """Like rivertide: previews as siblings; DNS belongs to foundational networking."""
    blocks = render('rivertide.biobuddi.es/')
    assert sorted(blocks) == [
        'cloudflare_workers_route.this',
        'cloudflare_workers_script.this',
        'cloudflare_workers_script_subdomain.this',
        'data.cloudflare_dns_records.this',
    ]
    assert (
        '"main" ? ["rivertide.biobuddi.es", "*.biobuddi.es"] : ["*.biobuddi.es"]'
        in blocks['data.cloudflare_dns_records.this']
    )
    assert (
        'pattern = terraform.workspace == "main" ? "rivertide.biobuddi.es/*"'
        ' : "rivertide-${terraform.workspace}.biobuddi.es/*"'
    ) in blocks['cloudflare_workers_route.this']
    assert 'script_name = "site-${terraform.workspace}"' in blocks['cloudflare_workers_script.this']
    assert 'bindings' not in blocks['cloudflare_workers_script.this']
    assert (
        'not_found_handling = "single-page-application"' in blocks['cloudflare_workers_script.this']
    )
    assert 'run_worker_first = ["/api/*"]' in blocks['cloudflare_workers_script.this']


def test_jam_apex_preview(render: Callable[[str], dict[str, str]]) -> None:
    """Like covicovey: previews under the apex, with or without a scheme; wildcards skip apexes."""
    blocks = render('https://cov.ing/covey/')
    assert '"${terraform.workspace}.cov.ing/covey/*"' in blocks['cloudflare_workers_route.this']
    assert '"main" ? ["cov.ing"] : ["*.cov.ing"]' in blocks['data.cloudflare_dns_records.this']


def test_jam_staff(render: Callable[[str], dict[str, str]]) -> None:
    """Look up, never manage, wildcard Access to previews and production, plus a tunnel."""
    blocks = render('staff@admin.cov.ing/')
    assert 'domain = "*.cov.ing"' in blocks['data.cloudflare_zero_trust_access_application.this']
    assert 'name = "cov.ing"' in blocks['data.cloudflare_zero_trust_tunnel_cloudflared.this']
    assert not any('zero_trust' in address for address in blocks if not address.startswith('data'))
    assert (
        'text = data.cloudflare_zero_trust_access_application.this.aud'
        in (blocks['cloudflare_workers_script.this'])
    )
    assert '"admin-${terraform.workspace}.cov.ing/*"' in blocks['cloudflare_workers_route.this']


@mark.parametrize('url', ('admin@rivertide.biobuddi.es/', 'staff@cov.ing/admin/'))
def test_jam_rejects(render: Callable[[str], dict[str, str]], url: str) -> None:
    """Other users raise, as does staff@ on an apex, which wildcard Access skips."""
    with raises(ValueError, match=url):
        render(url)
