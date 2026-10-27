"""Every file in site/media is used by a page, the stylesheet, or a data
file. An unused file is still published, so it costs downloads and can leak
private documents."""
import pathlib
import unittest

import context

MEDIA_DIR = context.REPO_ROOT / "site" / "media"
REFERENCE_GLOBS = (("site", "**/*.html"), ("site", "**/*.css"), ("data", "*.json"))


def reference_text(repo_root: pathlib.Path) -> str:
    return "\n".join(
        path.read_text() for base, pattern in REFERENCE_GLOBS for path in (repo_root / base).glob(pattern)
    )


def unused_media(media_dir: pathlib.Path, text: str) -> list[str]:
    """Each file under media_dir, as a path below it, that the text never names. A file in a folder keeps its folder."""
    paths = (path.relative_to(media_dir).as_posix() for path in media_dir.rglob("*") if path.is_file())
    return sorted(path for path in paths if path not in text)


class TestMediaRefs(unittest.TestCase):
    def test_finds_an_unused_file(self):
        media_dir = context.temp_repo(self) / "site" / "media"
        media_dir.mkdir()
        (media_dir / "used.png").touch()
        (media_dir / "unused.png").touch()
        self.assertEqual(unused_media(media_dir, '<img src="media/used.png">'), ["unused.png"])

    def test_finds_an_unused_file_in_a_folder(self):
        media_dir = context.temp_repo(self) / "site" / "media"
        (media_dir / "projects").mkdir(parents=True)
        (media_dir / "projects" / "a.webp").touch()
        (media_dir / "projects" / "b.webp").touch()
        self.assertEqual(unused_media(media_dir, "/media/projects/a.webp"), ["projects/b.webp"])

    def test_every_site_media_file_is_used(self):
        self.assertEqual(unused_media(MEDIA_DIR, reference_text(context.REPO_ROOT)), [])


if __name__ == "__main__":
    unittest.main()
