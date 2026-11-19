"""
빈칸 연습 채점기.

IDLE  : 이 파일을 열고 F5 (Run Module). 문제 1~6을 모두 채점한다.
터미널: python3 check.py          모두 채점
        python3 check.py 1 3      문제 1, 3만
        python3 check.py --answers  풀이/ 폴더의 답으로 채점 (채점기 확인용)

문제마다 숨은 케이스를 돌려 (통과 수 / 전체 수) × 100 점을 낸다.
시험처럼 문제별 점수의 평균이 총점이다.
"""

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SHOW_DETAIL = True      # False 로 바꾸면 틀린 케이스 이름을 숨긴다 (진짜 시험처럼)

CROSS3 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
X3 = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]


# ---------------------------------------------------------------------------
# 도우미
# ---------------------------------------------------------------------------
class Raises:
    def __init__(self, exc):
        self.exc = exc


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def same(got, want):
    if is_num(got) and is_num(want):
        return abs(got - want) < 1e-9
    if isinstance(want, list):
        return isinstance(got, list) and len(got) == len(want) and all(
            same(g, w) for g, w in zip(got, want))
    if isinstance(want, dict):
        return isinstance(got, dict) and set(got) == set(want) and all(
            same(got[k], want[k]) for k in want)
    return type(got) is type(want) and got == want


def run_case(thunk, want):
    try:
        got = thunk()
    except Exception as e:
        if isinstance(want, Raises) and isinstance(e, want.exc):
            return True, ""
        return False, f"{type(e).__name__}: {e}"
    if isinstance(want, Raises):
        return False, f"{want.exc.__name__}가 나와야 하는데 값을 돌려줬다: {got!r}"
    if callable(want):
        ok = bool(want(got))
        return ok, "" if ok else f"돌려준 값 {got!r}"
    if same(got, want):
        return True, ""
    return False, f"기대 {want!r}, 돌려준 값 {got!r}"


def load(name, use_answers):
    folder = os.path.join(HERE, "풀이") if use_answers else HERE
    sys.path.insert(0, folder)
    try:
        sys.modules.pop(name, None)
        return importlib.import_module(name), None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    finally:
        sys.path.pop(0)


def banned_words(path, words):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return []
    # 문제 설명(맨 위 따옴표 세 개 안)은 빼고 본다
    if text.startswith('"""'):
        end = text.find('"""', 3)
        if end != -1:
            text = text[end + 3:]
    return [w for w in words if w in text]


# ---------------------------------------------------------------------------
# 문제별 케이스
# ---------------------------------------------------------------------------
def cases_p1(m):
    mac = m.mac
    return [
        ("예시 2×2", lambda: mac([[1, 2], [3, 4]], [[1, 0], [0, 1]]), 5),
        ("예시 float", lambda: mac([[0.5, 0.5], [0.5, 0.5]], [[1, 1], [1, 1]]), 2.0),
        ("예시 1×3", lambda: mac([[1, 2, 3]], [[1, 2, 3]]), Raises(ValueError)),
        ("1×1", lambda: mac([[7]], [[3]]), 21),
        ("십자가끼리", lambda: mac(CROSS3, CROSS3), 5),
        ("십자가와 X", lambda: mac(CROSS3, X3), 1),
        ("음수", lambda: mac([[-1, 2], [3, -4]], [[1, 1], [1, 1]]), 0),
        ("5×5 전부 1", lambda: mac([[1] * 5 for _ in range(5)], [[2] * 5 for _ in range(5)]), 50),
        ("0.1 + 0.2", lambda: mac([[0.1, 0.2], [0, 0]], [[1, 1], [1, 1]]), 0.3),
        ("빈 입력", lambda: mac([], []), Raises(ValueError)),
        ("크기 다름 2×2 / 3×3", lambda: mac([[1, 2], [3, 4]], X3), Raises(ValueError)),
        ("필터만 정사각형 아님", lambda: mac([[1, 2], [3, 4]], [[1, 2], [3]]), Raises(ValueError)),
        ("패턴 줄 길이 들쭉날쭉", lambda: mac([[1, 2], [3, 4, 5]], [[1, 2], [3, 4]]), Raises(ValueError)),
    ]


