"""Download images listed in metadata.jsonl to their sharded local paths.

Each record must have: id, url, sha256, path.
Existing files whose hash matches are skipped; corrupted or missing files are
re-fetched. Failures are logged and the script continues to the next record.
"""

import hashlib
import json
import urllib.request
from pathlib import Path

METADATA = Path("metadata.jsonl")


def sha256(path: Path) -> str:
    """Return the hex SHA-256 digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(url: str, dest: Path, expected: str) -> None:
    """Download url to dest and verify its SHA-256 against expected.

    Raises ValueError and removes the file if the hash does not match.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url, headers={"User-Agent": "FacesDataset/0.1 (https://github.com/Faces)"}
    )
    with urllib.request.urlopen(req) as response:
        dest.write_bytes(response.read())
    if sha256(dest) != expected:
        dest.unlink()
        raise ValueError(f"hash mismatch")


def main() -> None:
    """Iterate metadata.jsonl and download any missing or corrupted images."""
    records = [json.loads(line) for line in METADATA.read_text().splitlines() if line]
    for r in records:
        path = Path(r["path"])
        if path.exists() and sha256(path) == r["sha256"]:
            print(f"skip (already downloaded) {r['id']}")
            continue
        print(f"fetch {r['id']}")
        try:
            fetch(r["url"], path, r["sha256"])
            print(f"ok    {r['id']}")
        except Exception as e:
            print(f"fail  {r['id']}: {e}")


if __name__ == "__main__":
    main()
