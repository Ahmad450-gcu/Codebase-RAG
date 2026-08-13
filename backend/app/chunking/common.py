from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Chunk:
    file_path: str
    chunk_type: str        
    name: str
    parent_class: Optional[str]
    language: str
    start_line: int
    end_line: int
    source: str

def source_with_exclusions(source_bytes: bytes, start_byte: int, end_byte: int, exclude_ranges: list[tuple[int, int]]) -> str:
    parts = []
    cursor = start_byte
    for ex_start, ex_end in sorted(exclude_ranges):
        if ex_start > cursor:
            parts.append(source_bytes[cursor:ex_start])
        cursor = max(cursor, ex_end)
    if cursor < end_byte:
        parts.append(source_bytes[cursor:end_byte])
    return b"".join(parts).decode("utf8")