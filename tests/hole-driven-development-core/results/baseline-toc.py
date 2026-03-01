import re


def generate_toc(markdown: str) -> str:
    """Parse markdown headings (# through ####) and generate a table of contents.

    Returns a markdown string with nested, indented links.
    Duplicate headings get -1, -2, etc. appended to their slugs.
    """
    lines = markdown.splitlines()
    toc_entries = []
    slug_counts: dict[str, int] = {}

    for line in lines:
        match = re.match(r"^(#{1,4})\s+(.+)$", line)
        if not match:
            continue

        level = len(match.group(1))
        text = match.group(2).strip()

        # GitHub-style slug: lowercase, strip non-alphanumeric (keep hyphens/spaces),
        # collapse spaces to single hyphens.
        slug = text.lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s]+", "-", slug).strip("-")

        # Handle duplicates: first occurrence is plain, subsequent get -1, -2, ...
        if slug in slug_counts:
            slug_counts[slug] += 1
            slug = f"{slug}-{slug_counts[slug]}"
        else:
            slug_counts[slug] = 0

        indent = "  " * (level - 1)
        toc_entries.append(f"{indent}- [{text}](#{slug})")

    return "\n".join(toc_entries)


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
