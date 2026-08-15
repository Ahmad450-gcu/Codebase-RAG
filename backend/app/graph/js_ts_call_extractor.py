from app.chunking.common import Chunk
from app.chunking.js_ts_chunker import _PARSER
from app.graph.common import CallEdge

def text(node, source_bytes) -> str:
    return source_bytes[node.start_byte:node.end_byte].decode("utf8")

def iter_call_nodes(node):
    if node.type == "call_expression":
        yield node
    for child in node.children:
        yield from iter_call_nodes(child)

def classify_call(call_node, source_bytes):
    func_node = call_node.child_by_field_name("function")
    if func_node is None:
        return None

    if func_node.type == "identifier":
        return "plain", text(func_node, source_bytes)

    if func_node.type == "member_expression":
        obj_node = func_node.child_by_field_name("object")
        prop_node = func_node.child_by_field_name("property")
        if prop_node is None:
            return None
        method_name = text(prop_node, source_bytes)

        if obj_node is not None and obj_node.type == "this":
            return "instance_method", method_name

        return "attribute", method_name
    return None

def extract_intra_file_calls(file_path: str, chunks: list[Chunk], language: str) -> list[CallEdge]:
    if language not in _PARSER:
        raise ValueError(f"Unsupported language: {language}")
    parser = _PARSER[language]

    function_names = {c.name for c in chunks if c.chunk_type == "function"}
    method_keys = {(c.parent_class, c.name) for c in chunks if c.chunk_type == "method"}

    edges: list[CallEdge] = []

    for chunk in chunks:
        if chunk.chunk_type not in ("function", "method"):
            continue

        source_bytes = chunk.source.encode("utf8")
        root = parser.parse(source_bytes).root_node

        for call_node in iter_call_nodes(root):
            classification = classify_call(call_node, source_bytes)
            if classification is None:
                continue
            call_type, callee_name = classification

            resolved, target_name, target_parent_class = False, None, None

            if call_type == "plain" and callee_name in function_names:
                resolved, target_name = True, callee_name
            elif call_type == "instance_method" and (chunk.parent_class, callee_name) in method_keys:
                resolved, target_name, target_parent_class = True, callee_name, chunk.parent_class

            edges.append(CallEdge(
                file_path=file_path,
                caller_name=chunk.name,
                caller_parent_class=chunk.parent_class,
                callee_name=callee_name,
                call_type=call_type,
                resolved=resolved,
                target_name=target_name,
                target_parent_class=target_parent_class,
            ))
    return edges