def cases_p2(m):
    cross, x = m.make_cross, m.make_x

    def independent(f):
        def run():
            g = f(3)
            g[0][0] = 9
            return g[1][0] != 9 and g[2][0] != 9
        return run

    def ones(g):
        return sum(sum(r) for r in g)

    return [
        ("예시 cross 3", lambda: cross(3), CROSS3),
        ("예시 x 3", lambda: x(3), X3),
        ("cross 1", lambda: cross(1), [[1]]),
        ("x 1", lambda: x(1), [[1]]),
        ("cross 5", lambda: cross(5), [[0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [1, 1, 1, 1, 1],
                                       [0, 0, 1, 0, 0], [0, 0, 1, 0, 0]]),
        ("x 5", lambda: x(5), [[1, 0, 0, 0, 1], [0, 1, 0, 1, 0], [0, 0, 1, 0, 0],
                               [0, 1, 0, 1, 0], [1, 0, 0, 0, 1]]),
        ("cross 25의 1 개수", lambda: ones(cross(25)), 49),
        ("x 13의 1 개수", lambda: ones(x(13)), 25),
        ("cross 줄이 서로 따로", independent(cross), True),
        ("x 줄이 서로 따로", independent(x), True),
        ("값이 int", lambda: all(type(v) is int for r in cross(5) for v in r), True),
        ("cross 짝수", lambda: cross(4), Raises(ValueError)),
        ("x 짝수", lambda: x(2), Raises(ValueError)),
        ("cross 0", lambda: cross(0), Raises(ValueError)),
        ("x 음수", lambda: x(-3), Raises(ValueError)),
    ]


def cases_p3(m):
    judge = m.judge
    float_tie = [[0.3, 0.1, 0.0], [0.2, 0.0, 0.0], [0.0, 0.0, 0.0]]
    return [
        ("예시 Cross", lambda: judge(CROSS3, CROSS3, X3), "Cross"),
        ("예시 X", lambda: judge(X3, CROSS3, X3), "X"),
        ("예시 가운데 한 칸", lambda: judge([[0, 0, 0], [0, 1, 0], [0, 0, 0]], CROSS3, X3), "UNDECIDED"),
        ("예시 float 동점", lambda: judge(float_tie, CROSS3, X3), "UNDECIDED"),
        ("전부 0", lambda: judge([[0] * 3 for _ in range(3)], CROSS3, X3), "UNDECIDED"),
        ("가로 줄만", lambda: judge([[0, 0, 0], [1, 1, 1], [0, 0, 0]], CROSS3, X3), "Cross"),
        ("모서리만", lambda: judge([[1, 0, 0], [0, 0, 0], [0, 0, 0]], CROSS3, X3), "X"),
        ("아주 작은 차이 1e-6", lambda: judge([[0, 1e-6, 0], [0, 0, 0], [0, 0, 0]], CROSS3, X3), "Cross"),
        ("eps 바꾸기", lambda: judge([[0, 1, 0], [0, 0, 0], [0, 0, 0]], CROSS3, X3, eps=2), "UNDECIDED"),
        ("eps 이름으로", lambda: judge(X3, CROSS3, X3, eps=0.5), "X"),
        ("크기 다름", lambda: judge([[1, 0], [0, 1]], CROSS3, X3), Raises(ValueError)),
    ]


def cases_p4(m):
    n = m.normalize
    return [
        ("+", lambda: n("+"), "Cross"),
        ("cross", lambda: n("cross"), "Cross"),
        ("CROSS", lambda: n("CROSS"), "Cross"),
        ("' Cross '", lambda: n(" Cross "), "Cross"),
        ("x", lambda: n("x"), "X"),
        ("' X '", lambda: n(" X "), "X"),
        ("탭과 줄바꿈", lambda: n("\tx\n"), "X"),
        ("' + '", lambda: n(" + "), "Cross"),
        ("o", lambda: n("o"), None),
        ("빈 글", lambda: n(""), None),
        ("공백만", lambda: n("   "), None),
        ("crossx", lambda: n("crossx"), None),
        ("None", lambda: n(None), None),
        ("숫자 1", lambda: n(1), None),
    ]


def cases_p5(m):
    s = m.summarize
    base_filters = {"size_3": {"cross": CROSS3, "x": X3}}
    example = {
        "filters": base_filters,
        "patterns": {
            "size_3_0": {"input": CROSS3, "expected": "+"},
            "size_3_1": {"input": X3, "expected": " X "},
            "size_3_2": {"input": [[0, 0, 0], [0, 1, 0], [0, 0, 0]], "expected": "cross"},
            "size_5_0": {"input": [[0] * 5 for _ in range(5)], "expected": "x"},
        },
    }
    order = {
        "filters": base_filters,
        "patterns": {
            "size_10_1": {"input": CROSS3, "expected": "+"},
            "size_3_10": {"input": CROSS3, "expected": "x"},
            "size_3_2": {"input": X3, "expected": "+"},
            "size_3_1": {"input": CROSS3, "expected": "+"},
        },
    }
    broken = {
        "filters": {"size_3": {"Cross": CROSS3, "X": X3}, "size_5": {"cross": [[0] * 5] * 5}},
        "patterns": {
            "size_3_1": {"input": CROSS3, "expected": "CROSS"},       # 필터 키 대문자도 PASS
            "big_3_1": {"input": CROSS3, "expected": "+"},            # 키 꼴 틀림
            "size_3_x": {"input": CROSS3, "expected": "+"},           # 번호가 숫자 아님
            "size_3_2": {"input": [[1, 0], [0, 1]], "expected": "x"},  # 크기 다름
            "size_3_3": {"input": X3, "expected": "o"},               # expected 정리 못 함
            "size_3_4": {"expected": "+"},                            # input 없음
            "size_5_1": {"input": [[0] * 5] * 5, "expected": "+"},    # X 필터 없음
            "size_3_5": "이건 dict가 아니다",
        },
    }
    with_real = None
    real_path = os.path.join(os.path.dirname(HERE), "data.json")
    if os.path.exists(real_path):
        with open(real_path, encoding="utf-8") as f:
            with_real = json.load(f)

    cases = [
        ("예시", lambda: s(example), {"total": 4, "pass": 2, "fail": 2, "fails": ["size_3_2", "size_5_0"]}),
        ("실패 키 숫자 순", lambda: s(order)["fails"], ["size_3_2", "size_3_10", "size_10_1"]),
        ("통과 수", lambda: s(order)["pass"], 1),
        ("잘못된 케이스가 섞여도 안 멈춤", lambda: s(broken),
         {"total": 8, "pass": 1, "fail": 7,
          "fails": ["size_3_2", "size_3_3", "size_3_4", "size_3_5", "size_5_1", "big_3_1", "size_3_x"]}),
        ("빈 dict", lambda: s({}), {"total": 0, "pass": 0, "fail": 0, "fails": []}),
        ("patterns만 있음", lambda: s({"patterns": {"size_3_1": {"input": CROSS3, "expected": "+"}}}),
         {"total": 1, "pass": 0, "fail": 1, "fails": ["size_3_1"]}),
    ]
    if with_real is not None:
        cases.append(("미션 data.json", lambda: s(with_real),
                      {"total": 9, "pass": 9, "fail": 0, "fails": []}))
    return cases


def cases_p6(m):
    G = m.Grid

    def copied():
        rows = [[1, 2], [3, 4]]
        g = G(rows)
        rows[0][0] = 99
        return g.get(0, 0)

    return [
        ("n", lambda: G([[1, 0], [0, 1]]).n, 2),
        ("get", lambda: G([[1, 2], [3, 4]]).get(1, 0), 3),
        ("get 음수", lambda: G([[1, 0], [0, 1]]).get(-1, 0), Raises(IndexError)),
        ("get 범위 밖", lambda: G([[1, 0], [0, 1]]).get(0, 2), Raises(IndexError)),
        ("str", lambda: str(G([[1, 0], [0, 1]])), "1 0\n0 1"),
        ("str float", lambda: str(G([[0.5]])), "0.5"),
        ("mac", lambda: G([[1, 0], [0, 1]]).mac(G([[2, 3], [4, 5]])), 7),
        ("mac 크기 다름", lambda: G([[1]]).mac(G(X3)), Raises(ValueError)),
        ("복사해 둠", copied, 1),
        ("정사각형 아님", lambda: G([[1, 2]]), Raises(ValueError)),
        ("빈 입력", lambda: G([]), Raises(ValueError)),
        ("숫자 아님", lambda: G([["a"]]), Raises(ValueError)),
    ]


PROBLEMS = [
    (1, "p1_mac", ["mac"], cases_p1, ["import", "sum(", "zip("]),
    (2, "p2_filters", ["make_cross", "make_x"], cases_p2, ["import"]),
    (3, "p3_judge", ["judge"], cases_p3, ["import"]),
    (4, "p4_label", ["normalize"], cases_p4, ["import"]),
    (5, "p5_summary", ["summarize"], cases_p5, ["import"]),
    (6, "p6_grid", ["Grid"], cases_p6, ["import"]),
]


# ---------------------------------------------------------------------------
# 실행
# ---------------------------------------------------------------------------
def grade(num, name, needs, make_cases, banned, use_answers):
    print(f"\n== 문제 {num} · {name}.py ==")
    folder = os.path.join(HERE, "풀이") if use_answers else HERE
    found = banned_words(os.path.join(folder, name + ".py"), banned)
    if found:
        print("  ! 쓰지 말기로 한 것이 있다: " + ", ".join(found) + "  (시험의 사용 제한 코드 연습)")

    mod, err = load(name, use_answers)
    if mod is None:
        print(f"  불러오기 실패 → 0점  ({err})")
        return 0
    missing = [n for n in needs if not hasattr(mod, n)]
    if missing:
        print("  아직 없음: " + ", ".join(missing) + " → 0점")
        return 0

    cases = make_cases(mod)
    passed = 0
    for desc, thunk, want in cases:
        ok, why = run_case(thunk, want)
        if ok:
            passed += 1
        elif SHOW_DETAIL:
            print(f"  FAIL  {desc}: {why}")
    score = round(passed * 100 / len(cases))
    print(f"  {passed}/{len(cases)} 통과 → {score}점")
    return score


def main(argv):
    use_answers = "--answers" in argv
    picks = {int(a) for a in argv if a.isdigit()}
    scores = []
    for num, name, needs, make_cases, banned in PROBLEMS:
        if picks and num not in picks:
            continue
        scores.append(grade(num, name, needs, make_cases, banned, use_answers))
    if scores:
        print(f"\n총점 (문제별 평균): {sum(scores) / len(scores):.1f}점")
    print("글로 답하기는 글답.md 를 풀고 풀이/글답_정답.md 와 맞춰 본다.")


if __name__ == "__main__":
    main(sys.argv[1:])
