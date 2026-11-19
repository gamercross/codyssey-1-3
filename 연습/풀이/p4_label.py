"""문제 4 풀이. 먼저 직접 써 보고 나서 본다."""


def normalize(label):
    if not isinstance(label, str):
        return None
    s = label.strip().lower()
    if s == "+" or s == "cross":
        return "Cross"
    if s == "x":
        return "X"
    return None
