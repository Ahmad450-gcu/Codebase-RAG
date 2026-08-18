from app.chunking.common import Chunk
from app.graph.common import CallEdge
from app.graph.graph_builder import build_graph
from app.graph.node_id import node_id

def chunk(file_path, name, parent_class=None, chunk_type="function"):
    return Chunk(
        file_path=file_path, chunk_type=chunk_type, name=name, parent_class=parent_class,
        language="python", start_line=1, end_line=2, source="pass",
    )

def test_everychunk_becomes_a_node():
    chunks = [chunk("m.py", "a"), chunk("m.py", "b")]
    graph = build_graph(chunks, [])
    assert graph.number_of_nodes() == 2

def test_resolved_call_edge_becomes_graph_edge():
    chunks = [chunk("m.py", "a"), chunk("m.py", "b")]
    edge = CallEdge(
        file_path="m.py", caller_name="a", caller_parent_class=None,
        callee_name="b", call_type="plain", resolved=True,
        target_name="b", target_parent_class=None,
    )
    graph = build_graph(chunks, [edge])
    assert graph.number_of_edges() == 1
    assert graph.has_edge(node_id("m.py", "a"), node_id("m.py", "b"))

def test_unresolved_call_edge_does_not_become_graph_edge():
    chunks = [chunk("m.py", "a")]
    edge = CallEdge(
        file_path="m.py", caller_name="a", caller_parent_class=None,
        callee_name="os.path.join", call_type="attribute", resolved=False,
        target_name=None, target_parent_class=None,
    )
    graph = build_graph(chunks, [edge])
    assert graph.number_of_edges() == 0

def test_method_and_class_nodes_have_distinct_ids():
    chunks = [
        chunk("m.py", "Widget", chunk_type="class"),
        chunk("m.py", "render", parent_class="Widget", chunk_type="method"),
    ]
    graph = build_graph(chunks, [])
    assert node_id("m.py", "Widget") in graph
    assert node_id("m.py", "render", "Widget") in graph

def test_same_function_name_in_different_files_are_distinct_nodes():
    chunks = [chunk("a.py", "helper"), chunk("b.py", "helper")]
    graph = build_graph(chunks, [])
    assert graph.number_of_nodes() == 2
    assert node_id("a.py", "helper") != node_id("b.py", "helper")

def test_node_carries_useful_attributes():
    chunks = [chunk("m.py", "a")]
    graph = build_graph(chunks, [])
    attrs = graph.nodes[node_id("m.py", "a")]
    assert attrs["chunk_type"] == "function"
    assert attrs["language"] == "python"
    assert attrs["start_line"] == 1