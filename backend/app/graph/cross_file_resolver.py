from dataclasses import replace # The dataclasses.replace() function creates a new instance of a data class, copying the original object while replacing specific fields with new values. It is the preferred method for modifying instances of frozen (immutable) data classes without changing the original data
from app.chunking.common import Chunk 
from app.graph.common import CallEdge
from app.graph.import_extractor import ImportBinding

def function_names_in_file(file_chunks: dict[str: list[Chunk]], file_path: str) -> set[str]:
    function_names = set()
    for c in file_chunks.get(file_path, []):
        if c.chunk_type == "function":
            function_names.add(c.name)
    return function_names

def resolve_python_cross_file_calls(
        edges: list[CallEdge], file_chunks: dict[str: list[Chunk]], 
        file_import_bindings: dict[str, list[ImportBinding]], module_index: dict[str: str]
        ) -> list[CallEdge]:
    resolved_edges = []
    for edge in edges:
        if edge.resolved or edge.call_type not in ('plain', 'attribute'):
            resolved_edges.append(edge)
            continue
        bindings = file_import_bindings.get(edge.file_path, [])
        target_file = None
        if edge.call_type == 'plain':
            match = next((b for b in bindings if b.local_name == edge.callee_name and b.imported_name is not None), None) # next() is a built-in function that fetches the absolute first item returned from an iterator block. It runs until it hits the first element that satisfies the criteria, then stops execution just like using break in a loop after a condition satisfies.
            if match is not None:
                candidate = module_index.get(match.target_module)
                if candidate and match.imported_name in function_names_in_file(file_chunks, candidate):
                    target_file = candidate
        elif edge.call_type == 'attribure' and edge.object_name is not None:
             match = next((b for b in bindings if b.local_name == edge.object_name and b.imported_name is None), None)
             if match is not None:
                candidate = module_index.get(match.target_module)
                if candidate and edge.callee_name in function_names_in_file(file_chunks, candidate):
                    target_file = candidate
        if target_file is not None:
             resolved_edges.append(replace(edge, resolved=True, target_name=edge.callee_name, target_parent_class=None, target_file=target_file))
        else:
            resolved_edges.append(edge)
    return resolved_edges     