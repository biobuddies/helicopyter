"""Register only the given services so the provider builds on a stock GitHub runner.

Usage: python -m trim provider.go service...

All 389 services need over 20 GB of Go build cache.
"""

import re
import sys
from pathlib import Path

path, *services = sys.argv[1:]
lines = Path(path).read_text().splitlines(keepends=True)
Path(path).write_text(
    ''.join(
        line
        for line in lines
        if not (
            match := re.match(
                r'\t"github.com/cloudflare/terraform-provider-cloudflare/internal/services/(\w+)"$'
                r'|\t\t(\w+)\.New\w*,( *// deprecated\.)?$',
                line.rstrip('\n'),
            )
        )
        or (match[1] or match[2]) in services
    )
)
