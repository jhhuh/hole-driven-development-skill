# Scenario: Implement a CSV parser with iterative reasoning

## Setup
Working in Python, no type checker configured.

## Prompt
Implement a function `parse_csv(text: str) -> list[dict[str, str]]` that:
- Splits into rows by newline
- Uses first row as headers
- Returns list of dicts mapping header to value
- Handles quoted fields with commas inside

## Expected WITHOUT skill (baseline)
Agent writes complete implementation without visible holes or
iterative decomposition.

## Expected WITH skill
Agent writes skeleton with HOLE markers visible in the file
(e.g., raise NotImplementedError("HOLE_1: ...")), then fills
them one at a time, reasoning about each hole's contract.
