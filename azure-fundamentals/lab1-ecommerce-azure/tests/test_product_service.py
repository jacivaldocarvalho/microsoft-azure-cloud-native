"""Product registration must validate first and compensate cross-service failures."""

from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from product_service import (
    ProductRegistrationError,
    ProductValidationError,
    register_product,
    validate_product,
)


class ProductValidationTests(unittest.TestCase):
    def test_values_are_normalized_within_schema_limits(self):
        product = validate_product("  Notebook  ", "  Description  ", "25.50")
        self.assertEqual(product["nome"], "Notebook")
        self.assertEqual(product["descricao"], "Description")
        self.assertEqual(product["preco"], Decimal("25.50"))

    def test_schema_length_violations_are_rejected(self):
        invalid_values = [
            ("x" * 101, "valid", 1),
            ("valid", "x" * 256, 1),
        ]
        for name, description, price in invalid_values:
            with self.subTest(name_length=len(name), description_length=len(description)):
                with self.assertRaises(ProductValidationError):
                    validate_product(name, description, price)

    def test_invalid_price_and_extension_are_rejected(self):
        with self.assertRaises(ProductValidationError):
            validate_product("valid", "valid", -1)
        with self.assertRaises(ProductValidationError):
            validate_product(
                "valid", "valid", 1, SimpleNamespace(name="image.gif")
            )


class ProductRegistrationTests(unittest.TestCase):
    def test_invalid_product_calls_no_external_service(self):
        upload, insert, delete = Mock(), Mock(), Mock()
        with self.assertRaises(ProductValidationError):
            register_product(
                "valid", "x" * 256, 1, SimpleNamespace(name="image.png"),
                upload, insert, delete,
            )
        upload.assert_not_called()
        insert.assert_not_called()
        delete.assert_not_called()

    def test_successful_registration_keeps_uploaded_image(self):
        upload = Mock(return_value={"url": "https://example/image.png", "blob_name": "image.png"})
        insert, delete = Mock(return_value=True), Mock()
        product = register_product(
            "Product", "Description", 10, SimpleNamespace(name="image.png"),
            upload, insert, delete,
        )
        self.assertEqual(product["imagem_url"], "https://example/image.png")
        insert.assert_called_once_with(product)
        delete.assert_not_called()

    def test_database_failure_removes_uploaded_image(self):
        upload = Mock(return_value={"url": "https://example/image.jpg", "blob_name": "image.jpg"})
        insert = Mock(side_effect=RuntimeError("database unavailable"))
        delete = Mock()
        with self.assertRaises(ProductRegistrationError) as result:
            register_product(
                "Product", "Description", 10, SimpleNamespace(name="image.jpg"),
                upload, insert, delete,
            )
        self.assertIn("Database insert failed", str(result.exception))
        delete.assert_called_once_with("image.jpg")

    def test_upload_failure_prevents_database_insert(self):
        upload = Mock(side_effect=RuntimeError("storage unavailable"))
        insert, delete = Mock(), Mock()
        with self.assertRaises(ProductRegistrationError) as result:
            register_product(
                "Product", "Description", 10, SimpleNamespace(name="image.jpeg"),
                upload, insert, delete,
            )
        self.assertIn("Image upload failed", str(result.exception))
        insert.assert_not_called()
        delete.assert_not_called()


if __name__ == "__main__":
    unittest.main()
