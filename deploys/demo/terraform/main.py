"""Demonstrate a simple HeliStack synth function using CDKTF constructs."""

from cdktf import LocalExecProvisioner, TerraformLocal, TerraformOutput, TerraformVariable
from cdktf_cdktf_provider_null.resource import Resource as NullResource

from helicopyter import HeliStack


def synth(stack: HeliStack) -> None:
    """
    Accept the GIt HAsh (GIHA) as a variable and output it.

    Also infer the ENVIronment (ENVI) from the workspace and echo it to standard output.
    """
    stack.push(TerraformLocal, 'cona', stack.cona)
    stack.push(TerraformLocal, 'envi', '${terraform.workspace}')

    stack.push(
        NullResource,
        'this',
        provisioners=[
            LocalExecProvisioner(
                command='echo $envi', environment={'envi': '${local.envi}'}, type='local-exec'
            )
        ],
    )
    giha = stack.push(TerraformVariable, 'giha', type='string')
    stack.push(TerraformOutput, 'giha', value=giha.to_string())
