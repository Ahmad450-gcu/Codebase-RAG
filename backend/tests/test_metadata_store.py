from pathlib import Path
from app.db.metadata_store import MetadataStore
from app.ingestion.classifier import ClassifiedFile

def _file(path: str) -> ClassifiedFile:
    return ClassifiedFile(
        relative_path=path,
        absolute_path=Path(path),
        size_bytes=10,
        modified_time=0.0,
        category="code",
        language="python",
    )

def test_upsert_repository_is_idempotent(tmp_path):
    store = MetadataStore(str(tmp_path / "test.db"))
    id1 = store.upsert_repository("repo", "/some/path")
    id2 = store.upsert_repository("repo", "/some/path")
    assert id1 == id2
    store.close()

def test_new_file_reports_as_changed(tmp_path):
    store = MetadataStore(str(tmp_path / "test.db"))
    repo_id = store.upsert_repository("repo", "/some/path")
    changed = store.upsert_file(repo_id, _file("main.py"), "hash1")
    assert changed is True
    store.close()

def test_unchanged_file_reports_as_unchanged_on_second_run(tmp_path):
    store = MetadataStore(str(tmp_path / "test.db"))
    repo_id = store.upsert_repository("repo", "/some/path")
    store.upsert_file(repo_id, _file("main.py"), "hash1")
    changed = store.upsert_file(repo_id, _file("main.py"), "hash1")
    assert changed is False
    store.close()

def test_modified_file_reports_as_changed(tmp_path):
    store = MetadataStore(str(tmp_path / "test.db"))
    repo_id = store.upsert_repository("repo", "/some/path")
    store.upsert_file(repo_id, _file("main.py"), "hash1")
    changed = store.upsert_file(repo_id, _file("main.py"), "hash2")
    assert changed is True
    store.close()

def test_list_files_returns_all_files_for_repo(tmp_path):
    store = MetadataStore(str(tmp_path / "test.db"))
    repo_id = store.upsert_repository("repo", "/some/path")
    store.upsert_file(repo_id, _file("main.py"), "hash1")
    store.upsert_file(repo_id, _file("app.ts"), "hash2")
    files = store.list_files(repo_id)
    assert len(files) == 2
    store.close()