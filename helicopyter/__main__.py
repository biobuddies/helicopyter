"""Generate Hashicorp Configuration Language (HCL) or JSON from Python."""

from sys import argv

from helicopyter import Parameters, multisynth
from helicopyter.cloudflare import fqdn

if argv[1:2] == ['fqdn']:
    print(fqdn(*argv[2:]))  # noqa: T201
else:
    args = Parameters().parse_args()
    multisynth(
        args.conas,
        change_directory=args.directory,
        format_with=args.format_with,
        hashicorp_configuration_language=args.hashicorp_configuration_language,
    )
