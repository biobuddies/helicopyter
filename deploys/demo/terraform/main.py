"""Demonstrate Python Syntax for Terraform."""

from helicopyter import Block, cona, resource, string, terraform, tlocals, var, variable

tlocals(cona=cona, envi=terraform.workspace)

resource.null_resource.this(
    provisioner=Block('provisioner', 'local-exec')(
        command='echo $envi', environment={'envi': '${local.envi}'}
    )
)
variable.giha(type=string)
Block('output', 'giha')(value=var.giha)
