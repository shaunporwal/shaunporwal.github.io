"""Reads the pixel size of a PNG or JPEG file, with the standard library only.

The generators write width and height on each image, so the browser reserves the space
before the image loads and the page does not jump.
"""
import pathlib
import struct

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SOF_MARKERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


def png_size(data: bytes) -> tuple[int, int]:
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def jpeg_size(data: bytes) -> tuple[int, int]:
    index = 2
    while index + 9 < len(data):
        marker = data[index + 1]
        if marker in SOF_MARKERS:
            height, width = struct.unpack(">HH", data[index + 5 : index + 9])
            return width, height
        index += 2 + struct.unpack(">H", data[index + 2 : index + 4])[0]
    raise ValueError("no size marker in the JPEG data")


def image_size(path: pathlib.Path) -> tuple[int, int] | None:
    """(width, height) of a PNG or JPEG file, or None for any other type."""
    data = path.read_bytes()
    if data.startswith(PNG_SIGNATURE):
        return png_size(data)
    if data.startswith(b"\xff\xd8"):
        return jpeg_size(data)
    return None


def size_attributes(path: pathlib.Path) -> str:
    """' width="W" height="H"' for the image, or an empty string when the size is unknown."""
    size = image_size(path)
    return f' width="{size[0]}" height="{size[1]}"' if size else ""
