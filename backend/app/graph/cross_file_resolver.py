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
