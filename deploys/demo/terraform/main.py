from cdktf import TerraformVariable, TerraformLocal, TerraformOutput
from helicopyter import HeliStack


def synth(stack: HeliStack):
    image = TerraformVariable(stack, 'image', type='string')
    TerraformLocal(stack, 'environment', '${terraform.workspace}')
    TerraformOutput(stack, 'reference', value=image.to_string())
