import tree_sitter_javascript as tsjs
from tree_sitter import Language, Parser

JS_LANGUAGE = Language(tsjs.language())
PARSER = Parser(JS_LANGUAGE)

def dump (node, source_bytes, depth=0):
    text_preview = source_bytes[node.start_byte:node.end_byte].decode("utf-8").split('\n')[0][50]
    print("  " * depth + f"{node.type}  -> {text_preview!r}")
    for child in node.children:
        dump(child, source_bytes, depth + 1)

samples = [
    ("default import", b"import foo from './utils';"),
    ("named import", b"import { helper } from './utils';"),
    ("named import with alias", b"import { helper as h } from './utils';"),
    ("multiple named imports", b"import { a, b } from './utils';"),
    ("namespace import", b"import * as utils from './utils';"),
    ("default + named combined", b"import foo, { helper } from './utils';"),
    ("export default function", b"export default function foo() {}"),
    ("export named function", b"export function foo() {}"),
    ("export named const", b"export const foo = () => {};"),
    ("export named class", b"export class Foo {}"),
]

for label, code in samples:
    print("=" * 15, label, "=" * 15)
    tree = PARSER.parse(code)
    dump(tree.root_node, code)
    print()