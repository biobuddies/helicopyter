"""Test optional legacy CDKTF support."""

from textwrap import dedent

from pytest import importorskip, raises

cdktf = importorskip('cdktf')
NullResource = importorskip('cdktf_cdktf_provider_null.resource').Resource

from helicopyter.cdktf import HeliStack  # noqa: E402


def test_helistack() -> None:
    """An empty stack retains its codename and generates no HCL."""
    stack = HeliStack('foo')
    assert stack.cona == 'foo'
    assert stack.to_hcl_terraform()['hcl'] == ''


def test_override() -> None:
    stack = HeliStack('foo')
    stack.override(foo=True, bar=False)
    output = stack.to_terraform()
    assert output['foo']
    assert not output['bar']


def test_push_id() -> None:
    """Within a given Element such as the NullResource, the id_ must be unique."""
    stack = HeliStack('foo')
    my_first_null = stack.push(NullResource, 'bar')
    assert isinstance(my_first_null, NullResource)

    my_second_null = stack.push(NullResource, 'baz')
    assert isinstance(my_second_null, NullResource)

    assert (
        stack.to_hcl_terraform()['hcl'].strip()
        == dedent("""
        resource "null_resource" "bar" {
        }
        resource "null_resource" "baz" {
        }
    """).strip()
    )

    with raises(RuntimeError):
        stack.push(NullResource, 'bar')


def test_push_provider() -> None:
    """The same id_ must be allowed for different Elements."""
    stack = HeliStack('foo')
    stack.push(NullResource, 'bar')
    stack.push(cdktf.TerraformLocal, 'bar', 'bar')
    stack.push(cdktf.TerraformOutput, 'bar', value='bar')
    stack.push(cdktf.TerraformVariable, 'bar')
    assert (
        stack.to_hcl_terraform()['hcl'].strip()
        == dedent("""
        locals {
            bar = "bar"
        }
        resource "null_resource" "bar" {
        }

        output "bar" {
        value = "bar"
        }

        variable "bar" {

        }
    """).strip()
    )
