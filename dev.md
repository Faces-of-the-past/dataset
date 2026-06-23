# Description

## How to run me

The data curator should run this:
```sh
poetry run python build_manifest.py
```

Other users will directly download from the manifest and check consistency (to be developed).

## Main idea

The download url seems to be coded in the media.original_file_name_lref field. With this pattern:

```sh
https://media.rkd.nl/iiif/{media.original_file_name_lref}/full/max/0/default.jpg.
```

`build_manifest.py` does the following: 
- parses `subset.xml` directly (no JSONL intermediate)
- resolves each `<media>` entry's `media.original_file_name_lref` to `https://media.rkd.nl/iiif/{lref}/full/max/0/default.jpg`
- downloads the jpg
- hashes it
- writes `subset_metadata.jsonl` (51 entries, one per media item, content-addressed under `data/<hash-prefix>/rkd{priref}_{occ}.jpg`)

In addition, it resumes safely: a killed/interrupted run reuses already-downloaded files by id instead of re-fetching, and requests now have a 30s timeout (the original run stalled indefinitely on one slow request before this fix).

## Questions for Lia

- Each XML record can have several <media> entries (e.g. priref 19 has 3: an ektachrome, a color reproduction, a b/w photo). Which should become the image we download for that record?

## Next steps
- Use `@priref` as identifier. It is the core of the permalink.
