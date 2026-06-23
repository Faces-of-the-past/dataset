"""Build a metadata manifest directly from an RKD AdLib XML export.

For each <record>/<media> pair, downloads the image once via RKD's IIIF
endpoint, hashes it, and emits a manifest line in the same shape consumed by
download.py: {id, url, sha256, path, label}. Existing files are reused
instead of re-downloaded if already present and correctly placed.
"""

import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

XML_IN = Path("subset.xml")
JSONL_OUT = Path("subset_metadata.jsonl")
IMAGE_URL = "https://media.rkd.nl/iiif/{lref}/full/max/0/default.jpg"


def label_for(record: ET.Element) -> str:
    """Prefer the English title; fall back to the Dutch one."""
    return record.findtext("titel_engels") or record.findtext("benaming_kunstwerk") or ""


def fetch(url: str, timeout: float = 30) -> bytes:
    """Download url and return its raw bytes."""
    req = urllib.request.Request(
        url, headers={"User-Agent": "FacesDataset/0.1 (https://github.com/Faces)"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def build_records(records: list[ET.Element]):
    """Yield one manifest dict per <media> entry, downloading as needed.

    A record already downloaded in a prior (interrupted) run is reused from
    disk instead of re-fetched, since its sharded path is keyed by id.
    """
    for record in records:
        priref = record.get("priref")
        label = label_for(record)
        for occ, media in enumerate(record.findall("media"), start=1):
            lref = media.findtext("media.original_file_name_lref")
            if not lref:
                continue
            record_id = f"rkd{priref}_{occ}"
            url = IMAGE_URL.format(lref=lref)
            existing = next(Path("data").glob(f"*/{record_id}.jpg"), None)
            if existing is not None:
                print(f"skip (already downloaded) {record_id}")
                data, path = existing.read_bytes(), existing
            else:
                print(f"fetch {record_id}")
                try:
                    data = fetch(url)
                except Exception as e:
                    print(f"fail  {record_id}: {e}")
                    continue
                path = Path("data") / hashlib.sha256(data).hexdigest()[:2] / f"{record_id}.jpg"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                print(f"ok    {record_id}")
            digest = hashlib.sha256(data).hexdigest()
            yield {
                "id": record_id,
                "url": url,
                "sha256": digest,
                "path": str(path),
                "label": label,
            }


def main() -> None:
    """Parse XML_IN and write the resulting manifest to JSONL_OUT."""
    root = ET.parse(XML_IN).getroot()
    records = root.find("recordList").findall("record")
    with JSONL_OUT.open("w") as f:
        n = 0
        for entry in build_records(records):
            f.write(json.dumps(entry, ensure_ascii=False))
            f.write("\n")
            n += 1
    print(f"wrote {n} manifest entries to {JSONL_OUT}")


if __name__ == "__main__":
    main()
