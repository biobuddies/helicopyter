"""Generate Python from Terraform JSON."""

from functools import partial
from json import loads
from logging import getLogger
from pathlib import Path
from re import compile
from subprocess import run
from tempfile import TemporaryDirectory
from textwrap import dedent, fill, indent

from tap import Tap

logger = getLogger(__name__)


class Parameters(Tap):
    def configure(self) -> None:
        pass


def python_type(json: list | str) -> str:
    if isinstance(json, list):
        if json[0] == 'object':
            output = "TypedDict(\n        'Something',\n        {\n            "
            output += ',\n            '.join(
                [python_parameter(json, quote=True) for key, value in json[1].items()]
            )
            output += '\n        }\n    )'
            return output
        nested_type = json[1:]
        if len(nested_type) == 1:
            nested_type = nested_type[0]
        return f'{python_type(json[0])}[{python_type(nested_type)}]'
    return (
        json.replace('dynamic', 'Any')
        .replace('map', 'dict')
        .replace('number', 'float')
        .replace('string', 'str')
    )


rename_string = partial(compile(r'^str$').sub, 'string')


def python_parameter(signature: dict, *, comma: bool = False, quote: bool = False) -> str:
    converted_type = python_type(signature['type'])
    description = signature.get('description', '')

    if signature.get('computed'):
        return dedent(
            f'''
            @property
            def {signature["name"]}(self) -> {converted_type}:
                {f'"""{description}"""' if description else 'pass'}
            '''
        )

    if signature.get('optional'):
        converted_type += f' | None = {signature.get("default")}'

    # TODO is_nullable
    renamed_name = rename_string(signature['name'])
    comment_prefix = '#: '
    comments = fill(
        signature.get('description', ''),
        width=100 - len(comment_prefix),
        initial_indent=comment_prefix,
        subsequent_indent=comment_prefix,
    )
    return (
        (f'{comments}\n' if comments else '')
        + (f"'{renamed_name}'" if quote else renamed_name)
        + ': '
        + converted_type
        + (',' if comma else '')
        + ('\n' if comments else '')
    )


def required_optional_computed(item: tuple[str, dict]) -> int:
    if item[1].get('computed'):
        return 2
    if item[1].get('optional'):
        return 1
    return 0


def built_in_functions() -> None:
    if functions_json := run(
        ['terraform', 'metadata', 'functions', '-json'],  # noqa: S603
        capture_output=True,
        check=False,
    ).stdout:
        functions = loads(functions_json)
        output = 'from typing import Any\n\n'
        for function, signature in functions.get('function_signatures', {}).items():
            lowercase_description = signature['description'].replace(f'`{function}` ', '')
            parameter_list = [
                python_parameter(parameter, comma=True)
                for parameter in signature.get('parameters', [])
            ]
            multiline = any('\n' in parameter for parameter in parameter_list)
            if multiline:
                parameters = '\n' + indent('\n'.join(parameter_list), '    ')
            else:
                parameters = (' '.join(parameter_list))[:-1]
            output += (
                f'\ndef {function.replace("try", "try_")}({parameters}) -> '
                + python_type(signature['return_type'])
                + ':\n    """\n'
                + fill(
                    lowercase_description[0].upper() + lowercase_description[1:],
                    width=100,
                    initial_indent='    ',
                    subsequent_indent='    ',
                )
                + '\n    """\n    pass\n\n'
            )
        (Path(__file__).parent / 'providers' / 'functions.py').write_text(output)
        del functions['format_version']
        del functions['function_signatures']
        if functions:
            logger.warning(f'Unprocessed functions: {functions}')  # noqa: G004


def provider(fully_qualified_provider: str, version: str) -> None:
    short_provider = fully_qualified_provider.split('/')[-1]
    with TemporaryDirectory() as directory:
        (Path(directory) / 'main.tf').write_text(
            dedent(
                """
                terraform {
                    required_providers {
                        %s = {
                            source  = "%s"
                            version = "%s"
                        }
                    }
                }
                """  # noqa: UP031
                % (short_provider, fully_qualified_provider, version)
            )
        )
        run(['terraform', 'init'], capture_output=True, check=True, cwd=directory)  # noqa: S603
        if schema_json := run(
            ['terraform', 'providers', 'schema', '-json'],  # noqa: S603
            capture_output=True,
            cwd=directory,
            check=False,
        ).stdout:
            schema = loads(schema_json)
            output = dedent(
                """
                from dataclasses import dataclass
                from functools import partial
                from typing import ClassVar, TypedDict


                class Registry:
                    def __init__(self, cls):
                        self.cls = cls
                        self.instances: dict[str, cls] = {}

                    def __getattr__(self, name):
                        if name in self.instances:
                            return self.instances[name]
                        return partial(self.cls, self, name)

                    def __str__(self):
                        return self.cls._str


                registries: dict[str, Registry] = {}


                @dataclass
                class RegisteredDataclass:
                    _str: ClassVar[str]
                    _registry: Registry
                    _name: str

                    def __post_init__(self):
                        print(f'initializing {self._registry}.{self._name}')
                        #registries[]
                        self._registry.instances[self._name] = self


                """
            )
            for provider, resources in schema['provider_schemas'].items():
                for snake_case_resource, schema in resources['resource_schemas'].items():
                    if snake_case_resource != 'cloudflare_record':
                        continue
                    from json import dumps

                    camel_case_resource = ''.join(
                        [word.title() for word in snake_case_resource.split('_')]
                    )
                    attributes = [
                        python_parameter({'name': attribute, **signature})
                        for attribute, signature in sorted(
                            schema['block']['attributes'].items(), key=required_optional_computed
                        )
                    ]
                    output += dedent(
                        f'''
                        @dataclass
                        class {camel_case_resource}(RegisteredDataclass):
                            """{schema['block']['description']}"""\n
                            _str: ClassVar[str] = '{snake_case_resource}'
                            _registry: Registry
                            _name: str

                        '''
                    )
                    output += indent('\n'.join(attributes), '    ')
                    output += f'\n\n\n{snake_case_resource} = Registry({camel_case_resource})\n'
                    del schema['version']
                    del schema['block']['attributes']
                    del schema['block']['description']
                    del schema['block']['description_kind']
                    # TODO block_types
                    if schema:
                        logger.warning(f'Unprocessed schema: {dumps(schema, indent=4)}')  # noqa: G004
                (Path(__file__).parent / 'providers' / f'{provider.split("/")[-1]}.py').write_text(
                    output[1:]
                )


if __name__ == '__main__':
    args = Parameters().parse_args()

    built_in_functions()

    provider('cloudflare/cloudflare', '4.0')

    """
    terraform version -json > versions.json
    """
