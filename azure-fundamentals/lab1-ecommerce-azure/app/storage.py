"""Read private product images using the application's storage credentials."""
from urllib.parse import unquote, urlsplit

from azure.storage.blob import BlobServiceClient


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
