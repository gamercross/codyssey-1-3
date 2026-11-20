# 심화 연습: MAC 기반 2D 컨볼루션 (짐작으로 만든 연습)

"MAC 기반 연산 처리 · 2D 컨볼루션, 함수 열 개 남짓을 채우는 2문제 + data.json 만들기"가 나온다는 이야기를 듣고 그 꼴로 만든 연습입니다. **실제 시험 문제가 아닙니다.**

꼴은 Downloads에서 받은 `practice.py`(Matrix 클래스 · PatternManager 연습)와 맞췄습니다. 함수 머리와 설명만 있고 몸통은 `pass`입니다. **잘못된 입력이면 예외 대신 `None`(또는 `False`)을 돌려줍니다.**

## 하는 법 (IDLE)

1. `practice.py`를 열어 `pass` 자리를 채운다. 위에서부터 차례로 쓰면 뒤 함수에서 앞 함수를 쓸 수 있다.
2. 같은 폴더에 `data.json`을 **손으로** 만든다(문제 3).
3. `check.py`를 열고 **F5**. 문제마다 숨은 케이스로 채점한다(모두 101개).
4. 다 쓴 뒤에만 `풀이/solution.py` · `풀이/data.json`을 연다.

터미널: `python3 check.py` · `python3 check.py 1`(문제 1만) · `python3 check.py --solution`(풀이 채점).
진짜 시험처럼 하려면 `check.py`의 `SHOW_DETAIL = True`를 `False`로 바꾼다.

## 문제

| 문제 | 만들 것 | 숨은 케이스가 보는 곳 |
|---|---|---|
| 1 · 함수 10개 | `shape` · `zeros` · `mac` · `window` · `pad` · `out_size` · `conv2d` · `flip` · `relu` · `max_pool` | 줄 길이 들쭉날쭉, `[[0]*n]*n` 함정, 패딩 · stride, 커널을 **뒤집지 않음**, 직사각형, 원본을 바꾸지 않음 (53개) |
| 2 · 함수 1개 + 클래스 메서드 9개 | `normalize_label`, `ConvClassifier`의 `add_filter` · `add_pattern` · `load_data` · `scores` · `classify` · `classify_all` · `summary` · `get_failed` · `count_by_verdict` | 이름 정리, 겹친 이름, 필터보다 작은 패턴, 잘못된 항목 건너뛰기, 동점 → UNDECIDED, 0개인 키 (37개) |
| 3 · data.json | 필터 2개 이상(cross · x 포함, 3×3), 패턴 6개 이상(5×5) | JSON 문법, 꼴, id 겹침, `"+"` 표기, 모두 PASS (11개) |

**점수 = conv2d 결과의 가장 큰 값.** 모양이 그림 어디에 있든 찾습니다. 5×5 가운데 십자가는 cross 5 · x 3이고, 가운데 한 칸만 켜진 그림은 1 · 1로 동점(UNDECIDED)입니다.

## 시험장에서 기억할 것

- `[[0] * n] * n`은 줄이 모두 같은 리스트다 → `[[0] * n for _ in range(n)]`
- 출력 크기 `(n + 2p − k) // s + 1`, 창의 왼쪽 위는 `(i * s, j * s)`
- 딥러닝의 conv는 커널을 뒤집지 않는다(교차상관). 뒤집으면 `flip`
- 동점은 `abs(a − b) < eps`, `==`가 아니다
- JSON: 큰따옴표, 마지막 쉼표 없음, `true` · `false` · `null`
