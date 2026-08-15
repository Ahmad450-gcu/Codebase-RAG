import tree_sitter_javascript as tsjs
from tree_sitter import Language, Parser

JS_LANGUAGE = Language(tsjs.language())
parser = Parser(JS_LANGUAGE)

def dump(node, source_bytes, depth=0):
    text_preview = source_bytes[node.start_byte:node.end_byte].decode("utf8").split("\n")[0][:40]
    print("  " * depth + f"{node.type}   -> {text_preview!r}")
    for child in node.children:
        dump(child, source_bytes, depth + 1)

print("=" * 15, "plain call: helper()", "=" * 15)
s1 = b"helper();"
t1 = parser.parse(s1)
dump(t1.root_node, s1)

print()
print("=" * 15, "this.method()", "=" * 15)
s2 = b"this.helperMethod();"
t2 = parser.parse(s2)
dump(t2.root_node, s2)

print()
print("=" * 15, "field check on this.method()", "=" * 15)
call_node = t2.root_node.children[0].children[0]
print(f"call node type: {call_node.type}")
func_field = call_node.child_by_field_name("function")
print(f"function field: {func_field}, type={func_field.type if func_field else None}")
if func_field and func_field.type == "member_expression":
    print(f"  object field: {func_field.child_by_field_name('object')}")
    print(f"  property field: {func_field.child_by_field_name('property')}")