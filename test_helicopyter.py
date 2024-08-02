"""Test the helicopyter module."""

from cdktf import TerraformLocal, TerraformOutput, TerraformVariable
from cdktf_cdktf_provider_null.resource import Resource as NullResource
from pytest import raises

from helicopyter import HeliStack


def test_helistack() -> None:
    """The class must instantiate and provide the cona attribute and provide and push methods."""
    stack = HeliStack('foo')
    assert stack.cona == 'foo'
    assert callable(stack.provide)
    assert callable(stack.push)


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
