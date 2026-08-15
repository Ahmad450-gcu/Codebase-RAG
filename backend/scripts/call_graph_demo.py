import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.chunking.python_chunker import chunk_python_file
from app.graph.python_call_extractor import extract_intra_file_calls

def main(file_path: str):
    source = Path(file_path).read_text(encoding="utf8")
    chunks = chunk_python_file(file_path, source)
    edges = extract_intra_file_calls(file_path, chunks)
    print(f"{len(edges)} call edges from {file_path}\n")
    for e in edges:
        caller = f"{e.caller_parent_class}.{e.caller_name}" if e.caller_parent_class else e.caller_name
        status = "RESOLVED" if e.resolved else "unresolved"
        print(f"  [{status}] {caller} --({e.call_type})--> {e.callee_name}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/call_graph_demo.py <path_to_python_file>")
        sys.exit(1)
    main(sys.argv[1])