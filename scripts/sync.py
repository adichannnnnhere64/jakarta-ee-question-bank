#!/usr/bin/env python3
"""Mirror validated Tutorialz content without regenerating authored questions."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def sync(source: Path, destination: Path) -> None:
    incoming = json.loads((source / "catalog.json").read_text())
    current = json.loads((destination / "catalog.json").read_text())
    if incoming["collection_id"] != current["collection_id"]:
        raise ValueError("Refusing to replace the published collection")
    if incoming.get("content_revision", 0) < current.get("content_revision", 0):
        raise ValueError("Refusing to publish an older catalog revision")
    # Validate every referenced file before changing the destination.
    for entry in incoming["courses"]:
        path = Path(entry["path"])
        if path.is_absolute() or ".." in path.parts or "\\" in str(path) or ":" in str(path):
            raise ValueError(f"Unsafe course path: {path}")
        data = (source / path).read_bytes()
        if hashlib.sha256(data).hexdigest() != entry["sha256"].lower():
            raise ValueError(f"Hash mismatch: {path}")
        if json.loads(data)["id"] != entry["id"]:
            raise ValueError(f"Course ID mismatch: {path}")
    for path in source.rglob("*"):
        if path.is_file():
            relative = path.relative_to(source)
            target = destination / ("CONTENT.md" if str(relative) == "README.md" else relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Tutorialz content/enterprise directory")
    args = parser.parse_args()
    sync(args.source, Path(__file__).resolve().parents[1])
