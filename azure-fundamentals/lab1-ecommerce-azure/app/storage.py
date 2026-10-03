"""Manage private product images using the application's storage credentials."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
from uuid import uuid4

from azure.storage.blob import BlobServiceClient, ContentSettings

CONTENT_TYPES = {
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
}


def upload_product_image(file, connection_string, account_name, container_name):
    """Upload an image with its original extension and correct MIME type."""
    suffix = Path(file.name).suffix.lower()
    if suffix not in CONTENT_TYPES:
        raise ValueError("Product image must be PNG, JPG, or JPEG.")

    blob_name = f"{uuid4()}{suffix}"
    with BlobServiceClient.from_connection_string(connection_string) as service:
        blob = service.get_blob_client(container=container_name, blob=blob_name)
        blob.upload_blob(
            file.read(),
            overwrite=False,
            content_settings=ContentSettings(content_type=CONTENT_TYPES[suffix]),
        )

    return {
        "blob_name": blob_name,
        "url": (
            f"https://{account_name}.blob.core.windows.net/"
            f"{container_name}/{blob_name}"
        ),
    }


def delete_product_image(blob_name, connection_string, container_name):
    """Remove an uploaded image during compensation after a SQL failure."""
    with BlobServiceClient.from_connection_string(connection_string) as service:
        service.get_blob_client(
            container=container_name, blob=blob_name
        ).delete_blob(delete_snapshots="include")


def download_product_image(image_url, connection_string, account_name, container_name):
    url = urlsplit(image_url)
    prefix = f"/{container_name}/"
    if (url.scheme != "https" or url.netloc != f"{account_name}.blob.core.windows.net"
            or not url.path.startswith(prefix) or url.query or url.fragment):
        raise ValueError("Image URL does not belong to the configured product container.")
    blob_name = unquote(url.path[len(prefix):])
    if not blob_name:
        raise ValueError("Image URL has no blob name.")
    with BlobServiceClient.from_connection_string(connection_string) as service:
        return service.get_blob_client(container=container_name, blob=blob_name).download_blob().readall()
