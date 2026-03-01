import re


def generate_toc(markdown: str) -> str:
    """Parse markdown headings (# through ####) and generate a table of contents.

    Returns a markdown string with nested, indented links.
    Duplicate headings get -1, -2, etc. appended to their slugs.
    """
    headings = _extract_headings(markdown)
    toc_entries: list[str] = []
    slug_counts: dict[str, int] = {}

    for level, text in headings:
        slug = _make_slug(text)
        slug = _deduplicate_slug(slug, slug_counts)
        toc_entries.append(_format_entry(level, text, slug))

    return "\n".join(toc_entries)


def _extract_headings(markdown: str) -> list[tuple[int, str]]:
    headings = []
    for line in markdown.splitlines():
        match = re.match(r"^(#{1,4})\s+(.+)$", line)
        if match:
            headings.append((len(match.group(1)), match.group(2).strip()))
    return headings


def _make_slug(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s]+", "-", slug).strip("-")


def _deduplicate_slug(slug: str, slug_counts: dict[str, int]) -> str:
    if slug in slug_counts:
        slug_counts[slug] += 1
        return f"{slug}-{slug_counts[slug]}"
    else:
        slug_counts[slug] = 0
        return slug


def _format_entry(level: int, text: str, slug: str) -> str:
    indent = "  " * (level - 1)
    return f"{indent}- [{text}](#{slug})"


if __name__ == "__main__":
    sample = """\
# Introduction
## Getting Started
## Installation
### Prerequisites
### Steps
## Getting Started
# API Reference
## Methods
### get
### set
### get
#### Details
"""
    print(generate_toc(sample))
