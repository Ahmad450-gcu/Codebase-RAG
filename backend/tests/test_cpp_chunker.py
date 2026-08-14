from app.chunking.cpp_chunker import chunk_cpp_file

def test_free_function():
    code = "int add(int a, int b) {\n    return a + b;\n}\n"
    funcs = [c for c in chunk_cpp_file("m.cpp", code) if c.chunk_type == "function"]
    assert len(funcs) == 1
    assert funcs[0].name == "add"
    assert funcs[0].parent_class is None

def test_class_with_inline_and_declaration_only_methods():
    code = '''class Shape {
public:
    Shape(double area);
    double getArea() const {
        return area_;
    }
private:
    double area_;
};
'''
    chunks = chunk_cpp_file("shape.h", code)
    methods = [c for c in chunks if c.chunk_type == "method"]
    classes = [c for c in chunks if c.chunk_type == "class"]

    assert {m.name for m in methods} == {"Shape", "getArea"}
    assert all(m.parent_class == "Shape" for m in methods)

    constructor = next(m for m in methods if m.name == "Shape")
    assert "area_" not in constructor.source  # declaration-only, no body

    get_area = next(m for m in methods if m.name == "getArea")
    assert "return area_;" in get_area.source

    assert len(classes) == 1
    assert "double area_;" in classes[0].source
    assert "return area_;" not in classes[0].source  # no duplication

def test_out_of_line_method_uses_qualified_name():
    code = "double Shape::getArea2() const {\n    return area_ * 2;\n}\n"
    chunks = chunk_cpp_file("shape.cpp", code)
    methods = [c for c in chunks if c.chunk_type == "method"]
    assert len(methods) == 1
    assert methods[0].name == "getArea2"
    assert methods[0].parent_class == "Shape"

def test_declaration_and_definition_in_separate_files_stay_independent():
    header_chunks = chunk_cpp_file("shape.h", "class Shape {\npublic:\n    double getArea() const;\n};\n")
    cpp_chunks = chunk_cpp_file("shape.cpp", "double Shape::getArea() const {\n    return 1.0;\n}\n")

    header_method = next(c for c in header_chunks if c.chunk_type == "method")
    cpp_method = next(c for c in cpp_chunks if c.chunk_type == "method")

    assert header_method.name == cpp_method.name == "getArea"
    assert header_method.parent_class == cpp_method.parent_class == "Shape"
    assert header_method.file_path != cpp_method.file_path
    assert "return" not in header_method.source
    assert "return" in cpp_method.source

def test_struct_with_no_methods_produces_class_chunk():
    code = "struct Point {\n    int x;\n    int y;\n};\n"
    chunks = chunk_cpp_file("point.h", code)
    assert len([c for c in chunks if c.chunk_type == "method"]) == 0
    classes = [c for c in chunks if c.chunk_type == "class"]
    assert len(classes) == 1
    assert classes[0].name == "Point"
    assert "int x;" in classes[0].source


def test_namespace_extracts_members_and_still_produces_namespace_chunk():
    code = '''namespace geometry {
    double square(double x) {
        return x * x;
    }

    class Circle {
    public:
        double radius;
    };
}
'''
    chunks = chunk_cpp_file("geo.h", code)
    namespaces = [c for c in chunks if c.chunk_type == "namespace"]
    functions = [c for c in chunks if c.chunk_type == "function"]
    classes = [c for c in chunks if c.chunk_type == "class"]

    assert len(namespaces) == 1
    assert namespaces[0].name == "geometry"
    assert len(functions) == 1
    assert functions[0].name == "square"
    assert len(classes) == 1
    assert classes[0].name == "Circle"
    assert "double radius;" in classes[0].source

def test_template_class_has_no_special_chunk_type():
    code = '''template<typename T>
class Container {
public:
    T get() { return value; }
private:
    T value;
};
'''
    chunks = chunk_cpp_file("container.h", code)
    classes = [c for c in chunks if c.chunk_type == "class"]
    methods = [c for c in chunks if c.chunk_type == "method"]

    assert len(classes) == 1
    assert classes[0].name == "Container"
    assert "template<typename T>" in classes[0].source  # template header preserved as plain text
    assert len(methods) == 1
    assert methods[0].name == "get"
    assert methods[0].parent_class == "Container"