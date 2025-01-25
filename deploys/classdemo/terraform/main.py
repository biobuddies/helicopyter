"""Demonstrate a synth function that uses a subclass of HeliStack."""

from cdktf import LocalExecProvisioner, TerraformLocal, TerraformOutput, TerraformVariable
from cdktf_cdktf_provider_null.resource import Resource as NullResource

from helicopyter import HeliStack


class NewStack(HeliStack):
    """Infer the ENVIronment (ENVI) from the workspace. Provide it and COdeNAme (CONA) as locals."""

    def __init__(self, cona: str) -> None:
        super().__init__(cona)
        self.push(TerraformLocal, 'cona', self.cona)
        self.push(TerraformLocal, 'envi', '${terraform.workspace}')
        self.push(
            NullResource,
            'this',
            provisioners=[
                LocalExecProvisioner(
                    command='echo $envi', environment={'envi': '${local.envi}'}, type='local-exec'
                )
            ],
        )
        giha = self.push(TerraformVariable, 'giha', type='string')
        self.push(TerraformOutput, 'giha', value=giha.to_string())


def synth(stack: NewStack) -> None:
    pass
