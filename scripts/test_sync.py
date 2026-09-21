import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from sync import sync


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "source"
        self.destination = Path(self.temp.name) / "bank"
        self.source.mkdir()
        self.destination.mkdir()
        data = b'{"id": "course"}\n'
        (self.source / "course.json").write_bytes(data)
        self.catalog = {"collection_id": "bank", "content_revision": 1, "courses": [
            {"id": "course", "path": "course.json", "sha256": hashlib.sha256(data).hexdigest()}
        ]}
        self.write_catalog()
        (self.destination / "catalog.json").write_text(json.dumps({"collection_id": "bank"}))

    def write_catalog(self):
        (self.source / "catalog.json").write_text(json.dumps(self.catalog))

    def assert_rejected(self, message):
        before = (self.destination / "catalog.json").read_bytes()
        with self.assertRaisesRegex(ValueError, message):
            sync(self.source, self.destination)
        self.assertEqual((self.destination / "catalog.json").read_bytes(), before)
        self.assertFalse((self.destination / "course.json").exists())

    def test_copies_exact_bytes_and_notices_idempotently(self):
        (self.source / "README.md").write_text("upstream notes")
        (self.destination / "README.md").write_text("publication instructions")
        (self.source / "imports").mkdir()
        (self.source / "imports/LICENSE.txt").write_text("attribution")
        for _ in range(2):
            sync(self.source, self.destination)
        for name in ("catalog.json", "course.json", "imports/LICENSE.txt"):
            self.assertEqual((self.source / name).read_bytes(), (self.destination / name).read_bytes())
        self.assertEqual((self.destination / "CONTENT.md").read_text(), "upstream notes")
        self.assertEqual((self.destination / "README.md").read_text(), "publication instructions")

    def test_rejects_corrupt_course_before_copying(self):
        (self.source / "course.json").write_text('{"id": "modified"}')
        self.assert_rejected("Hash mismatch")

    def test_rejects_different_course_id(self):
        self.catalog["courses"][0]["id"] = "another-course"
        self.write_catalog()
        self.assert_rejected("Course ID mismatch")

    def test_rejects_downgrades(self):
        current = dict(self.catalog, content_revision=2)
        (self.destination / "catalog.json").write_text(json.dumps(current))
        self.assert_rejected("older catalog")

    def test_rejects_collection_switches(self):
        self.catalog["collection_id"] = "another-bank"
        self.write_catalog()
        self.assert_rejected("published collection")

    def test_rejects_unsafe_paths(self):
        for path in ("../course.json", "/course.json", "https://example.com/course.json", "..\\course.json"):
            with self.subTest(path=path):
                self.catalog["courses"][0]["path"] = path
                self.write_catalog()
                self.assert_rejected("Unsafe course path")


if __name__ == "__main__":
    unittest.main()
