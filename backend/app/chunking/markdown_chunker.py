import re
from app.chunking.common import Chunk

_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_FENCE_RE = re.compile(r"^(```|~~~)")

def _find_headers(lines: list[str]) -> list[tuple[int, int, str]]:
    headers = []
    in_fence = False
    fence_marker = None
    for i, line in enumerate(lines):
        fence_match = _FENCE_RE.match(line.strip())
        if fence_match:
            marker = fence_match.group(1)
            if not in_fence:
                in_fence, fence_marker = True, marker
            elif marker == fence_marker:
                in_fence, fence_marker = False, None
            continue
        if in_fence:
            continue
        header_match = _HEADER_RE.match(line)
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()
            headers.append((i, level, title))
    return headers

def chunk_markdown_file(file_path: str, source_code: str) -> list[Chunk]:
    lines = source_code.splitlines()
    headers = _find_headers(lines)
    chunks: list[Chunk] = []
    first_header_line = headers[0][0] if headers else len(lines)
    preamble_text = "\n".join(lines[:first_header_line]).strip()
    if preamble_text:
        chunks.append(Chunk(
            file_path=file_path, chunk_type="preamble", name="<preamble>",
            parent_class=None, language="markdown",
            start_line=1, end_line=first_header_line, source=preamble_text,
        ))

    stack: list[tuple[int, str]] = []  # (level, title) - builds the breadcrumb

    for idx, (line_no, level, title) in enumerate(headers):
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        header_path = [t for _, t in stack]

        end_line = headers[idx + 1][0] if idx + 1 < len(headers) else len(lines)
        section_text = "\n".join(lines[line_no:end_line]).strip()

        chunks.append(Chunk(
            file_path=file_path, chunk_type="section", name=title,
            parent_class=None, language="markdown",
            start_line=line_no + 1, end_line=end_line, source=section_text,
            metadata={"header_path": header_path, "level": level},
        ))
    return chunks