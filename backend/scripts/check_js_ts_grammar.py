import tree_sitter_javascript as tsjs
import tree_sitter_typescript as tsts
from tree_sitter import Language, Parser

JS_LANGUAGE = Language(tsjs.language())
TS_LANGUAGE = Language(tsts.language_typescript())

def dump(node, source_bytes, depth=0, max_depth=4):
    if depth > max_depth:
        return
    if node.is_named:
        text_preview = source_bytes[node.start_byte:node.end_byte].decode("utf8").split("\n")[0][:40]
        print("  " * depth + f"{node.type}   -> {text_preview!r}")
    for child in node.children:
        dump(child, source_bytes, depth + 1, max_depth)

js_sample = b"""
function add(a, b) {
  return a + b;
}

const multiply = (a, b) => a * b;

class Greeter {
  constructor(name) {
    this.name = name;
  }

  greet() {
    return `Hello, ${this.name}`;
  }
}
"""

ts_sample = b"""
interface Point {
  x: number;
  y: number;
}

type ID = string | number;

const double = (n: number): number => n * 2;
"""

print("=" * 20, "JAVASCRIPT", "=" * 20)
parser = Parser(JS_LANGUAGE)
tree = parser.parse(js_sample)
dump(tree.root_node, js_sample)
print()
print("=" * 20, "TYPESCRIPT", "=" * 20)
parser = Parser(TS_LANGUAGE)
tree = parser.parse(ts_sample)
dump(tree.root_node, ts_sample)