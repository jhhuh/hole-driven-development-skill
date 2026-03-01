import json
from typing import Any


def process_log_file(path: str) -> dict[str, Any]:
    """
    Read a log file, parse each line as JSON, group entries by level
    (INFO/WARN/ERROR), compute statistics (count per level, avg message
    length), and return a summary dict.
    """
    # HOLE_1 filled: read file and parse each line as JSON -> list[dict]
    with open(path) as f:
        entries = [json.loads(line) for line in f]

    # HOLE_2 filled: group parsed entries by level -> dict[str, list[dict]]
    grouped: dict[str, list[dict]] = {}
    for entry in entries:
        level = entry["level"]
        grouped.setdefault(level, []).append(entry)

    # HOLE_3 filled: compute stats and build summary dict -> dict[str, Any]
    summary: dict[str, Any] = {}
    for level, level_entries in grouped.items():
        count = len(level_entries)
        avg_msg_len = sum(len(e["message"]) for e in level_entries) / count
        summary[level] = {"count": count, "avg_message_length": avg_msg_len}

    return summary
