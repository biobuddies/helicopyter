from functools import partial
from importlib import import_module
from json import dump
from pathlib import Path
from typing import Callable, Iterable, Type, Union

from cdktf import App, TerraformElement, TerraformLocal, TerraformOutput, TerraformStack, TerraformVariable
from constructs import Construct, Node
from tap import Tap


class HeliStack(TerraformStack):
    def __init__(self, codename: str):
        self.codename = codename
        # Something is automatically creating outdir, which is cdktf.out by default
        super().__init__(App(outdir='.'), codename)
        self.Local = partial(TerraformLocal, Construct(self, 'local'))
        self.Output = partial(TerraformOutput, Construct(self, 'output'))
        self.Variable = partial(TerraformVariable, Construct(self, 'variable'))

    def _allocate_logical_id(self, element: Union[Node, TerraformElement]) -> str:
        if isinstance(element, Node):
            raise Exception('AWS CDK unsupported')
        return element.node.id

    def load_path(self, path: str, element: str) -> Callable[..., Type[TerraformElement]]:
        """
        Example usage:
            stack.load_path('cdktf_cdktf_provider_null.resource', 'Resource')
        """
        module = import_module(path)
        element_class = getattr(module, element)
        if issubclass(element_class, TerraformElement):
            return partial(element_class, Construct(self, module.__name__))
        raise Exception(f'{element} is not a TerraformElement')

    def load(self, label: str) -> Callable[..., Type[TerraformElement]]:
        """
        Example usage:
            stack.load('null_resource')
        """
        infix, _, element = label.rpartition('_')
        snake_case_element = ''.join(
            [element[0].lower(), *('_' + c.lower() if c.isupper() else c for c in element[1:])]
        )
        return self.load_path(f'cdktf_cdktf_provider_{infix}.{snake_case_element}', element[0].upper() + element[1:])


def multisynth(codenames: Iterable[str]):
    if not codenames:
        print('No codename specified. Doing nothing.')
        return

    if 'all' in codenames:
        codenames = {
            file.parent.parent.name for file in (Path(__file__).parent / 'deploys').glob('**/terraform/main.py')
        }

    for codename in codenames:
        path_to_check = Path(codename)
        if path_to_check.exists() and path_to_check.name == 'main.py' and path_to_check.parent.name == 'terraform':
            codename = path_to_check.parent.parent.name
        relative_path = f'deploys/{codename}/terraform/main.tf.json'
        print(f'Generating {relative_path}')
        module = import_module(f'deploys.{codename}.terraform.main')
        stack = HeliStack(codename)
        module.synth(stack)
        dictionary = stack.to_terraform()
        dictionary['//']['AUTOGENERATED'] = 'by helicopyter'
        with (Path(__file__).parent / relative_path).open('w') as output:
            dump(dictionary, output, indent=4, sort_keys=True)
            output.write('\n')


class Parameters(Tap):
    codenames: list[str]

    def configure(self):
        self.add_argument('codenames')


if __name__ == '__main__':
    args = Parameters().parse_args()
    multisynth(args.codenames)
