"""Test the helicopyter module."""

from unittest import TestCase

import pytest
from cdktf_cdktf_provider_null.resource import Resource

from helicopyter import HeliStack


class TestHeliStack(TestCase):
    def test_load(self) -> None:
        """Multiple calls should work if and only if the id_ string is unique."""
        stack = HeliStack('foo')
        NullResource = stack.load('null_resource')  # noqa: N806
        my_first_null = NullResource('bar')
        assert isinstance(my_first_null, Resource)

        my_second_null = NullResource('baz')
        assert isinstance(my_second_null, Resource)

        with pytest.raises(RuntimeError):
            NullResource('bar')

        with pytest.raises(RuntimeError):
            stack.push(Resource, 'bar')

    def test_push(self) -> None:
        """Multiple calls should work if and only if the id_ string is unique."""
        stack = HeliStack('foo')
        my_first_null = stack.push(Resource, 'bar')
        assert isinstance(my_first_null, Resource)

        my_second_null = stack.push(Resource, 'baz')
        assert isinstance(my_second_null, Resource)

        with pytest.raises(RuntimeError):
            stack.push(Resource, 'bar')

        with pytest.raises(RuntimeError):
            stack.load('null_resource')('bar')
