"""Private-image reads must use authenticated access to the configured container."""
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import storage


class PrivateImageTests(unittest.TestCase):
    def test_private_image_is_downloaded_with_application_credentials(self):
        service = MagicMock()
        service.__enter__.return_value.get_blob_client.return_value.download_blob.return_value.readall.return_value = b"image-bytes"
        with patch.object(storage.BlobServiceClient, "from_connection_string", return_value=service) as factory:
            result = storage.download_product_image(
                "https://account.blob.core.windows.net/products/photo.jpg",
                "test-only", "account", "products"
            )
        self.assertEqual(result, b"image-bytes")
        factory.assert_called_once_with("test-only")
        service.__enter__.return_value.get_blob_client.assert_called_once_with(container="products", blob="photo.jpg")

    def test_foreign_or_tokenized_urls_are_rejected_before_network_access(self):
        urls = [
            "https://other.blob.core.windows.net/products/photo.jpg",
            "https://account.blob.core.windows.net/other/photo.jpg",
            "http://account.blob.core.windows.net/products/photo.jpg",
            "https://account.blob.core.windows.net/products/photo.jpg?sig=token",
            "https://account.blob.core.windows.net/products/",
        ]
        with patch.object(storage.BlobServiceClient, "from_connection_string") as factory:
            for url in urls:
                with self.subTest(url=url), self.assertRaises(ValueError):
                    storage.download_product_image(url, "test-only", "account", "products")
            factory.assert_not_called()

    def test_download_errors_are_propagated_to_the_interface(self):
        with patch.object(storage.BlobServiceClient, "from_connection_string", side_effect=RuntimeError("unavailable")):
            with self.assertRaises(RuntimeError):
                storage.download_product_image("https://account.blob.core.windows.net/products/photo.jpg", "test-only", "account", "products")
