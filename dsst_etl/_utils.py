from .config import config


def get_compute_context_id():
    return hash(f"{config.HOSTNAME}_{config.USERNAME}")


def get_bucket_name():
    bucket_name = config.S3_BUCKET_NAME
    if not bucket_name:
        raise ValueError("S3_BUCKET_NAME environment variable is not set")
    return bucket_name
