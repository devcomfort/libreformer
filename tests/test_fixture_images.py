"""Tests for programmatic test image generation (US4)."""

from io import BytesIO
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image

from fixture_helpers.images import create_test_image


def test_create_test_image_returns_valid_png():
    """create_test_image() returns valid PNG bytes."""
    data = create_test_image()
    # PNG magic bytes: \x89PNG\r\n\x1a\n
    assert data[:4] == b"\x89PNG"


def test_create_test_image_minimum_size():
    """Generated image is at least 100x100 pixels."""
    data = create_test_image(200, 200)
    img = Image.open(BytesIO(data))
    assert img.width >= 100
    assert img.height >= 100


def test_create_test_image_custom_size():
    """create_test_image() respects custom width/height."""
    data = create_test_image(300, 150)
    img = Image.open(BytesIO(data))
    assert img.width == 300
    assert img.height == 150


def test_create_test_image_format_is_png():
    """Generated image format is PNG."""
    data = create_test_image()
    img = Image.open(BytesIO(data))
    assert img.format == "PNG"


def test_test_image_bytes_fixture(test_image_bytes: bytes):
    """test_image_bytes fixture returns valid PNG bytes."""
    assert test_image_bytes[:4] == b"\x89PNG"
    img = Image.open(BytesIO(test_image_bytes))
    assert img.width == 200
    assert img.height == 200
