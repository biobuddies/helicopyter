"""Base stack with R2 backend."""

from cdktf import S3Backend

from helicopyter import HeliStack


class BaseStack(HeliStack):
    """
    R2 backend requires the following environment variables.

    AWS_ACCESS_KEY_ID     - R2 token
    AWS_SECRET_ACCESS_KEY - R2 secret
    AWS_ENDPOINT_URL_S3   - R2 location: https://ACCOUNT_ID.r2.cloudflarestorage.com
    """

    def __init__(self, cona: str) -> None:
        super().__init__(cona)
        # Organize state files as: {cona}/{envi}/{cona}.tfstate
        backend = S3Backend(
            self,
            bucket='terraform',
            # Just in case somebody uses the default environment for two different codenames
            key=f'{cona}.tfstate',
            region='auto',
            workspace_key_prefix=cona,
        )
        # Sadly `attribute=True` above was resulting in `attribute = undefined` in the HCL
        for attribute in (
            'skip_credentials_validation',
            'skip_metadata_api_check',
            'skip_region_validation',
            'skip_requesting_account_id',
            'skip_s3_checksum',
            'use_path_style',
        ):
            backend.add_override(attribute, 'true')
