import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.chunking.python_chunker import chunk_python_file

def main(file_path: str):
    source = Path(file_path).read_text(encoding="utf8")
    chunks = chunk_python_file(file_path, source)
    print(f"{len(chunks)} chunks from {file_path}\n")
    for c in chunks:
        parent = f" (in {c.parent_class})" if c.parent_class else ""
        print(f"[{c.chunk_type}] {c.name}{parent}  lines {c.start_line}-{c.end_line}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/chunk_python_demo.py <path_to_python_file>")
        sys.exit(1)
    main(sys.argv[1])