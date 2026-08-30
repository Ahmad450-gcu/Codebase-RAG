import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chunking.python_chunker import chunk_python_file
from app.graph.cross_file_resolver import resolve_python_cross_file_calls
from app.graph.graph_builder import build_graph
from app.graph.import_extractor import extract_imports
from app.graph.module_index import build_module_index
from app.graph.python_call_extractor import extract_intra_file_calls
from app.ingestion.classifier import classify_repository

def main(repo_path: str):
    python_files = [
        c for c in classify_repository(repo_path)
        if c.category == "code" and c.language == "python"
    ]
    chunks_by_file, edges, bindings_by_file = {}, [], {}
    for f in python_files:
        source = f.absolute_path.read_text(encoding="utf8")
        chunks = chunk_python_file(f.relative_path, source)
        chunks_by_file[f.relative_path] = chunks
        edges.extend(extract_intra_file_calls(f.relative_path, chunks))
        bindings_by_file[f.relative_path] = extract_imports(source)
    module_index = build_module_index(list(chunks_by_file.keys()))

    before_resolved = sum(1 for e in edges if e.resolved)
    edges = resolve_python_cross_file_calls(edges, chunks_by_file, bindings_by_file, module_index)
    after_resolved = sum(1 for e in edges if e.resolved)

    all_chunks = [c for cs in chunks_by_file.values() for c in cs]
    graph = build_graph(all_chunks, edges)

    print(f"Resolved before cross-file: {before_resolved}")
    print(f"Resolved after cross-file:  {after_resolved}")
    print(f"New cross-file resolutions: {after_resolved - before_resolved}")
    print(f"Graph edges: {graph.number_of_edges()}")
    print()
    print("Cross-file edges specifically:")
    for e in edges:
        if e.resolved and e.target_file and e.target_file != e.file_path:
            print(f"  {e.file_path}::{e.caller_name}  -->  {e.target_file}::{e.target_name}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/cross_file_resolution_demo.py <repo_path>")
        sys.exit(1)
    main(sys.argv[1])