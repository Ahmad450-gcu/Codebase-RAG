import networkx as nx
from app.chunking.common import Chunk
from app.graph.common import CallEdge
from app.graph.node_id import node_id

def build_graph(chunks: list[Chunk], call_edges: list[CallEdge]) -> nx.DiGraph:
    graph = nx.DiGraph()
    for chunk in chunks:
        nid = node_id(chunk.file_path, chunk.name, chunk.parent_class)
        graph.add_node(
            nid,
            file_path=chunk.file_path,
            chunk_type=chunk.chunk_type,
            name=chunk.name,
            parent_class=chunk.parent_class,
            language=chunk.language,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
        )

    for edge in call_edges:
        if not edge.resolved:
            continue
        caller_id = node_id(edge.file_path, edge.caller_name, edge.caller_parent_class)
        callee_id = node_id(edge.file_path, edge.target_name, edge.target_parent_class)
        if caller_id not in graph or callee_id not in graph:
            continue
        graph.add_edge(caller_id, callee_id, call_type="calls")
        
    return graph