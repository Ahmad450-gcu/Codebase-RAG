def node_id(file_path: str, name: str, parent_class: str | None = None) -> str:
    if parent_class:
        return f"{file_path}::{parent_class}.{name}"
    return f"{file_path}::{name}"