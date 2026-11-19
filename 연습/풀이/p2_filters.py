"""문제 2 풀이. 먼저 직접 써 보고 나서 본다."""


def _check(n):
    if not isinstance(n, int) or n < 1 or n % 2 == 0:
        raise ValueError("n은 1 이상의 홀수여야 한다")


def _zeros(n):
    # [[0] * n] * n 으로 만들면 모든 줄이 같은 리스트가 된다 (함정)
    return [[0] * n for _ in range(n)]


def make_cross(n):
    _check(n)
    m = _zeros(n)
    mid = n // 2
    for i in range(n):
        m[mid][i] = 1
        m[i][mid] = 1
    return m


def make_x(n):
    _check(n)
    m = _zeros(n)
    for i in range(n):
        m[i][i] = 1
        m[i][n - 1 - i] = 1
    return m
