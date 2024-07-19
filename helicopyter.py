"""Generate JSON which Terraform can use from Python."""

from collections.abc import Callable, Iterable
from functools import partial
from importlib import import_module
from json import dump
from pathlib import Path
from typing import Any, TypeVar

from cdktf import (
    App,
    TerraformElement,
    TerraformLocal,
    TerraformOutput,
    TerraformStack,
    TerraformVariable,
)
from constructs import Construct, Node
from tap import Tap


class HeliStack(TerraformStack):
    def __init__(self, cona: str) -> None:
        # Something is automatically creating outdir, which is cdktf.out by default
        super().__init__(App(outdir='.'), cona)

        self.Local = partial(TerraformLocal, Construct(self, 'local'))
        self.Output = partial(TerraformOutput, Construct(self, 'output'))
        self.Variable = partial(TerraformVariable, Construct(self, 'variable'))
        self.cona = cona
        self.imports: dict[str, str] = {}  # {to: id}
        self._scopes: dict[str, Construct] = {}

    def _allocate_logical_id(self, element: Node | TerraformElement) -> str:
        if isinstance(element, Node):
            # Mostly for mypy. Patches to support AWS CDK welcome.
            raise TypeError('AWS CDK unsupported; please use CDKTF')
        return element.node.id

    def scopes(self, module_name: str) -> Construct:
        """Get or create a Construct for module_name for scoping purposes."""
        if module_name not in self._scopes:
            self._scopes[module_name] = Construct(self, module_name)
        return self._scopes[module_name]

    def load(self, label: str) -> Callable[..., type[TerraformElement]]:
        """
        Return a Data or Resource class given a substring of the module/package name.

        Example usage:
        AccessApplication = stack.load('cloudflare_access_application')

        In contrast to HeliStack.push, this method is more concise but obscures type annotations.
        """
        provider, _, snake_case_element = label.partition('_')
        module = import_module(f'cdktf_cdktf_provider_{provider}.{snake_case_element}')
        if snake_case_element == 'provider':
            camel_case_element = f'{provider.title()}Provider'
        else:
            camel_case_element = ''.join(part.title() for part in snake_case_element.split('_'))
        element_class = getattr(module, camel_case_element)
        if issubclass(element_class, TerraformElement):
            print(f'Loading {module.__name__}')
            return partial(element_class, self.scopes(module.__name__))
        raise Exception(f'{camel_case_element} is not a TerraformElement')

    def provide(self, name: str) -> type[TerraformElement]:
        """
        Return a Provider class instance given its short name.

        Example usage:
        stack.provide('cloudflare')
        """
        module = import_module(f'cdktf_cdktf_provider_{name}.provider')
        return getattr(module, f'{name.title()}Provider')(self, 'this')

    E = TypeVar('E', bound=TerraformElement)

    def push(
        self,
        Element: type[E],  # noqa: N803
        id_: str,
        *args: Any,  # noqa: ANN401
        import_id: str = '',
        **kwargs: Any,  # noqa: ANN401
    ) -> E:
        """
        Add Data or a Resource to the stack and return it.

        Example usage:
        from cdktf_cdktf_provider_cloudflare.access_application import AccessApplication
        stack.push(AccessApplication, 'mydomain-wildcard', domain='*.mydomain.com')

        In contrast to HeliStack.load, this method preserves type annotations at the cost of
        verbose imports.
        """
        print(f'Pushing {id_} to {Element.__module__}')
        element = Element(self.scopes(Element.__module__), id_, *args, **kwargs)
        if import_id:
            self.imports[
                f"{Element.__module__.replace('cdktf_cdktf_provider_', '').replace('.', '_')}.{id_}"
            ] = import_id
        return element


# ruff: noqa: T201
def multisynth(all_or_conas_or_paths: Iterable[str]) -> None:
    if not all_or_conas_or_paths:
        print('No codenames specified. Doing nothing.')
        return

    if 'all' in all_or_conas_or_paths or 'helicopyter.py' in all_or_conas_or_paths:
        conas_or_paths = {
            file.parent.parent.name
            for file in (Path(__file__).parent / 'deploys').glob('**/terraform/main.py')
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
        relative_path = f'deploys/{cona}/terraform/main.tf.json'
        print(f'Generating {relative_path}')
        module = import_module(f'deploys.{cona}.terraform.main')
        stack = HeliStack(cona)
        module.synth(stack)
        dictionary = stack.to_terraform()
        dictionary['//']['AUTOGENERATED'] = 'by helicopyter'
        if stack.imports:
            dictionary['import'] = [
                {'to': resource, 'id': import_id} for resource, import_id in stack.imports.items()
            ]
        with (Path(__file__).parent / relative_path).open('w') as output:
            dump(dictionary, output, indent=4, sort_keys=True)
            output.write('\n')


class Parameters(Tap):
    conas: list[str]

    def configure(self) -> None:  # noqa: D102
        self.add_argument('conas', help='COdeNAmes')


if __name__ == '__main__':
    args = Parameters().parse_args()
    multisynth(args.conas)
