import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

sample_code = b'''
def greet(name):
    """Say hello."""
    print(f"Hello, {name}")

class Greeter:
    def __init__(self, name):
        self.name = name

    def greet(self):
        greet(self.name)
'''

tree = parser.parse(sample_code)
root = tree.root_node

print(f"Root node type: {root.type}")
print(f"Has errors: {root.has_error}")
print(f"Child count: {root.child_count}")
print()
print("Top-level node types:")
for child in root.children:
    print(f"  {child.type}  (lines {child.start_point[0]+1}-{child.end_point[0]+1})")