"""Demonstrate the pure-Python HCL syntax (no CDKTF)."""

from helicopyter import cona, local, resource, string, terraform, tlocals, variable

tlocals(cona=cona, envi=terraform.workspace)
resource.null_resource.this(triggers={'cona': local.cona, 'envi': local.envi})
variable.giha(type=string)
