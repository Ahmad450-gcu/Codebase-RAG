from app.chunking.python_chunker import chunk_python_file

def test_simple_function():
    code = "def add(a, b):\n    return a + b\n"
    funcs = [c for c in chunk_python_file("m.py", code) if c.chunk_type == "function"]
    assert len(funcs) == 1
    assert funcs[0].name == "add"

def test_decorated_function_keeps_decorator():
    code = "@staticmethod\ndef helper():\n    pass\n"
    funcs = [c for c in chunk_python_file("m.py", code) if c.chunk_type == "function"]
    assert len(funcs) == 1
    assert funcs[0].source.startswith("@staticmethod")

def test_class_with_methods_no_duplication():
    code = '''class Greeter:
    """Greets people."""

    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, {self.name}"
'''
    chunks = chunk_python_file("g.py", code)
    methods = [c for c in chunks if c.chunk_type == "method"]
    classes = [c for c in chunks if c.chunk_type == "class"]

    assert {m.name for m in methods} == {"__init__", "greet"}
    assert all(m.parent_class == "Greeter" for m in methods)
    assert len(classes) == 1
    assert "Greets people" in classes[0].source
    assert "self.name = name" not in classes[0].source  # no duplication

def test_decorated_method_inside_class():
    code = "class Config:\n    @property\n    def value(self):\n        return 42\n"
    methods = [c for c in chunk_python_file("c.py", code) if c.chunk_type == "method"]
    assert len(methods) == 1
    assert methods[0].source.startswith("@property")
    assert methods[0].parent_class == "Config"

def test_class_with_no_methods_still_produces_class_chunk():
    code = 'class Point:\n    """A 2D point."""\n    x: int\n    y: int\n'
    chunks = chunk_python_file("p.py", code)
    assert len([c for c in chunks if c.chunk_type == "method"]) == 0
    classes = [c for c in chunks if c.chunk_type == "class"]
    assert len(classes) == 1
    assert "A 2D point" in classes[0].source

def test_module_level_statements_captured():
    code = 'import os\n\nVERSION = "1.0"\n\ndef main():\n    pass\n'
    module_chunks = [c for c in chunk_python_file("a.py", code) if c.chunk_type == "module_level"]
    assert len(module_chunks) == 1
    assert "import os" in module_chunks[0].source
    assert "def main" not in module_chunks[0].source

def test_file_with_only_definitions_has_no_module_level_chunk():
    code = "def a():\n    pass\n\ndef b():\n    pass\n"
    module_chunks = [c for c in chunk_python_file("d.py", code) if c.chunk_type == "module_level"]
    assert len(module_chunks) == 0