# Scenario: Implement a markdown table-of-contents generator

## Setup
You are working on a utility that parses markdown and generates a table of contents.

## Prompt
Implement a function `generate_toc(markdown: str) -> str` that:
- Parses heading lines (# through ####)
- Generates a nested, indented TOC with links
- Handles duplicate headings by appending -1, -2, etc.
- Returns the TOC as a markdown string

## Expected WITHOUT skill (baseline)
Agent writes the complete implementation in one pass without decomposing into holes.

## Expected WITH skill
Agent decomposes: skeleton first, identifies sub-problems (parsing headings, slugifying, deduplication, indentation) as holes, fills them one at a time.
