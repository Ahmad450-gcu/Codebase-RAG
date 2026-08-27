from app.graph.import_extractor import ImportBinding, extract_imports

def test_plain_import():
    assert extract_imports("import os\n") == [
        ImportBinding(local_name="os", target_module="os", imported_name=None)
    ]

def test_aliased_import():
    assert extract_imports("import numpy as np\n") == [
        ImportBinding(local_name="np", target_module="numpy", imported_name=None)
    ]

def test_from_import():
    assert extract_imports("from app.utils import helper\n") == [
        ImportBinding(local_name="helper", target_module="app.utils", imported_name="helper")
    ]

def test_from_import_with_alias():
    assert extract_imports("from app.utils import helper as h\n") == [
        ImportBinding(local_name="h", target_module="app.utils", imported_name="helper")
    ]

def test_from_import_multiple_names():
    bindings = extract_imports("from app.utils import a, b\n")
    assert {b.local_name for b in bindings} == {"a", "b"}
    assert all(b.target_module == "app.utils" for b in bindings)

def test_relative_import_is_skipped():
    assert extract_imports("from . import foo\n") == []

def test_relative_import_with_module_is_skipped():
    assert extract_imports("from .utils import bar\n") == []

def test_dotted_plain_import_without_alias_is_skipped():
    assert extract_imports("import app.utils\n") == []