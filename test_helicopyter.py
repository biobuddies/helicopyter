"""Test the helicopyter module."""

from cdktf import TerraformLocal, TerraformOutput, TerraformVariable
from cdktf_cdktf_provider_null.resource import Resource as NullResource
from pytest import raises

from helicopyter import (
    HeliStack,
    Reference,
    data,
    local,
    number,
    provider,
    registry,
    resource,
    string,
    tbool,
    terraform,
    tlocals,
    var,
    variable,
)


def test_helistack() -> None:
    """The class must instantiate and provide the cona attribute and provide and push methods."""
    stack = HeliStack('foo')
    assert stack.cona == 'foo'
    assert callable(stack.provide)
    assert callable(stack.push)


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

    with raises(RuntimeError):
        stack.push(NullResource, 'bar')


def test_push_provider() -> None:
    """The same id_ must be allowed for different Elements."""
    stack = HeliStack('foo')
    stack.push(NullResource, 'bar')
    stack.push(TerraformLocal, 'bar', 'bar')
    stack.push(TerraformOutput, 'bar', value='bar')
    stack.push(TerraformVariable, 'bar')
    stack.to_terraform()


def test_ref_str() -> None:
    assert str(Reference('string')) == 'string'
    assert str(Reference('terraform').workspace) == 'terraform.workspace'
    assert str(local.cona) == 'local.cona'
    assert str(var.giha) == 'var.giha'
    assert str(string) == 'string'
    assert str(tbool) == 'bool'
    assert str(number) == 'number'


def test_block_str() -> None:
    assert str(resource.null_resource.this) == 'resource.null_resource.this'
    assert str(data.github_repository.helicopyter) == 'data.github_repository.helicopyter'


def test_compile_locals() -> None:
    tlocals(cona='demo', envi=terraform.workspace)
    hcl = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert hcl == 'locals {\n  cona = "demo"\n  envi = terraform.workspace\n}'


def test_compile_variable() -> None:
    variable.giha(type=string)
    hcl = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert hcl == 'variable "giha" {\n  type = string\n}'


def test_compile_resource_with_nested_dict() -> None:
    resource.null_resource.this(triggers={'cona': local.cona})
    hcl = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert hcl == (
        'resource "null_resource" "this" {\n  triggers = {\n    cona = local.cona\n  }\n}'
    )


def test_compile_data() -> None:
    data.github_repository.helicopyter(name='helicopyter')
    hcl = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert hcl == ('data "github_repository" "helicopyter" {\n  name = "helicopyter"\n}')


def test_compile_provider() -> None:
    provider.aws(region='us-east-1')
    hcl = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert hcl == 'provider "aws" {\n  region = "us-east-1"\n}'


def test_compile_multiple_blocks() -> None:
    tlocals(cona='demo')
    variable.giha(type=string)
    hcl = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert 'locals' in hcl
    assert 'variable "giha"' in hcl
    assert hcl.index('locals') < hcl.index('variable')


def test_clear_registry() -> None:
    tlocals(cona='demo')
    first = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert first != ''
    second = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert second == ''


def test_prototype_not_mutated() -> None:
    """Calling a builder must not mutate the prototype for subsequent calls."""
    resource.null_resource.first(name='a')
    resource.null_resource.second(name='b')
    hcl = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert '"first"' in hcl
    assert '"second"' in hcl
