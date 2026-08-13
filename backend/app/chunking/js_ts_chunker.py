import tree_sitter_javascript as tsjs
import tree_sitter_typescript as tsts
from tree_sitter import Language, Parser
from app.chunking.common import Chunk, source_with_exclusions

JS_LANGUAGE = Language(tsjs.language())
TS_LANGUAGE = Language(tsts.language_typescript())
_PARSERS = {"javascript": Parser(JS_LANGUAGE), "typescript": Parser(TS_LANGUAGE)}
_FUNCTION_VALUE_TYPES = ("arrow_function", "function_expression")
_NAME_NODE_TYPES = ("identifier", "property_identifier", "type_identifier")

def text(node, source_bytes) -> str:
    return source_bytes[node.start_byte:node.end_byte].decode("utf8")

def name_of(node, source_bytes) -> str:
    name_node = node.child_by_field_name("name")
    if name_node is None:
        name_node = next((c for c in node.children if c.type in _NAME_NODE_TYPES), None)
    return text(name_node, source_bytes) if name_node else "<anonymous>"

def field_or_type(node, field_name: str, type_name: str):
    child = node.child_by_field_name(field_name)
    if child is not None:
        return child
    return next((c for c in node.children if c.type == type_name), None)

def single_function_declarator(decl_node):
    declarators = [c for c in decl_node.children if c.type == "variable_declarator"]
    if len(declarators) != 1:
        return None
    value = declarators[0].child_by_field_name("value")
    if value is None:
        value = next((c for c in declarators[0].children if c.type in _FUNCTION_VALUE_TYPES), None)
    return declarators[0] if value is not None and value.type in _FUNCTION_VALUE_TYPES else None

def class_chunks(file_path, class_node, source_bytes, language) -> list[Chunk]:
    class_name = name_of(class_node, source_bytes)
    chunks, method_ranges = [], []
    body = field_or_type(class_node, "body", "class_body")
    if body is not None:
        for child in body.children:
            if child.type != "method_definition":
                continue
            chunks.append(Chunk(
                file_path=file_path, chunk_type="method", name=name_of(child, source_bytes),
                parent_class=class_name, language=language,
                start_line=child.start_point[0] + 1, end_line=child.end_point[0] + 1,
                source=text(child, source_bytes),
            ))
            method_ranges.append((child.start_byte, child.end_byte))

    shelltext = source_with_exclusions(
        source_bytes, class_node.start_byte, class_node.end_byte, method_ranges
    ).strip()
    if shelltext:
        chunks.append(Chunk(
            file_path=file_path, chunk_type="class", name=class_name, parent_class=None,
            language=language, start_line=class_node.start_point[0] + 1,
            end_line=class_node.end_point[0] + 1, source=shelltext,
        ))
    return chunks

def chunk_js_ts_file(file_path: str, source_code: str, language: str) -> list[Chunk]:
    if language not in _PARSERS:
        raise ValueError(f"Unsupported language: {language}")

    source_bytes = source_code.encode("utf8")
    root = _PARSERS[language].parse(source_bytes).root_node

    chunks: list[Chunk] = []
    top_level_ranges: list[tuple[int, int]] = []

    for node in root.children:
        if node.type == "function_declaration":
            chunks.append(Chunk(
                file_path=file_path, chunk_type="function", name=name_of(node, source_bytes),
                parent_class=None, language=language,
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                source=text(node, source_bytes),
            ))
            top_level_ranges.append((node.start_byte, node.end_byte))

        elif node.type in ("lexical_declaration", "variable_declaration"):
            declarator = single_function_declarator(node)
            if declarator is not None:
                chunks.append(Chunk(
                    file_path=file_path, chunk_type="function", name=name_of(declarator, source_bytes),
                    parent_class=None, language=language,
                    start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                    source=text(node, source_bytes),
                ))
                top_level_ranges.append((node.start_byte, node.end_byte))

        elif node.type == "class_declaration":
            chunks.extend(class_chunks(file_path, node, source_bytes, language))
            top_level_ranges.append((node.start_byte, node.end_byte))

        elif node.type in ("interface_declaration", "type_alias_declaration"):
            chunks.append(Chunk(
                file_path=file_path, chunk_type="type_definition", name=name_of(node, source_bytes),
                parent_class=None, language=language,
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                source=text(node, source_bytes),
            ))
            top_level_ranges.append((node.start_byte, node.end_byte))

    moduletext = source_with_exclusions(
        source_bytes, root.start_byte, root.end_byte, top_level_ranges
    ).strip()
    if moduletext:
        chunks.append(Chunk(
            file_path=file_path, chunk_type="module_level", name="<module_top_level>",
            parent_class=None, language=language,
            start_line=root.start_point[0] + 1, end_line=root.end_point[0] + 1,
            source=moduletext,
        ))
    return chunks