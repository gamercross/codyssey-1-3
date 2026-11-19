"""문제 1 풀이. 먼저 직접 써 보고 나서 본다."""


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
