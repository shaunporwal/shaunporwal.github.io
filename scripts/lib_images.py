"""Reads the pixel size of a PNG, JPEG or WebP file, with the standard library only.

The type comes from the first bytes of the file, not from its name: some post images are WebP data in a .png file.

The generators write width and height on each image, so the browser reserves the space
before the image loads and the page does not jump.
"""
import pathlib
import struct

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
VP8_START_CODE = b"\x9d\x01\x2a"
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


def webp_size(data: bytes) -> tuple[int, int] | None:
    """(width, height) of a WebP file in the lossy, lossless or extended layout, or None."""
    kind = data[12:16]
    if kind == b"VP8X":
        return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
    if kind == b"VP8L" and data[20:21] == b"\x2f":
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if kind == b"VP8 " and data[23:26] == VP8_START_CODE:
        return int.from_bytes(data[26:28], "little") & 0x3FFF, int.from_bytes(data[28:30], "little") & 0x3FFF
    return None


def image_size(path: pathlib.Path) -> tuple[int, int] | None:
    """(width, height) of a PNG, JPEG or WebP file, or None for any other type."""
    data = path.read_bytes()
    if data.startswith(PNG_SIGNATURE):
        return png_size(data)
    if data.startswith(b"\xff\xd8"):
        return jpeg_size(data)
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return webp_size(data)
    return None


def size_attributes(path: pathlib.Path) -> str:
    """' width="W" height="H"' for the image, or an empty string when the size is unknown."""
    size = image_size(path)
    return f' width="{size[0]}" height="{size[1]}"' if size else ""
