from app.graph.module_index import build_module_index, module_path

def test_simple_file():
    assert module_path("app/chunking/common.py") == "app.chunking.common"

def test_init_file_maps_to_package():
    assert module_path("app/__init__.py") == "app"

def test_nested_init_file():
    assert module_path("app/chunking/__init__.py") == "app.chunking"

def test_build_module_index():
    index = build_module_index(["app/chunking/common.py", "app/__init__.py"])
    assert index["app.chunking.common"] == "app/chunking/common.py"
    assert index["app"] == "app/__init__.py"