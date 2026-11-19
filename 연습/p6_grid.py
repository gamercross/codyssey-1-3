"""
문제 6. 클래스로 만들기 (2주차 기초)               파일: p6_grid.py

class Grid 를 만든다.

- Grid(rows): rows는 2차원 리스트.
    · 비었거나 정사각형이 아니면 ValueError.
    · 값이 int · float가 아니면 ValueError.
    · rows를 그대로 들고 있지 말고 복사해 둔다.
      (만든 뒤 바깥에서 rows를 바꿔도 Grid는 바뀌지 않는다)
- g.n: 한 변의 크기 (속성).
- g.get(i, j): i줄 j칸 값. 0 ≤ i, j < n 이 아니면 IndexError (음수도 안 된다).
- g.mac(other): other도 Grid. 같은 자리끼리 곱해 더한 값. 크기가 다르면 ValueError.
- str(g): 줄마다 값을 빈칸 하나로 잇고, 줄은 "\n"으로 잇는다. 값은 str(값) 그대로.

예시
    g = Grid([[1, 0], [0, 1]])
    g.n             → 2
    g.get(1, 1)     → 1
    g.get(-1, 0)    → IndexError
    str(g)          → "1 0\n0 1"
    g.mac(Grid([[2, 3], [4, 5]]))  → 7
    Grid([[1, 2]])  → ValueError

제약: import 없이.
"""

# 여기부터 직접 쓴다.
