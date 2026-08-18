import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.chunking.cpp_chunker import chunk_cpp_file
from app.chunking.js_ts_chunker import chunk_js_ts_file
from app.chunking.python_chunker import chunk_python_file
from app.chunking.markdown_chunker import chunk_markdown_file
from app.graph.cpp_call_extractor import extract_intra_file_calls as cpp_calls
from app.graph.python_call_extractor import extract_intra_file_calls as python_calls
from app.graph.js_ts_call_extractor import extract_intra_file_calls as js_ts_calls
from app.graph.graph_builder import build_graph
from app.ingestion.classifier import classify_repository

def process_repo(repo_path: str):
    all_chunks, all_edges = [], []
    for classified in classify_repository(repo_path):
        try:
            source = classified.absolute_path.read_text(encoding="utf-8")
        except(UnicodeDecodeError, OSError):
            continue
        if classified.category == "code" and classified.language == "python":
            chunks = chunk_python_file(file_path=classified.relative_path, source_code=source)
            edges = python_calls(file_path=classified.relative_path, chunks=chunks)
        elif classified.category == "code" and classified.language == "javascript":
            chunks = chunk_js_ts_file(file_path=classified.relative_path, source_code=source, language="javascript")
            edges = js_ts_calls(file_path=classified.relative_path, chunks=chunks, language="javascript")
        elif classified.category == "code" and classified.language == "typescript":
            chunks = chunk_js_ts_file(file_path=classified.relative_path, source_code=source, language="typescript")
            edges = js_ts_calls(file_path=classified.relative_path, chunks=chunks, language="typescript")
        elif classified.category == "code" and classified.language == "cpp":
            chunks = chunk_cpp_file(file_path=classified.relative_path, source_code=source)
            edges = cpp_calls(file_path=classified.relative_path, chunks=chunks)
        elif classified.category == "markdown":
            chunks = chunk_markdown_file(classified.relative_path, source)
            edges = []
        else:
            continue
        all_chunks.extend(chunks)
        all_edges.extend(edges)
    return all_chunks, all_edges

def main(repo_path: str):
    chunks, edges = process_repo(repo_path=repo_path)
    graph = build_graph(chunks=chunks, call_edges=edges)
    resolved = [e for e in edges if e.resolved]
    print(f"Chunks: {len(chunks)}")
    print(f"Call edges found: {len(edges)}  ({len(resolved)} resolved, {len(edges) - len(resolved)} unresolved)")
    print(f"Graph nodes: {graph.number_of_nodes()}")
    print(f"Graph edges: {graph.number_of_edges()}")
    print()
    print("Graph edges (caller -> callee):")
    for u, v, data in graph.edges(data=True):
        print(f"  {u}  --({data['call_type']})-->  {v}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/build_graph_demo.py <repo_path>")
        sys.exit(1)
    main(sys.argv[1])