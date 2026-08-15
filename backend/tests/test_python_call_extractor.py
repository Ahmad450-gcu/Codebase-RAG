from app.chunking.python_chunker import chunk_python_file
from app.graph.python_call_extractor import extract_intra_file_calls

def test_plain_call_resolves_within_same_file():
    code = "def helper():\n    pass\n\ndef caller():\n    helper()\n"
    chunks = chunk_python_file("m.py", code)
    edges = extract_intra_file_calls("m.py", chunks)

    plain_edges = [e for e in edges if e.call_type == "plain"]
    assert len(plain_edges) == 1
    assert plain_edges[0].callee_name == "helper"
    assert plain_edges[0].resolved is True
    assert plain_edges[0].target_name == "helper"

def test_instance_method_call_resolves_within_same_class():
    code = '''class Greeter:
    def greet(self):
        self.helper_method()

    def helper_method(self):
        pass
'''
    chunks = chunk_python_file("g.py", code)
    edges = extract_intra_file_calls("g.py", chunks)

    self_edges = [e for e in edges if e.call_type == "instance_method"]
    assert len(self_edges) == 1
    assert self_edges[0].callee_name == "helper_method"
    assert self_edges[0].resolved is True
    assert self_edges[0].target_parent_class == "Greeter"

def test_call_on_external_module_is_unresolved():
    code = "def uses_os():\n    os.path.join('a', 'b')\n"
    chunks = chunk_python_file("m.py", code)
    edges = extract_intra_file_calls("m.py", chunks)

    attr_edges = [e for e in edges if e.call_type == "attribute"]
    assert len(attr_edges) == 1
    assert attr_edges[0].callee_name == "join"
    assert attr_edges[0].resolved is False

def test_self_call_to_method_not_in_file_is_unresolved():
    code = "class Widget:\n    def render(self):\n        self.missing_method()\n"
    chunks = chunk_python_file("w.py", code)
    edges = extract_intra_file_calls("w.py", chunks)

    self_edges = [e for e in edges if e.call_type == "instance_method"]
    assert len(self_edges) == 1
    assert self_edges[0].resolved is False

def test_nested_call_in_arguments_is_also_found():
    code = "def outer():\n    pass\n\ndef inner():\n    pass\n\ndef caller():\n    outer(inner())\n"
    chunks = chunk_python_file("m.py", code)
    edges = extract_intra_file_calls("m.py", chunks)

    plain_edges = {e.callee_name for e in edges if e.call_type == "plain"}
    assert plain_edges == {"outer", "inner"}

def test_module_level_code_is_not_scanned():
    code = "def helper():\n    pass\n\nhelper()\n" 
    chunks = chunk_python_file("m.py", code)
    edges = extract_intra_file_calls("m.py", chunks)
    assert len(edges) == 0  