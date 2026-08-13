from dataclasses import dataclass
from typing import Optional
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from app.chunking.common import Chunk, source_with_exclusions

PY_LANGUAGE = Language(tspython.language())
_PARSER = Parser(PY_LANGUAGE)

def unwrap_decorated(node):
    if node.type == "decorated_definition":
        return node, node.child_by_field_name("definition")
    return node, node

def node_name(def_node) -> str:
    name_node = def_node.child_by_field_name("name")
    return name_node.text.decode("utf8") if name_node else "<anonymous>"

def definition_chunk(file_path, range_node, def_node, source_bytes, parent_class) -> Chunk:
    return Chunk(
        file_path=file_path,
        chunk_type="method" if parent_class else "function",
        name=node_name(def_node),
        parent_class=parent_class,
        language="python",
        start_line=range_node.start_point[0] + 1,
        end_line=range_node.end_point[0] + 1,
        source=source_bytes[range_node.start_byte:range_node.end_byte].decode("utf8"),
    )

def class_chunks(file_path, range_node, def_node, source_bytes) -> list[Chunk]:
    class_name = node_name(def_node)
    chunks = []
    method_ranges = []
    body = def_node.child_by_field_name("body")
    if body is not None:
        for child in body.children:
            if child.type not in ("function_definition", "decorated_definition"):
                continue
            m_range, m_def = unwrap_decorated(child)
            if m_def.type != "function_definition":
                continue  
            chunks.append(definition_chunk(file_path, m_range, m_def, source_bytes, class_name))
            method_ranges.append((m_range.start_byte, m_range.end_byte))
    shell_text = source_with_exclusions(
        source_bytes, range_node.start_byte, range_node.end_byte, method_ranges
    ).strip()
    if shell_text:
        chunks.append(Chunk(
            file_path=file_path, chunk_type="class", name=class_name, parent_class=None,
            language="python", start_line=range_node.start_point[0] + 1,
            end_line=range_node.end_point[0] + 1, source=shell_text,
        ))
    return chunks

def chunk_python_file(file_path: str, source_code: str) -> list[Chunk]:
    source_bytes = source_code.encode("utf8")
    root = _PARSER.parse(source_bytes).root_node
    chunks: list[Chunk] = []
    top_level_ranges: list[tuple[int, int]] = []

    for node in root.children:
        if node.type not in ("function_definition", "class_definition", "decorated_definition"):
            continue

        range_node, def_node = unwrap_decorated(node)

        if def_node.type == "function_definition":
            chunks.append(definition_chunk(file_path, range_node, def_node, source_bytes, parent_class=None))
        elif def_node.type == "class_definition":
            chunks.extend(class_chunks(file_path, range_node, def_node, source_bytes))

        top_level_ranges.append((range_node.start_byte, range_node.end_byte))

    module_text = source_with_exclusions(
        source_bytes, root.start_byte, root.end_byte, top_level_ranges
    ).strip()

    if module_text:
        chunks.append(Chunk(
            file_path=file_path, chunk_type="module_level", name="<module_top_level>",
            parent_class=None, language="python", start_line=root.start_point[0] + 1,
            end_line=root.end_point[0] + 1, source=module_text,
        ))
    return chunks