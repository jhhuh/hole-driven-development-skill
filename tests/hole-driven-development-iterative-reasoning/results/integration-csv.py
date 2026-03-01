def parse_csv(text: str) -> list[dict[str, str]]:
    rows = text.strip().split('\n')
    if not rows:
        return []
    def parse_row(line: str) -> list[str]:
        fields = []
        current = []
        in_quotes = False
        for ch in line:
            if ch == '"':
                in_quotes = not in_quotes
            elif ch == ',' and not in_quotes:
                fields.append(''.join(current))
                current = []
            else:
                current.append(ch)
        fields.append(''.join(current))
        return fields

    headers = parse_row(rows[0])
    return [dict(zip(headers, parse_row(row))) for row in rows[1:]]
