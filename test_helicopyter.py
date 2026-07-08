"""Test the helicopyter module."""

from pathlib import Path
from sys import modules

from cdktf import TerraformLocal, TerraformOutput, TerraformVariable
from cdktf_cdktf_provider_null.resource import Resource as NullResource
from pytest import MonkeyPatch, raises

from helicopyter import (
    Block,
    HeliStack,
    data,
    local,
    multisynth,
    number,
    provider,
    quote,
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
    assert str(Block('string')) == 'string'
    assert str(Block('terraform').workspace) == 'terraform.workspace'
    assert str(local.cona) == 'local.cona'
    assert str(var.giha) == 'var.giha'
    assert str(string) == 'string'
    assert str(tbool) == 'bool'
    assert str(number) == 'number'


def test_block_str() -> None:
    assert str(resource.null_resource.this) == 'null_resource.this'
    assert str(resource.null_resource.this.id) == 'null_resource.this.id'
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


def test_compile_nested_block() -> None:
    """Block values in attrs render as nested blocks without = sign."""
    s3 = Block('backend', 's3')
    s3.attributes = {'bucket': 'terraform', 'key': 'test.tfstate', 'region': 'auto'}
    terraform(backend=s3)
    hcl = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert 'terraform {' in hcl
    assert '  backend "s3" {' in hcl
    assert '    bucket = "terraform"' in hcl
    assert '    key = "test.tfstate"' in hcl


def test_terraform_nested_blocks_via_parent() -> None:
    """Pre-assigned children auto-attach via parent when called."""
    terraform.backend('s3')(bucket='terraform', key='foundation.tfstate', region='auto')
    terraform.required_providers(github={'source': 'integrations/github', 'version': '6.6.0'})
    hcl = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert 'terraform {' in hcl
    assert '  backend "s3" {' in hcl
    assert '    bucket = "terraform"' in hcl
    assert '    key = "foundation.tfstate"' in hcl
    assert '  required_providers {' in hcl
    assert '    github = {' in hcl
    assert 'source = "integrations/github"' in hcl
    assert 'version = "6.6.0"' in hcl


def test_provider_github() -> None:
    provider.github(owner='biobuddies')
    hcl = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert hcl == 'provider "github" {\n  owner = "biobuddies"\n}'


def test_resource_label_chain() -> None:
    """Labels-only __call__ creates child without mutating prototype."""
    resource.github_repository('repo1')(name='repo1', description='First repo')
    resource.github_repository('repo2')(name='repo2', description='Second repo')
    hcl = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert '"repo1"' in hcl
    assert '"repo2"' in hcl
    assert 'name = "repo1"' in hcl
    assert 'name = "repo2"' in hcl


def test_multisynth_filters_children() -> None:
    """Blocks that are attr values in other blocks only render nested."""
    terraform.backend('s3')(bucket='tf', key='cona.tfstate', region='auto')
    terraform.required_providers(github={'source': 'integrations/github', 'version': '~> 6.0'})
    children = {
        id(value)
        for block in registry
        for value in block.attributes.values()
        if isinstance(value, Block) and value.attributes
    }
    top_level = [b for b in registry if id(b) not in children]
    hcl = '\n\n'.join(b.to_hcl() for b in top_level)
    registry.clear()
    assert hcl.startswith('terraform {')
    assert hcl.count('backend "s3" {') == 1
    assert hcl.count('required_providers {') == 1
    assert '  backend "s3" {' in hcl
    assert '  required_providers {' in hcl


def test_multisynth_isolates_deploys(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Each deploy's terraform block must render in its own call order, not a predecessor's."""
    registry.clear()
    terraform.attributes.clear()
    for cona, body in {
        'aaa': (
            'from helicopyter import terraform\n'
            "terraform.required_providers(github={'source': 'integrations/github'})\n"
            "terraform.backend('s3')(bucket='tf', key='aaa.tfstate')\n"
        ),
        'bbb': (
            'from helicopyter import terraform\n'
            "terraform.backend('s3')(bucket='tf', key='bbb.tfstate')\n"
            "terraform.required_providers(github={'source': 'integrations/github'})\n"
        ),
    }.items():
        (tmp_path / 'deploys' / cona / 'terraform').mkdir(parents=True)
        (tmp_path / 'deploys' / cona / 'terraform' / 'main.py').write_text(body)
    (tmp_path / 'deploys' / '__init__.py').write_text('')
    passthrough = tmp_path / 'fmt-passthrough'
    passthrough.write_text('#!/bin/sh\ncat\n')
    passthrough.chmod(0o755)
    monkeypatch.syspath_prepend(tmp_path)
    monkeypatch.delitem(modules, 'deploys', raising=False)
    multisynth(
        ['aaa', 'bbb'],
        change_directory=tmp_path,
        hashicorp_configuration_language=True,
        format_with=str(passthrough),
    )
    for name in [module for module in modules if module.startswith('deploys')]:
        del modules[name]
    assert (tmp_path / 'deploys' / 'aaa' / 'terraform' / 'main.tf').read_text() == (
        '# AUTOGENERATED by helicopyter\n'
        '\n'
        'terraform {\n'
        '  required_providers {\n'
        '    github = {\n'
        '      source = "integrations/github"\n'
        '    }\n'
        '  }\n'
        '  backend "s3" {\n'
        '    bucket = "tf"\n'
        '    key = "aaa.tfstate"\n'
        '  }\n'
        '}\n'
    )
    assert (tmp_path / 'deploys' / 'bbb' / 'terraform' / 'main.tf').read_text() == (
        '# AUTOGENERATED by helicopyter\n'
        '\n'
        'terraform {\n'
        '  backend "s3" {\n'
        '    bucket = "tf"\n'
        '    key = "bbb.tfstate"\n'
        '  }\n'
        '  required_providers {\n'
        '    github = {\n'
        '      source = "integrations/github"\n'
        '    }\n'
        '  }\n'
        '}\n'
    )


def test_boolean_unquoted() -> None:
    assert quote(True) == 'true'  # noqa: FBT003
    assert quote(False) == 'false'  # noqa: FBT003


def test_list_quoting() -> None:
    assert quote(['a', 'b', 3]) == '["a", "b", "3"]'


def test_labels_plus_kwargs() -> None:
    """__call__ with both labels and kwargs mutates self in place."""
    block = terraform.backend('s3')(bucket='tf', key='x.tfstate')
    registry.clear()
    assert block.kind == 'backend'
    assert block.labels == ('s3',)
    assert block.attributes == {'bucket': 'tf', 'key': 'x.tfstate'}


def test_empty_attrs_block() -> None:
    empty = Block('empty')
    empty()
    registry.clear()
    assert empty.to_hcl() == 'empty {}'


def test_list_attribute_in_block() -> None:
    variable('myvar')(kind='list', default=['a', 'b', 'c'])
    hcl = '\n\n'.join(block.to_hcl() for block in registry)
    registry.clear()
    assert '["a", "b", "c"]' in hcl


def test_labels_and_kwargs_in_one_call() -> None:
    """Single __call__ with labels+kwargs mutates labels and attributes together."""
    blk = Block('thing')
    blk('mylabel', key='value')
    registry.clear()
    assert blk.labels == ('mylabel',)
    assert blk.attributes == {'key': 'value'}
