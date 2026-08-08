"""
Phase 1 end-to-end: walk + classify + hash + persist a repo's file
manifest.

Usage:
    python scripts/ingest_repo.py <repo_path> <repo_name>
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.metadata_store import MetadataStore
from app.ingestion.classifier import classify_repository
from app.ingestion.hashing import compute_content_hash


def ingest(repo_path: str, repo_name: str, db_path: str = "metadata.db"):
    store = MetadataStore(db_path)
    repo_id = store.upsert_repository(repo_name, repo_path)

    new_or_changed = 0
    unchanged = 0

    for classified in classify_repository(repo_path):
        content_hash = compute_content_hash(classified.absolute_path)
        if store.upsert_file(repo_id, classified, content_hash):
            new_or_changed += 1
        else:
            unchanged += 1

    store.close()
    print(f"Repo: {repo_name} (id={repo_id})")
    print(f"New/changed files: {new_or_changed}")
    print(f"Unchanged files: {unchanged}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/ingest_repo.py <repo_path> <repo_name>")
        sys.exit(1)
    ingest(sys.argv[1], sys.argv[2])