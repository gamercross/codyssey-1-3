"""문제 5 풀이. 먼저 직접 써 보고 나서 본다."""

EPS = 1e-9


def mac(pattern, filt):
    n = len(pattern)
    if n == 0 or len(filt) != n:
        raise ValueError("크기가 다르거나 비어 있다")
    for i in range(n):
        if len(pattern[i]) != n or len(filt[i]) != n:
            raise ValueError("정사각형이 아니다")
    total = 0
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filt[i][j]
    return total


def normalize(label):
    if not isinstance(label, str):
        return None
    s = label.strip().lower()
    if s == "+" or s == "cross":
        return "Cross"
    if s == "x":
        return "X"
    return None


def parse_key(key):
    """'size_13_2' → (13, 2). 꼴이 틀리면 None."""
    parts = key.split("_")
    if len(parts) != 3 or parts[0] != "size":
        return None
    if not parts[1].isdigit() or not parts[2].isdigit():
        return None
    return int(parts[1]), int(parts[2])


def load_filters(raw):
    """{'size_3': {'cross': ..., 'x': ...}} → {3: {'Cross': ..., 'X': ...}}"""
    filters = {}
    for key, group in raw.items():
        parts = key.split("_")
        if len(parts) != 2 or parts[0] != "size" or not parts[1].isdigit():
            continue
        if not isinstance(group, dict):
            continue
        loaded = {}
        for name, rows in group.items():
            label = normalize(name)
            if label is not None:
                loaded[label] = rows
        filters[int(parts[1])] = loaded
    return filters


def check_case(key, case, filters):
    parsed = parse_key(key)
    if parsed is None:
        return False
    n = parsed[0]
    f = filters.get(n)
    if f is None or "Cross" not in f or "X" not in f:
        return False
    if not isinstance(case, dict):
        return False
    expected = normalize(case.get("expected"))
    if expected is None:
        return False
    rows = case.get("input")
    if not isinstance(rows, list) or len(rows) != n:
        return False
    a = mac(rows, f["Cross"])          # 크기가 틀리면 ValueError
    b = mac(rows, f["X"])
    if abs(a - b) < EPS:
        return False                   # UNDECIDED 는 FAIL
    verdict = "Cross" if a > b else "X"
    return verdict == expected


def sort_key(key):
    parsed = parse_key(key)
    if parsed is None:
        return (1, 0, 0, key)          # 꼴이 틀린 키는 맨 뒤, 문자열 순
    return (0, parsed[0], parsed[1], "")


def summarize(data):
    if not isinstance(data, dict):
        data = {}
    raw_filters = data.get("filters", {})
    patterns = data.get("patterns", {})
    if not isinstance(raw_filters, dict):
        raw_filters = {}
    if not isinstance(patterns, dict):
        patterns = {}
    filters = load_filters(raw_filters)

    passed = 0
    fails = []
    for key, case in patterns.items():
        try:
            ok = check_case(key, case, filters)
        except Exception:              # 케이스 하나가 전체를 멈추지 않게
            ok = False
        if ok:
            passed += 1
        else:
            fails.append(key)
    fails.sort(key=sort_key)
    return {"total": len(patterns), "pass": passed, "fail": len(fails), "fails": fails}
