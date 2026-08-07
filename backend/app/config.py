DEFAULT_IGNORED_DIRS = {
    ".git", ".svn", ".hg",
    "node_modules", "__pycache__", ".venv", "venv", "env", "myenv", "myvenv"
    "build", "dist", "out", "target",
    ".idea", ".vscode", ".pytest_cache", ".mypy_cache",
    "vendor",
}

EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hxx": "cpp",
    ".h": "cpp",
}

MARKDOWN_EXTENSIONS = {".md", ".markdown", ".mdx"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB