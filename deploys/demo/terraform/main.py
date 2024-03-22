"""Demonstrate a simple HeliStack synth function using CDKTF constructs."""

from cdktf import LocalExecProvisioner

from helicopyter import HeliStack


def synth(stack: HeliStack) -> None:
    """
    Accept the Git hASH (GASH) as a variable and output it.

    Also infer the ENVIronment (ENVI) from the workspace and echo it to standard output.
    """
    NullResource = stack.load('null_resource')  # noqa: N806

    stack.Local('cona', stack.cona)
    stack.Local('envi', '${terraform.workspace}')

    NullResource(
        'main',
        provisioners=[
            LocalExecProvisioner(
                command='echo $envi', environment={'envi': '${local.envi}'}, type='local-exec'
            )
        ],
    )
    gash = stack.Variable('gash', type='string')
    stack.Output('gash', value=gash.to_string())
