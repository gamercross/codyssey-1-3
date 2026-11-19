"""
문제 3. 십자가와 X 판정                            파일: p3_judge.py

judge(pattern, cross, x, eps=1e-9) 함수를 만든다.

- a = pattern과 cross의 MAC 값, b = pattern과 x의 MAC 값.
- |a - b| < eps 이면 "UNDECIDED", a > b 이면 "Cross", 아니면 "X"를 돌려준다.
- 크기가 맞지 않으면 ValueError를 일으킨다 (문제 1과 같은 규칙).
- 다른 파일을 import하지 않는다. mac이 필요하면 이 파일 안에 다시 쓴다.

CROSS = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
X     = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]

예시
    judge(CROSS, CROSS, X)                         → "Cross"
    judge(X, CROSS, X)                             → "X"
    judge([[0, 0, 0], [0, 1, 0], [0, 0, 0]], CROSS, X)  → "UNDECIDED"
    judge([[0.3, 0.1, 0.0],
           [0.2, 0.0, 0.0],
           [0.0, 0.0, 0.0]], CROSS, X)             → "UNDECIDED"
        (a는 0.30000000000000004, b는 0.3. a == b로 비교하면 틀린다)

제약: import 없이.
"""

# 여기부터 직접 쓴다.
