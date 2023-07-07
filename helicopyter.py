from collections import defaultdict
from importlib import import_module
from json import dump
from pathlib import Path
from typing import Iterable, Type, Union

from cdktf import App, TerraformElement, TerraformLocal, TerraformOutput, TerraformStack, TerraformVariable
from constructs import Node
from tap import Tap


class HeliStack(TerraformStack):
    def __init__(self, deploy: str):
        self.resources: dict[str, dict[str, TerraformElement]] = defaultdict(dict)
        # Something is automatically creating outdir, which is cdktf.out by default
        super().__init__(App(outdir='.'), deploy)

    def _allocate_logical_id(self, element: Union[Node, TerraformElement]) -> str:
        if isinstance(element, Node):
            raise Exception('AWS CDK unsupported')
        return f'{element.__class__.__name__}-{element.node.id}'


def multisynth(deploys: Iterable[str]):
    if not deploys:
        print('No deployed specified. Doing nothing.')
        return

    if 'all' in deploys:
        python_files = (Path(__file__).parent / 'deploys').glob(f'**/terraform/main.py')
        deploys = ['demo']

    for deploy in deploys:
        module = import_module(f'deploys.{deploy}.terraform.main')
        stack = HeliStack(deploy)
        module.synth(stack)
        dictionaries = stack.to_terraform()
        dictionaries['//']['AUTOGENERATED'] = 'by helicopyter'
        with (Path(__file__).parent / 'deploys' / deploy / 'terraform/main.tf.json').open('w') as output:
            dump(dictionaries, output, indent=4, sort_keys=True)
            output.write('\n')


class Parameters(Tap):
    deploys: list[str]

    def configure(self):
        self.add_argument('deploys')


if __name__ == '__main__':
    args = Parameters().parse_args()
    multisynth(args.deploys)