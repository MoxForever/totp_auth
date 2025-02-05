import os


def get_secret_key() -> str:
    key = os.environ.get("SECRET_KEY", None)
    if key is None:
        raise ValueError("SECRET_KEY not set")

    return key
