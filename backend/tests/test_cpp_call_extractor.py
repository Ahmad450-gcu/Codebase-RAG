from app.chunking.cpp_chunker import chunk_cpp_file
from app.graph.cpp_call_extractor import extract_intra_file_calls

def test_plain_call_resolves_within_same_file():
    code = "void helper() {}\n\nvoid caller() {\n    helper();\n}\n"
    chunks = chunk_cpp_file("m.cpp", code)
    edges = extract_intra_file_calls("m.cpp", chunks)

    plain_edges = [e for e in edges if e.call_type == "plain"]
    assert len(plain_edges) == 1
    assert plain_edges[0].callee_name == "helper"
    assert plain_edges[0].resolved is True

def test_this_arrow_method_call_resolves_within_same_class():
    code = '''class Greeter {
public:
    void greet() {
        this->helperMethod();
    }
    void helperMethod() {}
};
'''
    chunks = chunk_cpp_file("g.cpp", code)
    edges = extract_intra_file_calls("g.cpp", chunks)

    instance_edges = [e for e in edges if e.call_type == "instance_method"]
    assert len(instance_edges) == 1
    assert instance_edges[0].callee_name == "helperMethod"
    assert instance_edges[0].resolved is True
    assert instance_edges[0].target_parent_class == "Greeter"


def test_out_of_line_method_calls_are_scanned_too():
    code = '''class Widget {
public:
    void render();
    void helperMethod();
};

void Widget::render() {
    this->helperMethod();
}
'''
    chunks = chunk_cpp_file("w.cpp", code)
    edges = extract_intra_file_calls("w.cpp", chunks)

    instance_edges = [e for e in edges if e.call_type == "instance_method"]
    assert len(instance_edges) == 1
    assert instance_edges[0].caller_name == "render"
    assert instance_edges[0].resolved is True

def test_call_on_external_object_is_unresolved():
    code = 'void useStream() {\n    std::cout << "hi";\n    someObj.doThing();\n}\n'
    chunks = chunk_cpp_file("m.cpp", code)
    edges = extract_intra_file_calls("m.cpp", chunks)

    attr_edges = [e for e in edges if e.call_type == "attribute"]
    assert any(e.callee_name == "doThing" and e.resolved is False for e in attr_edges)

def test_this_arrow_call_to_method_not_in_file_is_unresolved():
    code = "class Widget {\npublic:\n    void render() {\n        this->missingMethod();\n    }\n};\n"
    chunks = chunk_cpp_file("w.cpp", code)
    edges = extract_intra_file_calls("w.cpp", chunks)
    instance_edges = [e for e in edges if e.call_type == "instance_method"]
    assert len(instance_edges) == 1
    assert instance_edges[0].resolved is False