import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def dump(node, source_bytes, depth=0):
    text_preview = source_bytes[node.start_byte:node.end_byte].decode("utf8").split("\n")[0][:50]
    print("  " * depth + f"{node.type}   -> {text_preview!r}")
    for child in node.children:
        dump(child, source_bytes, depth + 1)

samples = [
    ("import os", b"import os"),
    ("import numpy as np", b"import numpy as np"),
    ("from app.utils import helper", b"from app.utils import helper"),
    ("from app.utils import helper as h", b"from app.utils import helper as h"),
    ("from . import foo", b"from . import foo"),
    ("from .utils import bar", b"from .utils import bar"),
]

for label, code in samples:
    print("=" * 15, label, "=" * 15)
    tree = parser.parse(code)
    dump(tree.root_node, code)
    print()