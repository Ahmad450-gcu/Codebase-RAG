def module_path(relative_path: str) -> str:
    path = relative_path[:-3] if relative_path.endswith('.py') else relative_path # for example "backend/app/utils.py" becomes "backend/app/utils"
    parts = path.split('/') #for example "backend/app/utils" becomes ["backend", "app", "utils"].
    if parts[-1] == '__init__':
        parts = parts[:-1]
    return '.'.join(parts)

def build_module_index(python_file_paths: list[str]) -> dict[str, str]:
    return {module_path(p):p for p in python_file_paths}