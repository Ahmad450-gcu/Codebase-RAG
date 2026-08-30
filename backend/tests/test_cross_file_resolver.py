from app.chunking.common import Chunk
from app.graph.common import CallEdge
from app.graph.cross_file_resolver import resolve_python_cross_file_calls
from app.graph.import_extractor import ImportBinding
from app.graph.module_index import build_module_index

def _chunk(file_path, name):
    return Chunk(file_path=file_path, chunk_type="function", name=name, parent_class=None,
                 language="python", start_line=1, end_line=2, source="pass")

def test_from_import_call_resolves_cross_file():
    chunks_by_file = {"app/utils.py": [_chunk("app/utils.py", "helper")]}
    bindings = {"app/main.py": [ImportBinding(local_name="helper", target_module="app.utils", imported_name="helper")]}
    module_index = build_module_index(["app/utils.py", "app/main.py"])

    edge = CallEdge(
        file_path="app/main.py", caller_name="caller", caller_parent_class=None,
        callee_name="helper", call_type="plain", resolved=False,
        target_name=None, target_parent_class=None,
    )
    resolved = resolve_python_cross_file_calls([edge], chunks_by_file, bindings, module_index)
    assert resolved[0].resolved is True
    assert resolved[0].target_file == "app/utils.py"

def test_aliased_module_attribute_call_resolves_cross_file():
    chunks_by_file = {"app/utils.py": [_chunk("app/utils.py", "helper")]}
    bindings = {"app/main.py": [ImportBinding(local_name="utils", target_module="app.utils", imported_name=None)]}
    module_index = build_module_index(["app/utils.py", "app/main.py"])

    edge = CallEdge(
        file_path="app/main.py", caller_name="caller", caller_parent_class=None,
        callee_name="helper", call_type="attribute", resolved=False,
        target_name=None, target_parent_class=None, object_name="utils",
    )
    resolved = resolve_python_cross_file_calls([edge], chunks_by_file, bindings, module_index)
    assert resolved[0].resolved is True
    assert resolved[0].target_file == "app/utils.py"

def test_import_with_no_matching_function_stays_unresolved():
    chunks_by_file = {"app/utils.py": [_chunk("app/utils.py", "other_func")]}
    bindings = {"app/main.py": [ImportBinding(local_name="helper", target_module="app.utils", imported_name="helper")]}
    module_index = build_module_index(["app/utils.py"])

    edge = CallEdge(
        file_path="app/main.py", caller_name="caller", caller_parent_class=None,
        callee_name="helper", call_type="plain", resolved=False,
        target_name=None, target_parent_class=None,
    )
    resolved = resolve_python_cross_file_calls([edge], chunks_by_file, bindings, module_index)
    assert resolved[0].resolved is False

def test_already_resolved_edge_is_left_untouched():
    edge = CallEdge(
        file_path="m.py", caller_name="a", caller_parent_class=None,
        callee_name="b", call_type="plain", resolved=True,
        target_name="b", target_parent_class=None,
    )
    resolved = resolve_python_cross_file_calls([edge], {}, {}, {})
    assert resolved[0] is edge