from tree_sitter import Language, Parser
import tree_sitter_cpp as tscpp
from app.chunking.common import Chunk, source_with_exclusions

CPP_LANGUAGE = Language(tscpp.language())
_PARSER = Parser(CPP_LANGUAGE)
_TEMPLATE_INNER_TYPES = ("function_definition", "class_specifier", "struct_specifier", "declaration")

def text(node, source_bytes) -> str:
    return source_bytes[node.start_byte:node.end_byte].decode("utf8")

def unwrap_template(node):
    if node.type != "template_declaration":
        return node, node
    inner = next((c for c in reversed(node.children) if c.type in _TEMPLATE_INNER_TYPES), node)
    return node, inner

def find_function_declarator(node):
    return next((c for c in node.children if c.type == "function_declarator"), None)

def is_function_declaration(decl_node) -> bool:
    return any(c.type == "function_declarator" for c in decl_node.children)

def extract_name_and_parent(declarator, source_bytes):
    if declarator is None:
        return "<anonymous>", None

    simple_name = next((c for c in declarator.children if c.type in ("identifier", "field_identifier")), None)
    if simple_name is not None:
        return text(simple_name, source_bytes), None

    qualified = next((c for c in declarator.children if c.type == "qualified_identifier"), None)
    if qualified is not None:
        scope_node = next((c for c in qualified.children if c.type == "namespace_identifier"), None)
        name_node = next((c for c in qualified.children if c.type == "identifier"), None)
        parent = text(scope_node, source_bytes) if scope_node else None
        name = text(name_node, source_bytes) if name_node else "<anonymous>"
        return name, parent

    return "<anonymous>", None

def function_chunk(file_path, range_node, def_node, source_bytes, language, explicit_parent_class=None) -> Chunk:
    declarator = find_function_declarator(def_node)
    name, parent_from_qualifier = extract_name_and_parent(declarator, source_bytes)
    parent_class = explicit_parent_class or parent_from_qualifier
    return Chunk(
        file_path=file_path, chunk_type="method" if parent_class else "function",
        name=name, parent_class=parent_class, language=language,
        start_line=range_node.start_point[0] + 1, end_line=range_node.end_point[0] + 1,
        source=text(range_node, source_bytes),
    )

def name_of_class(def_node, source_bytes) -> str:
    name_node = next((c for c in def_node.children if c.type == "type_identifier"), None)
    return text(name_node, source_bytes) if name_node else "<anonymous>"

def class_or_struct_chunks(file_path, range_node, def_node, source_bytes, language) -> list[Chunk]:
    class_name = name_of_class(def_node, source_bytes)
    chunks, member_ranges = [], []

    body = next((c for c in def_node.children if c.type == "field_declaration_list"), None)
    if body is not None:
        for child in body.children:
            t_range, t_node = unwrap_template(child)
            if t_node.type == "function_definition":
                chunks.append(function_chunk(file_path, t_range, t_node, source_bytes, language, class_name))
                member_ranges.append((t_range.start_byte, t_range.end_byte))
            elif t_node.type in ("declaration", "field_declaration") and is_function_declaration(t_node):
                chunks.append(function_chunk(file_path, t_range, t_node, source_bytes, language, class_name))
                member_ranges.append((t_range.start_byte, t_range.end_byte))

    shell_text = source_with_exclusions(
        source_bytes, range_node.start_byte, range_node.end_byte, member_ranges
    ).strip()

    if shell_text:
        chunks.append(Chunk(
            file_path=file_path, chunk_type="class", name=class_name, parent_class=None,
            language=language, start_line=range_node.start_point[0] + 1,
            end_line=range_node.end_point[0] + 1, source=shell_text,
        ))
    return chunks

def namespace_chunks(file_path, range_node, def_node, source_bytes, language) -> list[Chunk]:
    ns_name_node = next((c for c in def_node.children if c.type == "namespace_identifier"), None)
    ns_name = text(ns_name_node, source_bytes) if ns_name_node else "<anonymous>"
    chunks, member_ranges = [], []

    body = next((c for c in def_node.children if c.type == "declaration_list"), None)
    if body is not None:
        for child in body.children:
            t_range, t_node = unwrap_template(child)
            if t_node.type == "function_definition":
                chunks.append(function_chunk(file_path, t_range, t_node, source_bytes, language))
                member_ranges.append((t_range.start_byte, t_range.end_byte))
            elif t_node.type in ("declaration", "field_declaration") and is_function_declaration(t_node):
                chunks.append(function_chunk(file_path, t_range, t_node, source_bytes, language))
                member_ranges.append((t_range.start_byte, t_range.end_byte))
            elif t_node.type in ("class_specifier", "struct_specifier"):
                chunks.extend(class_or_struct_chunks(file_path, t_range, t_node, source_bytes, language))
                member_ranges.append((t_range.start_byte, t_range.end_byte))

    shell_text = source_with_exclusions(
        source_bytes, range_node.start_byte, range_node.end_byte, member_ranges
    ).strip()

    if not shell_text:
        shell_text = f"namespace {ns_name} {{ ... }}"

    chunks.append(Chunk(
        file_path=file_path, chunk_type="namespace", name=ns_name, parent_class=None,
        language=language, start_line=range_node.start_point[0] + 1,
        end_line=range_node.end_point[0] + 1, source=shell_text,
    ))
    return chunks

def chunk_cpp_file(file_path: str, source_code: str) -> list[Chunk]:
    source_bytes = source_code.encode("utf8")
    root = _PARSER.parse(source_bytes).root_node

    chunks: list[Chunk] = []
    top_level_ranges: list[tuple[int, int]] = []

    for node in root.children:
        range_node, def_node = unwrap_template(node)

        if def_node.type == "function_definition":
            chunks.append(function_chunk(file_path, range_node, def_node, source_bytes, "cpp"))
            top_level_ranges.append((range_node.start_byte, range_node.end_byte))
        elif def_node.type == "declaration" and is_function_declaration(def_node):
            chunks.append(function_chunk(file_path, range_node, def_node, source_bytes, "cpp"))
            top_level_ranges.append((range_node.start_byte, range_node.end_byte))
        elif def_node.type in ("class_specifier", "struct_specifier"):
            chunks.extend(class_or_struct_chunks(file_path, range_node, def_node, source_bytes, "cpp"))
            top_level_ranges.append((range_node.start_byte, range_node.end_byte))
        elif def_node.type == "namespace_definition":
            chunks.extend(namespace_chunks(file_path, range_node, def_node, source_bytes, "cpp"))
            top_level_ranges.append((range_node.start_byte, range_node.end_byte))

    module_text = source_with_exclusions(
        source_bytes, root.start_byte, root.end_byte, top_level_ranges
    ).strip()
    if module_text:
        chunks.append(Chunk(
            file_path=file_path, chunk_type="module_level", name="<module_top_level>",
            parent_class=None, language="cpp", start_line=root.start_point[0] + 1,
            end_line=root.end_point[0] + 1, source=module_text,
        ))
        
    return chunks