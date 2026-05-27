import re
from typing import Iterable

SECTION_HEADERS = {
    "experience",
    "skills",
    "education",
    "projects",
    "summary",
    "certifications",
}


def _is_header(line: str) -> str | None:
    normalized = re.sub(r"[^a-z ]", "", line.lower()).strip()
    if normalized in SECTION_HEADERS:
        return normalized
    return None


def _chunk_text(text: str, max_chars: int = 1000, overlap: int = 100) -> Iterable[str]:
    if len(text) <= max_chars:
        yield text
        return

    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        yield text[start:end]
        if end == len(text):
            break
        start = max(end - overlap, 0)


def chunk_sections(text: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in text.splitlines()]
    sections: list[dict[str, str]] = []

    current_section = "general"
    current_lines: list[str] = []

    for line in lines:
        if not line:
            continue
        header = _is_header(line)
        if header:
            if current_lines:
                sections.append(
                    {"section": current_section, "text": "\n".join(current_lines)}
                )
            current_section = header
            current_lines = []
            continue
        current_lines.append(line)

    if current_lines:
        sections.append({"section": current_section, "text": "\n".join(current_lines)})

    chunks: list[dict[str, str]] = []
    for section in sections:
        for chunk in _chunk_text(section["text"]):
            if chunk.strip():
                chunks.append({"section": section["section"], "text": chunk.strip()})

    return chunks
