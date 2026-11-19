from app.services.media import ImageFormat, detect_raster_image


def test_detects_jpeg_from_file_signature():
    assert detect_raster_image(b"\xff\xd8\xff\xe0fake-jpeg") == ImageFormat("jpg", "image/jpeg")


def test_detects_png_from_file_signature():
    assert detect_raster_image(b"\x89PNG\r\n\x1a\nrest-of-png") == ImageFormat("png", "image/png")


def test_detects_webp_from_riff_signature():
    assert detect_raster_image(b"RIFF\x10\x00\x00\x00WEBPrest") == ImageFormat("webp", "image/webp")


def test_rejects_svg_and_unrecognized_uploads():
    assert detect_raster_image(b"<svg xmlns='http://www.w3.org/2000/svg'></svg>") is None
    assert detect_raster_image(b"not an image") is None
    assert detect_raster_image(b"") is None
