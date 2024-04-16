"""Test the helicopyter module."""

from json import loads
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from unittest import TestCase

import pytest
from cdktf_cdktf_provider_null.resource import Resource

from helicopyter import HeliStack, synth


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

    def test_end_to_end_against_hcl(self) -> None:
        commandline = [
            'terraform',
            'apply',
            '-auto-approve',
            '-input=false',
            '-var',
            'gash=0066cea3822cf77ecb41dddf29079b00108e17ac-dirty',
        ]
        print('covdebug')
        with TemporaryDirectory() as directory_string:
            directory = Path(directory_string)
            (directory / 'main.py').write_text(
                Path('deploys/helidemo/terraform/main.py').read_text()
            )
            synth('demo', directory, 'main.tf.json')

            heli_init = run(
                ['terraform', 'init', '-input=false'],
                capture_output=True,
                check=True,
                cwd=directory,
            )  # noqa: S603, S607
            print(heli_init.stdout.decode())
            print(heli_init.stderr.decode())
            heli_result = run(commandline, capture_output=True, check=True, cwd=directory)  # noqa: S603
            print(heli_result.stdout.decode())
            print(heli_result.stderr.decode())
            heli_state = loads((directory / 'terraform.tfstate').read_text())

        with TemporaryDirectory() as directory_string:
            directory = Path(directory_string)
            (directory / 'main.tf').write_text(
                Path('deploys/hcldemo/terraform/main.tf').read_text().replace('hcldemo', 'demo')
            )
            hcl_init = run(
                ['terraform', 'init', '-input=false'],
                capture_output=True,
                check=True,
                cwd=directory,
            )  # noqa: S603, S607
            print(hcl_init.stdout.decode())
            print(hcl_init.stderr.decode())
            hcl_result = run(commandline, capture_output=True, check=True, cwd=directory)  # noqa: S603
            print(hcl_result.stdout.decode())
            print(hcl_result.stderr.decode())
            assert hcl_result.returncode == 0
            hcl_state = loads((directory / 'terraform.tfstate').read_text())

        assert heli_state == hcl_state
