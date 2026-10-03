"""Product validation and cross-service registration workflow."""

from decimal import Decimal, InvalidOperation
from pathlib import Path

NAME_MAX_LENGTH = 100
DESCRIPTION_MAX_LENGTH = 255
PRICE_MAX_VALUE = Decimal("99999999.99")
ALLOWED_IMAGE_EXTENSIONS = {".jpeg", ".jpg", ".png"}


class ProductValidationError(ValueError):
    """Raised before external services are called when product data is invalid."""


class ProductRegistrationError(RuntimeError):
    """Raised when a storage or database operation prevents registration."""


def validate_product(name, description, price, uploaded_file=None):
    """Validate and normalize values according to the SQL schema."""
    normalized_name = (name or "").strip()
    normalized_description = (description or "").strip()

    if not normalized_name:
        raise ProductValidationError("Product name is required.")
    if len(normalized_name) > NAME_MAX_LENGTH:
        raise ProductValidationError(
            f"Product name must contain at most {NAME_MAX_LENGTH} characters."
        )
    if not normalized_description:
        raise ProductValidationError("Product description is required.")
    if len(normalized_description) > DESCRIPTION_MAX_LENGTH:
        raise ProductValidationError(
            "Product description must contain at most "
            f"{DESCRIPTION_MAX_LENGTH} characters."
        )

    try:
        normalized_price = Decimal(str(price))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ProductValidationError("Product price must be a valid number.") from exc
    if not normalized_price.is_finite() or normalized_price < 0:
        raise ProductValidationError("Product price must be zero or greater.")
    if normalized_price > PRICE_MAX_VALUE:
        raise ProductValidationError(
            f"Product price must not exceed {PRICE_MAX_VALUE}."
        )

    if uploaded_file is not None:
        suffix = Path(uploaded_file.name).suffix.lower()
        if suffix not in ALLOWED_IMAGE_EXTENSIONS:
            raise ProductValidationError("Product image must be PNG, JPG, or JPEG.")

    return {
        "nome": normalized_name,
        "descricao": normalized_description,
        "preco": normalized_price,
        "imagem_url": "",
    }


def register_product(
    name,
    description,
    price,
    uploaded_file,
    upload_image,
    insert_product,
    delete_image,
):
    """Register one product and compensate the Blob upload if SQL fails."""
    product = validate_product(name, description, price, uploaded_file)
    uploaded_image = None

    if uploaded_file is not None:
        try:
            uploaded_image = upload_image(uploaded_file)
            product["imagem_url"] = uploaded_image["url"]
        except Exception as exc:
            raise ProductRegistrationError(f"Image upload failed: {exc}") from exc

    try:
        inserted = insert_product(product)
        if inserted is False:
            raise RuntimeError("The database operation did not insert the product.")
    except Exception as database_error:
        if uploaded_image is not None:
            try:
                delete_image(uploaded_image["blob_name"])
            except Exception as cleanup_error:
                raise ProductRegistrationError(
                    "Database insert failed and the uploaded image could not be removed: "
                    f"{cleanup_error}"
                ) from database_error
        raise ProductRegistrationError(
            f"Database insert failed: {database_error}"
        ) from database_error

    return product
