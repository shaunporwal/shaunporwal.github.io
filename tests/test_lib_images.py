"""Tests for scripts/lib_images.py."""
import struct
import unittest

import context
from lib_images import PNG_SIGNATURE, image_size, size_attributes

PNG = PNG_SIGNATURE + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 640, 480) + b"\x08\x06\x00\x00\x00"
APP0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x01\x01\x00\x00\x01\x00\x01\x00\x00"
SOF0 = b"\xff\xc0" + struct.pack(">H", 11) + b"\x08" + struct.pack(">HH", 300, 400) + b"\x01\x01\x11\x00"
JPEG = b"\xff\xd8" + APP0 + SOF0
RIFF = b"RIFF" + struct.pack("<I", 100) + b"WEBP"
CANVAS = (799).to_bytes(3, "little") + (599).to_bytes(3, "little")
WEBP_EXTENDED = RIFF + b"VP8X" + struct.pack("<I", 10) + b"\x00\x00\x00\x00" + CANVAS
WEBP_LOSSLESS = RIFF + b"VP8L" + struct.pack("<I", 5) + b"\x2f" + struct.pack("<I", 639 | (479 << 14))
WEBP_LOSSY = RIFF + b"VP8 " + struct.pack("<I", 10) + b"\x00\x00\x00" + b"\x9d\x01\x2a" + struct.pack("<HH", 320, 200)


class TestImageSize(unittest.TestCase):
    def setUp(self):
        self.dir = context.temp_repo(self)

    def test_reads_a_png(self):
        (self.dir / "a.png").write_bytes(PNG)
        self.assertEqual(image_size(self.dir / "a.png"), (640, 480))

    def test_reads_a_jpeg_after_skipping_the_header_segment(self):
        (self.dir / "a.jpg").write_bytes(JPEG)
        self.assertEqual(image_size(self.dir / "a.jpg"), (400, 300))

    def test_reads_each_webp_layout_even_in_a_png_file(self):
        for data, size in ((WEBP_EXTENDED, (800, 600)), (WEBP_LOSSLESS, (640, 480)), (WEBP_LOSSY, (320, 200))):
            (self.dir / "a.png").write_bytes(data)
            self.assertEqual(image_size(self.dir / "a.png"), size)

    def test_other_types_have_no_size(self):
        (self.dir / "a.gif").write_bytes(b"GIF89a")
        self.assertIsNone(image_size(self.dir / "a.gif"))

    def test_size_attributes(self):
        (self.dir / "a.png").write_bytes(PNG)
        (self.dir / "a.gif").write_bytes(b"GIF89a")
        self.assertEqual(size_attributes(self.dir / "a.png"), ' width="640" height="480"')
        self.assertEqual(size_attributes(self.dir / "a.gif"), "")


if __name__ == "__main__":
    unittest.main()
