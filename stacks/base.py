"""Base stack with R2 backend."""

from cdktf import S3Backend

from helicopyter import HeliStack


class BaseStack(HeliStack):
    """
    R2 backend requires the following environment variables.

    AWS_ACCESS_KEY_ID     - R2 token
    AWS_SECRET_ACCESS_KEY - R2 secret
    #=AWS_ENDPOINT_URL_S3   - R2 location: https://ACCOUNT_ID.r2.cloudflarestorage.com
    """

    def __init__(self, cona: str) -> None:
        super().__init__(cona)
        S3Backend(
            self,
            bucket='terraform',
            # Just in case somebody uses the default environment for two different codenames
            key=f'{cona}.tfstate',
            region='auto',
            skip_credentials_validation=True,
            skip_metadata_api_check=True,
            skip_region_validation=True,
            skip_requesting_account_id=True,
            skip_s3_checksum=True,
            use_path_style=True,
            workspace_key_prefix=cona,
        )
