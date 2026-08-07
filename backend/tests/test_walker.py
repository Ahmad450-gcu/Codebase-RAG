from pathlib import Path
from app.ingestion.walker import walk_repository

def relative_paths(repo_root: Path) -> set[str]:
    return {e.relative_path for e in walk_repository(repo_root)}

def test_normal_source_files_are_included(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hi')")
    (tmp_path / "app.ts").write_text("console.log('hi')")
    result = relative_paths(tmp_path)
    assert "main.py" in result
    assert "app.ts" in result

def test_default_ignored_directories_are_never_walked(tmp_path: Path):
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "pkg.js").write_text("junk")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_text("junk")
    (tmp_path / "real.py").write_text("print(1)")
    result = relative_paths(tmp_path)
    assert "real.py" in result
    assert not any("node_modules" in p for p in result)
    assert not any(p.startswith(".git/") for p in result)

def test_gitignore_rules_are_respected(tmp_path: Path):
    (tmp_path / ".gitignore").write_text("secrets/\n*.log\n")
    (tmp_path / "secrets").mkdir()
    (tmp_path / "secrets" / "keys.env").write_text("API_KEY=x")
    (tmp_path / "debug.log").write_text("log data")
    (tmp_path / "keep.py").write_text("print(1)")
    result = relative_paths(tmp_path)
    assert "keep.py" in result
    assert "secrets/keys.env" not in result
    assert "debug.log" not in result

def test_binary_files_are_skipped_even_outside_ignored_dirs(tmp_path: Path):
    (tmp_path / "image.png").write_bytes(b"\x89PNG\x00\x01fakedata")
    (tmp_path / "real.py").write_text("print(1)")
    result = relative_paths(tmp_path)
    assert "real.py" in result
    assert "image.png" not in result

def test_oversized_files_are_skipped(tmp_path: Path, monkeypatch):
    import app.ingestion.walker as walker_module
    monkeypatch.setattr(walker_module, "MAX_FILE_SIZE_BYTES", 10) # temporarily setting Max size to 10kb
    (tmp_path / "small.py").write_text("x=1")   # only 3 bytes, should be accepted 
    (tmp_path / "big.py").write_text("x = 1\n" * 100)  # approx 600 bytes, should be discarded
    result = relative_paths(tmp_path)
    assert "small.py" in result
    assert "big.py" not in result

def test_empty_files_are_skipped(tmp_path: Path):
    (tmp_path / "empty.py").touch() # .touch creates an empty file
    (tmp_path / "real.py").write_text("print(1)")
    result = relative_paths(tmp_path)
    assert "real.py" in result
    assert "empty.py" not in result

def test_nonexistent_repo_root_raises(tmp_path: Path):
    import pytest
    with pytest.raises(ValueError):
        list(walk_repository(tmp_path / "does_not_exist"))