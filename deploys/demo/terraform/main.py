"""Demonstrate a simple HeliStack synth function."""

from cdktf import LocalExecProvisioner

from helicopyter import HeliStack


def synth(stack: HeliStack) -> None:
    """Output the Git hASH (GASH)."""
    NullResource = stack.load('null_resource')  # noqa: N806

    stack.Local('code', stack.code)
    stack.Local('envi', '${terraform.workspace}')

    NullResource(
        'main',
        provisioners=[
            LocalExecProvisioner(
                command='echo $ENVI', environment={'ENVI': '${local.envi}'}, type='local-exec'
            )
        ],
    )
    gash = stack.Variable('gash', type='string')
    stack.Output('gash', value=gash.to_string())
