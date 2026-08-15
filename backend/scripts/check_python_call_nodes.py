import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def dump(node, source_bytes, depth=0, max_depth=5):
    if depth > max_depth:
        return
    if node.is_named:
        text_preview = source_bytes[node.start_byte:node.end_byte].decode("utf8").split("\n")[0][:40]
        print("  " * depth + f"{node.type} -> {text_preview!r}")
    for child in node.children:
        dump(child, source_bytes, depth + 1, max_depth)


sample = b"""
def helper():
    pass

def caller():
    helper()

class Greeter:
    def greet(self):
        self.helper_method()
        print(self.name)

    def helper_method(self):
        pass

def uses_module_call():
    os.path.join("a", "b")
"""

tree = parser.parse(sample)
dump(tree.root_node, sample)