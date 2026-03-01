import json
from typing import Any


def process_log_file(path: str) -> dict[str, Any]:
    """
    Read a log file, parse each line as JSON, group entries by level
    (INFO/WARN/ERROR), compute statistics (count per level, avg message
    length), and return a summary dict.
    """
    raw_lines = _read_lines(path)
    entries = _parse_entries(raw_lines)
    grouped = _group_by_level(entries)
    stats = _compute_stats(grouped)
    return _assemble_result(grouped, stats)


def _read_lines(path: str) -> list[str]:
    with open(path) as f:
        return [line for line in f.read().splitlines() if line.strip()]


def _parse_entries(raw_lines: list[str]) -> list[dict[str, Any]]:
    return [json.loads(line) for line in raw_lines]


def _group_by_level(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        level = entry["level"]
        grouped.setdefault(level, []).append(entry)
    return grouped


def _compute_stats(grouped: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}
    for level, entries in grouped.items():
        count = len(entries)
        avg_msg_len = sum(len(e["message"]) for e in entries) / count
        stats[level] = {"count": count, "avg_message_length": avg_msg_len}
    return stats


def _assemble_result(grouped: dict[str, list[dict[str, Any]]], stats: dict[str, dict[str, Any]]) -> dict[str, Any]:
    total = sum(s["count"] for s in stats.values())
    return {
        "total_entries": total,
        "levels": stats,
        "entries_by_level": grouped,
    }
