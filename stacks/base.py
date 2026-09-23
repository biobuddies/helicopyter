"""Base stack with R2 backend."""

from typing import Any

from helicopyter import Block, provider, terraform


def provide(source: str, version: str, **kwargs: Any) -> Block:
    """Register R2/S3 backend and required provider blocks; return the provider block.

    R2 backend requires the following environment variables.

    AWS_ACCESS_KEY_ID     - R2 token
    AWS_SECRET_ACCESS_KEY - R2 secret
    AWS_ENDPOINT_URL_S3   - R2 location: https://ACCOUNT_ID.r2.cloudflarestorage.com
    """
    from helicopyter import cona

    terraform.backend('s3')(
        bucket='terraform',
        key=f'{cona}.tfstate',
        region='auto',
        workspace_key_prefix=cona,
        skip_credentials_validation='true',
        skip_metadata_api_check='true',
        skip_region_validation='true',
        skip_requesting_account_id='true',
        skip_s3_checksum='true',
        use_path_style='true',
    )
    name = source.rsplit('/', maxsplit=1)[-1]
    terraform.required_providers(**{name: {'source': source, 'version': version}})
    return getattr(provider, name)(**kwargs)
