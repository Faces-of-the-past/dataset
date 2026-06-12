# dataset
Dataset builder workflow

## Why?
The _Faces of the past_ project requires all of us to work on the same datset.
The dataset contains a collection of images and their corresponding metadata.
Here we provide a script that:

1. Takes the metadata sheet `workflow.jsonl` as an input.
2. Downloads each image locally.
3. Checks the consistency of the downloads. If something is missing or wrong, re-downloads that and only that.

## How to use?
We are using `poetry` for dependency management. Install `poetry` and run:

```sh
poetry run python download.py
```

If you prefer to use your own dependency management system, just run `python download.py`.

## Architecture

### Visual workflow
```mermaid
flowchart TD
    M["metadata.jsonl<br/>(id · url · sha256 · path · label)<br/>download.py"]

    M -->|clone repo| START([Run download.py])
    START --> LOOP{For each record<br/>in manifest}

    LOOP --> CHECK{File exists<br/>at sharded path?}
    CHECK -->|No| DL["Download image"]
    CHECK -->|Yes| HASH{sha256 matches<br/>manifest?}

    HASH -->|Yes| SKIP["Skip — already have it"]
    HASH -->|No| DL

    DL --> VERIFY{Downloaded hash<br/>matches manifest?}
    VERIFY -->|Yes| WRITE["Write to images/ab/abc123.jpg<br/>+ (optional) record in local ledger"]
    VERIFY -->|No| RETRY["Retry / log failure"]

    SKIP --> NEXT
    RETRY --> NEXT
    WRITE --> NEXT
    NEXT([Next record])

    LOOP -->|All processed| DONE([Dataset complete → freeze])
    DONE 
    style M fill:#fff,stroke:#4285f4
    style DONE fill:#e8f5e9,stroke:#34a853
```
