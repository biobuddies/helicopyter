"""Generate Hashicorp Configuration Language (HCL) or JSON from Python."""

from collections.abc import Iterable
from importlib import import_module
from json import dumps
from pathlib import Path
from re import sub
from subprocess import check_output
from typing import Any, TypeVar

from cdk8s import Chart
from cdktf import App, TerraformElement, TerraformStack
from constructs import Construct, Node
from tap import Tap


class HeliChart(Chart):
    def __init__(self, cona: str) -> None:
        super().__init__(App(), cona)
        self.cona = cona


class HeliStack(TerraformStack):
    def __init__(self, cona: str) -> None:
        # Something is automatically creating outdir, which is cdktf.out by default
        super().__init__(App(outdir='.'), cona)

        self.cona = cona
        self._scopes: dict[str, Construct] = {}

    def _allocate_logical_id(self, element: Node | TerraformElement) -> str:
        if isinstance(element, Node):
            # Mostly for mypy. Patches to support AWS CDK welcome.
            raise TypeError('AWS CDK unsupported; please use CDKTF')
        return element.node.id

    def override(self, **kwargs: Any) -> None:
        """Call add_override for each keyword argument."""
        for key, value in kwargs.items():
            self.add_override(key, value)

    def provide(self, name: str, **kwargs: Any) -> type[TerraformElement]:
        """
        Return a Provider class instance given its short name.

        Example usage:
        stack.provide('github', owner='biobuddies')
        """
        module = import_module(f'cdktf_cdktf_provider_{name}.provider')
        return getattr(module, f'{name.title()}Provider')(self, 'this', **kwargs)

    E = TypeVar('E', bound=TerraformElement)

    def push(
        self,
        Element: type[E],  # noqa: N803
        id_: str,
        *args: Any,
        **kwargs: Any,
    ) -> E:
        """
        Return new instance of Element (data, local, output, resource, or variable).

        In contrast to running Element(...) standalone, the new instance will be named in the
        traditional Terraform style.

        Also assigns Element.__str__ to Element.to_string.

        Example usage:
        from cdktf_cdktf_provider_cloudflare.zero_trust_access_application import (
            ZeroTrustAccessApplication
        )
        stack.push(ZeroTrustAccessApplication, 'mydomain-wildcard', domain='*.mydomain.com')
        """
        # assignment: mypy thinks narrow type on one side and broad object type on the other are
        # incompatible
        # method-assign: mypy can't handle it https://github.com/python/mypy/issues/2427
        Element.__str__ = Element.to_string  # type: ignore[assignment,method-assign]

        if Element.__module__ == 'cdktf':
            scope_name = Element.__name__.lower().replace('terraform', '')
        else:
            scope_name = Element.__module__.replace('cdktf_cdktf_provider_', '').replace('.', '_')
        if scope_name not in self._scopes:
            self._scopes[scope_name] = Construct(self, scope_name)

        print(f'Pushing {scope_name}.{id_}')
        return Element(self._scopes[scope_name], id_, *args, **kwargs)


# ruff: noqa: T201
def multisynth(
    all_or_conas_or_paths: Iterable[str],
    *,
    change_directory: Path | None,
    hashicorp_configuration_language: bool,
    format_with: str,
) -> None:
    """Generate Hashicorp Configuration Language (HCL) or JSON."""
    if not all_or_conas_or_paths:
        print('No codenames specified. Doing nothing.')
        return

    top_directory = change_directory if change_directory else Path.cwd()

    if 'all' in all_or_conas_or_paths or 'helicopyter.py' in all_or_conas_or_paths:
        conas_or_paths = {
            file.parent.parent.name
            for file in (top_directory / 'deploys').glob('**/terraform/main.py')
        }
    else:
        conas_or_paths = set(all_or_conas_or_paths)

    for cona_or_path in conas_or_paths:
        path_to_check = Path(cona_or_path)
        if (
            path_to_check.exists()
            and path_to_check.name == 'main.py'
            and path_to_check.parent.name == 'terraform'
        ):
            cona = path_to_check.parent.parent.name
        else:
            cona = cona_or_path
        relative_path = (
            f'deploys/{cona}/terraform/main.tf{"" if hashicorp_configuration_language else ".json"}'
        )
        print(f'Generating {relative_path}')
        try:
            module_path = f'deploys.{cona}.terraform.main'
            main = import_module(module_path)
            stack = main.synth.__annotations__['stack'](cona)
            main.synth(stack)
        except (AttributeError, ImportError, KeyError, TypeError):
            python_file = module_path.replace('.', '/') + '.py'
            print(f'`def synth(stack: HeliStack):` appears to be missing from {python_file}')
            raise
        if hashicorp_configuration_language:
            unformatted = '# AUTOGENERATED by helicopyter\n\n' + stack.to_hcl_terraform()['hcl']
            autoformatted = check_output(  # noqa: S603
                [format_with, 'fmt', '-'], input=unformatted.encode()
            ).decode()
            formatted = sub(
                r'\n{3,}',
                '\n\n',
                autoformatted.replace('}\n\n\n}', '}\n}').replace('}\nresource', '}\n\nresource'),
            )
            (top_directory / relative_path).write_text(formatted.strip() + '\n')
        else:
            dictionary = stack.to_terraform()
            dictionary['//']['AUTOGENERATED'] = 'by helicopyter'
            (top_directory / relative_path).write_text(
                dumps(dictionary, indent=4, sort_keys=True) + '\n'
            )


class Parameters(Tap):
    conas: list[str]  # space-separated COdeNAmes
    directory: Path | None = None
    format_with: str = 'terraform'
    hashicorp_configuration_language: bool = True

    def configure(self) -> None:  # noqa: D102
        self.add_argument('conas')  # Positional argument
        self.add_argument('-C', '--directory')  # Like make and tar
