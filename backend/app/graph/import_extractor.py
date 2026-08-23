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