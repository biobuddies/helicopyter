"""Generate Hashicorp Configuration Language (HCL) or JSON from Python."""

from helicopyter import Parameters, multisynth

args = Parameters().parse_args()
multisynth(
    args.conas,
    change_directory=args.directory,
    format_with=args.format_with,
    hashicorp_configuration_language=args.hashicorp_configuration_language,
)
