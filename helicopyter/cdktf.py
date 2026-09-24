"""Legacy CDKTF synthesis."""

from importlib import import_module
from os import environ
from typing import Any, TypeVar

from cdktf import App, TerraformElement, TerraformStack
from constructs import Construct, Node

environ['JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION'] = '1'


class HeliStack(TerraformStack):
    def __init__(self, cona: str) -> None:
        # Something is automatically creating outdir, which is cdktf.out by default
        super().__init__(App(outdir='.'), cona)

        self.cona = cona
        self._scopes: dict[str, Construct] = {}

    def _allocate_logical_id(self, tf_element: Node | TerraformElement) -> str:
        if isinstance(tf_element, Node):
            # Mostly for mypy. Patches to support AWS CDK welcome.
            raise TypeError('AWS CDK unsupported; please use CDKTF')  # pragma:no cover
        return tf_element.node.id

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
        return getattr(
            import_module(f'cdktf_cdktf_provider_{name}.provider'), f'{name.title()}Provider'
        )(self, 'this', **kwargs)

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

        print(f'Pushing {scope_name}.{id_}')  # noqa: T201
        return Element(self._scopes[scope_name], id_, *args, **kwargs)
