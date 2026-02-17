"""PNG image generation helper for embedding in test documents."""

from io import BytesIO

from PIL import Image, ImageDraw


def create_test_image(width: int = 200, height: int = 200) -> bytes:
    """Create a test PNG image programmatically using Pillow.

    Generates a white canvas with a blue rectangle, light-blue ellipse,
    and "TEST" text. Suitable for embedding in docx/pptx documents.

    Args:
        width: Image width in pixels. Minimum 100.
        height: Image height in pixels. Minimum 100.

    Returns:
        PNG image as bytes.
    """
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Blue rectangle border
    draw.rectangle([20, 20, width - 20, height - 20], outline="blue", width=3)

    # Light-blue filled ellipse
    draw.ellipse([40, 40, width - 40, height - 40], fill="lightblue")

    # "TEST" text centered
    draw.text((width // 2 - 20, height // 2 - 10), "TEST", fill="black")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
