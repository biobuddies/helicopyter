from cdktf import LocalExecProvisioner
from helicopyter import HeliStack


def synth(stack: HeliStack):
    NullResource = stack.load('null_resource')

    stack.Local('codename', stack.codename)
    stack.Local('environs', '${terraform.workspace}')

    NullResource(
        'main',
        provisioners=[
            LocalExecProvisioner(
                command='echo $ENVI', environment={'ENVI': '${local.envi}'}, type='local-exec'
            )
        ],
    )
    hash_ = stack.Variable('hash', type='string')
    stack.Output('hash', value=hash_.to_string())
