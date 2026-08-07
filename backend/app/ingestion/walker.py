import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional
import pathspec
from app.config import DEFAULT_IGNORED_DIRS, MAX_FILE_SIZE_BYTES

@dataclass(frozen=True)
class FileEntry:
    absolute_path: Path
    relative_path: str  
    size_bytes: int
    modified_time: float

def load_gitignore_spec(repo_root: Path) -> Optional[pathspec.PathSpec]:
    gitignore_path = repo_root /".gitignore"
    if not gitignore_path.exists():
        return None
    lines = gitignore_path.read_text(errors="ignore").splitlines()
    return pathspec.PathSpec.from_lines("gitignore", lines)

def is_probably_binary(path: Path, sniff_bytes: int = 1024) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(sniff_bytes)
    except OSError:
        return True 
    return b"\x00" in chunk

#  walks a repo and yield every FileEntry worth considering for ingestion.
def walk_repository(repo_root: str | Path) -> Iterator[FileEntry]:
    repo_root = Path(repo_root).resolve()
    if not repo_root.is_dir():
        raise ValueError(f"{repo_root} is not a directory")
    gitignore_spec = load_gitignore_spec(repo_root)

    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = sorted(d for d in dirnames if d not in DEFAULT_IGNORED_DIRS)
        filenames = sorted(filenames)

        for filename in filenames:
            absolute_path = Path(dirpath) / filename
            relative_path = absolute_path.relative_to(repo_root).as_posix()
            if gitignore_spec and gitignore_spec.match_file(relative_path):
                continue
            try:
                stat = absolute_path.stat()
            except OSError:
                continue
            if stat.st_size == 0 or stat.st_size > MAX_FILE_SIZE_BYTES:
                continue
            if is_probably_binary(absolute_path):
                continue
            
            yield FileEntry(absolute_path=absolute_path, relative_path=relative_path, size_bytes=stat.st_size, modified_time=stat.st_mtime,)