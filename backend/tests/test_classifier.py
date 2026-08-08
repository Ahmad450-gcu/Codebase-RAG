from pathlib import Path
from app.ingestion.classifier import classify_file, classify_repository
from app.ingestion.walker import FileEntry

def entry(relative_path: str) -> FileEntry:
    return FileEntry(
        absolute_path=Path(relative_path),
        relative_path=relative_path,
        size_bytes=10,
        modified_time=0.0,
    )

def test_python_file_classified_as_code():
    result = classify_file(entry("src/main.py"))
    assert result.category == "code"
    assert result.language == "python"

def test_javascript_and_typescript_variants():
    assert classify_file(entry("app.js")).language == "javascript"
    assert classify_file(entry("app.jsx")).language == "javascript"
    assert classify_file(entry("app.ts")).language == "typescript"
    assert classify_file(entry("app.tsx")).language == "typescript"

def test_cpp_variants_including_ambiguous_header():
    assert classify_file(entry("main.cpp")).language == "cpp"
    assert classify_file(entry("main.hpp")).language == "cpp"
    assert classify_file(entry("legacy.h")).language == "cpp"  

def test_markdown_file_classified_correctly():
    result = classify_file(entry("README.md"))
    assert result.category == "markdown"
    assert result.language is None

def test_config_file_classified_correctly():
    result = classify_file(entry("package.json"))
    assert result.category == "config"
    assert result.language is None

def test_unknown_extension_is_other():
    result = classify_file(entry("logo.svg"))
    assert result.category == "other"
    assert result.language is None

def test_classify_repository_integrates_walker_and_classifier(tmp_path: Path):
    (tmp_path / "main.py").write_text("print(1)")
    (tmp_path / "README.md").write_text("# Docs")
    (tmp_path / "notes.txt").write_text("random")

    results = {r.relative_path: r.category for r in classify_repository(tmp_path)}

    assert results["main.py"] == "code"
    assert results["README.md"] == "markdown"
    assert results["notes.txt"] == "other"