from app.chunking.js_ts_chunker import chunk_js_ts_file

def test_function_declaration():
    code = "function add(a, b) {\n  return a + b;\n}\n"
    funcs = [c for c in chunk_js_ts_file("m.js", code, "javascript") if c.chunk_type == "function"]
    assert len(funcs) == 1
    assert funcs[0].name == "add"

def test_arrow_function_const_is_first_class_function():
    code = "const multiply = (a, b) => a * b;\n"
    funcs = [c for c in chunk_js_ts_file("m.js", code, "javascript") if c.chunk_type == "function"]
    assert len(funcs) == 1
    assert funcs[0].name == "multiply"
    assert "=>" in funcs[0].source

def test_class_with_methods_no_duplication():
    code = '''class Greeter {
  constructor(name) {
    this.name = name;
  }
  greet() {
    return `Hello, ${this.name}`;
  }
}
'''
    chunks = chunk_js_ts_file("g.js", code, "javascript")
    methods = [c for c in chunks if c.chunk_type == "method"]
    classes = [c for c in chunks if c.chunk_type == "class"]

    assert {m.name for m in methods} == {"constructor", "greet"}
    assert all(m.parent_class == "Greeter" for m in methods)
    assert len(classes) == 1
    assert "this.name = name" not in classes[0].source  # no duplication

def test_typescript_interface_is_type_definition():
    code = "interface Point {\n  x: number;\n  y: number;\n}\n"
    chunks = chunk_js_ts_file("p.ts", code, "typescript")
    type_defs = [c for c in chunks if c.chunk_type == "type_definition"]
    assert len(type_defs) == 1
    assert type_defs[0].name == "Point"

def test_typescript_type_alias_is_type_definition():
    code = "type ID = string | number;\n"
    chunks = chunk_js_ts_file("id.ts", code, "typescript")
    type_defs = [c for c in chunks if c.chunk_type == "type_definition"]
    assert len(type_defs) == 1
    assert type_defs[0].name == "ID"

def test_typed_arrow_function():
    code = "const double = (n: number): number => n * 2;\n"
    funcs = [c for c in chunk_js_ts_file("d.ts", code, "typescript") if c.chunk_type == "function"]
    assert len(funcs) == 1
    assert funcs[0].name == "double"

def test_module_level_statements_captured():
    code = 'import { readFileSync } from "fs";\n\nfunction main() {\n  return 1;\n}\n'
    module_chunks = [c for c in chunk_js_ts_file("a.ts", code, "typescript") if c.chunk_type == "module_level"]
    assert len(module_chunks) == 1
    assert "import" in module_chunks[0].source
    assert "function main" not in module_chunks[0].source

def test_multi_declarator_const_left_as_module_level():
    code = "const a = 1, b = 2;\n"
    chunks = chunk_js_ts_file("m.ts", code, "typescript")
    assert len([c for c in chunks if c.chunk_type == "function"]) == 0
    assert any(c.chunk_type == "module_level" for c in chunks)