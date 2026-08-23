from dataclasses import dataclass
from typing import Optional
from tree_sitter import Parser
from app.chunking.python_chunker import PY_LANGUAGE

PARSER = Parser(PY_LANGUAGE)

@dataclass(frozen=True)
class ImportBinding:
    local_name: str #  if I import writing e.g, import pandas as pd, the local_name is "pd"
    target_module: str # For import pandas as pd, the target_module is "pandas".
    imported_name: Optional[str] # Only for "from" import statements. For from math import sqrt, the imported_name is "sqrt". If it’s just a plain import math, this stays empty (None).

def text(node, source_bytes) -> str:
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8")

def handle_import_statement(node, source_bytes) -> list[ImportBinding]:
    bindings = []
    for child in node.children:
        if child.type == 'dotted-name':
            module = text(child, source_bytes)
            if '.' in module:
                continue 
            bindings.append(ImportBinding(local_name=module, target_module=module, imported_name=None))
        elif child.type == "aliased_import":
            module_node = child.child_by_field_name("name") or next(
                (c for c in child.children if c.type == 'dotted_name'), None
            )
            alias_node = next((c for c in child.children if c.type == 'identifier'), None)
            if module_node is not None and alias_node is not None:
                bindings.append(ImportBinding(
                local_name= text(alias_node, source_bytes),
                target_module= text(module_node, source_bytes),
                imported_name=None,
                ))
    return bindings

def handle_import_from_statements(node, source_bytes) -> list[ImportBinding]:
    import_index = next((i for i, c in enumerate(node.children) if c.type == "import"), None)
    if import_index is None:
        return []
    before = node.children[:import_index]
    if any(c.type == "relative_import" for c in before):
        return []
    module_node = next((c for c in before if c.type == "dotted_name"), None)
    if module_node is None:
        return []
    module = text(module_node, source_bytes)
    bindings = []
    for child in node.children[import_index + 1:]:
        if child.type == "dotted_name":
            name = text(child, source_bytes)
            bindings.append(ImportBinding(local_name=name, target_module=module, imported_name=name))
        elif child.type == 'aliased_import':
            name_node = next((c for c in child.children if c.type == "dotted_name"), None)
            alias_node = next((c for c in child.children if c.type == "identifier"), None)
            if name_node is not None and alias_node is not None:
                bindings.append(ImportBinding(
                    local_name= text(alias_node, source_bytes),
                    target_module=module,
                    imported_name= text(name_node, source_bytes),
                ))
    return bindings

def iterate_import_nodes(node):
    if node.type in ("import_statement", "import_from_statement"):
        yield node
        return
    for child in node.children:
        yield from iterate_import_nodes(child)