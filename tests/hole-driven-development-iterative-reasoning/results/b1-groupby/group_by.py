def group_by(items: list[dict], key: str) -> dict[str, list[dict]]:
    """Group a list of dicts by a given key."""
    result: dict[str, list[dict]] = {}
    for item in items:
        result.setdefault(item[key], []).append(item)
    return result
