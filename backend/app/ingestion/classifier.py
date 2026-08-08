# For now, this is just a simple classifier based on file extensions. In the future, it can be extended to implement more complex classification like we may sneak peek the file a little to perform content-based classification

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional
from app.config import CONFIG_EXTENSIONS, EXTENSION_LANGUAGE_MAP, MARKDOWN_EXTENSIONS
from app.ingestion.walker import FileEntry, walk_repository

@dataclass(frozen=True)
class ClassifiedFile:
    relative_path: str
    absolute_path: Path
    size_bytes: int
    modified_time: float
    category: str                  
    language: Optional[str]        # It will be set only when category is code.

def classify_file(entry: FileEntry) -> ClassifiedFile:
    extension = entry.absolute_path.suffix.lower()
    if extension in EXTENSION_LANGUAGE_MAP:
        category, language = "code", EXTENSION_LANGUAGE_MAP[extension]
    elif extension in MARKDOWN_EXTENSIONS:
        category, language = "markdown", None
    elif extension in CONFIG_EXTENSIONS:
        category, language = "config", None
    else:
        category, language = "other", None
    return ClassifiedFile(
        relative_path=entry.relative_path,
        absolute_path=entry.absolute_path,
        size_bytes=entry.size_bytes,
        modified_time=entry.modified_time,
        category=category,
        language=language,
    )

def classify_repository(repo_root: str) -> Iterator[ClassifiedFile]:
    for entry in walk_repository(repo_root):
        yield classify_file(entry)