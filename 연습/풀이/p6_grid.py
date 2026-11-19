"""문제 6 풀이. 먼저 직접 써 보고 나서 본다."""


class Grid:
    def __init__(self, rows):
        if not isinstance(rows, list) or len(rows) == 0:
            raise ValueError("비어 있다")
        n = len(rows)
        copied = []
        for row in rows:
            if not isinstance(row, list) or len(row) != n:
                raise ValueError("정사각형이 아니다")
            new_row = []
            for v in row:
                if not isinstance(v, (int, float)):
                    raise ValueError("숫자가 아니다: " + repr(v))
                new_row.append(v)
            copied.append(new_row)
        self.n = n
        self.rows = copied

    def get(self, i, j):
        if not (0 <= i < self.n and 0 <= j < self.n):
            raise IndexError("범위 밖")
        return self.rows[i][j]

    def mac(self, other):
        if self.n != other.n:
            raise ValueError("크기가 다르다")
        total = 0
        for i in range(self.n):
            for j in range(self.n):
                total += self.rows[i][j] * other.rows[i][j]
        return total

    def __str__(self):
        lines = []
        for row in self.rows:
            lines.append(" ".join(str(v) for v in row))
        return "\n".join(lines)
