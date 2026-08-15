from app.chunking.js_ts_chunker import chunk_js_ts_file
from app.graph.js_ts_call_extractor import extract_intra_file_calls

def test_plain_call_resolves_within_same_file():
    code = "function helper() {}\n\nfunction caller() {\n  helper();\n}\n"
    chunks = chunk_js_ts_file("m.js", code, "javascript")
    edges = extract_intra_file_calls("m.js", chunks, "javascript")

    plain_edges = [e for e in edges if e.call_type == "plain"]
    assert len(plain_edges) == 1
    assert plain_edges[0].callee_name == "helper"
    assert plain_edges[0].resolved is True

def test_this_method_call_resolves_within_same_class():
    code = '''class Greeter {
  greet() {
    this.helperMethod();
  }

  helperMethod() {}
}
'''
    chunks = chunk_js_ts_file("g.js", code, "javascript")
    edges = extract_intra_file_calls("g.js", chunks, "javascript")

    instance_edges = [e for e in edges if e.call_type == "instance_method"]
    assert len(instance_edges) == 1
    assert instance_edges[0].callee_name == "helperMethod"
    assert instance_edges[0].resolved is True
    assert instance_edges[0].target_parent_class == "Greeter"

def test_call_on_external_object_is_unresolved():
    code = "function useConsole() {\n  console.log('hi');\n}\n"
    chunks = chunk_js_ts_file("m.js", code, "javascript")
    edges = extract_intra_file_calls("m.js", chunks, "javascript")

    attr_edges = [e for e in edges if e.call_type == "attribute"]
    assert len(attr_edges) == 1
    assert attr_edges[0].callee_name == "log"
    assert attr_edges[0].resolved is False

def test_this_call_to_method_not_in_file_is_unresolved():
    code = "class Widget {\n  render() {\n    this.missingMethod();\n  }\n}\n"
    chunks = chunk_js_ts_file("w.js", code, "javascript")
    edges = extract_intra_file_calls("w.js", chunks, "javascript")

    instance_edges = [e for e in edges if e.call_type == "instance_method"]
    assert len(instance_edges) == 1
    assert instance_edges[0].resolved is False

def test_arrow_function_calls_are_also_scanned():
    code = "function helper() {}\n\nconst caller = () => {\n  helper();\n};\n"
    chunks = chunk_js_ts_file("m.js", code, "javascript")
    edges = extract_intra_file_calls("m.js", chunks, "javascript")

    plain_edges = [e for e in edges if e.call_type == "plain"]
    assert len(plain_edges) == 1
    assert plain_edges[0].callee_name == "helper"
    assert plain_edges[0].resolved is True