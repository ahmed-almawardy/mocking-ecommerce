"""Small, deterministic helpers for validating uploaded raster image headers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImageFormat:
    extension: str
    content_type: str


def detect_raster_image(content: bytes) -> ImageFormat | None:
    """Identify supported image formats using their file signatures.

    Do not trust an upload's filename or browser-supplied Content-Type header.
    """
    if content.startswith(b"\xff\xd8\xff"):
        return ImageFormat("jpg", "image/jpeg")
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return ImageFormat("png", "image/png")
    if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return ImageFormat("webp", "image/webp")
    return None
