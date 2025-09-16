from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MinioMediaStorage(S3Boto3Storage):
    """Custom storage for MinIO media objects.

    We intentionally override url() to return a relative /media/ path so that
    Nginx can proxy those requests internally to MinIO. This keeps external
    URLs stable and lets us hide the MinIO endpoint from clients.
    """
    default_acl = "public-read"
    file_overwrite = False

    def __init__(self, *args, **kwargs):  # noqa: D401
        kwargs.setdefault("bucket_name", settings.STORAGES["default"].get("OPTIONS", {}).get("bucket_name"))
        # Ensure we use path style if requested
        if settings.STORAGES["default"].get("OPTIONS", {}).get("addressing_style", "path") == "path":
            self.addressing_style = "path"
        super().__init__(*args, **kwargs)

    def url(self, name, parameters=None, expire=None, http_method=None):  # noqa: D401
        base = settings.MEDIA_URL
        if not base.endswith('/'):
            base += '/'
        return f"{base}{name}".replace('//media/', '/media/')

