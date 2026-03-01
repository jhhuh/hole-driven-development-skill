def smart_merge(dict_a: dict, dict_b: dict) -> dict:
    """Merge two dicts 'smartly'.

    HOLE: Ambiguity detected — "smartly" is undefined.

    Possible strategies:
      1. Shallow merge (dict_b wins on conflicts)
      2. Deep/recursive merge (recursively merge nested dicts)
      3. Conflict-detecting merge (raise on conflicts)
      4. Type-aware merge (lists concatenated, dicts deep-merged, scalars: dict_b wins)

    Awaiting human clarification before filling this hole.
    """
    raise NotImplementedError(
        "smart_merge is ambiguous: 'smartly' is not defined. "
        "See docstring for candidate strategies. "
        "Human must choose a strategy before implementation proceeds."
    )
