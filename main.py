"""Mini NPU Simulator.

MAC(Multiply-Accumulate) 연산으로 입력 패턴이 어느 필터(Cross / X)와 더 닮았는지 판정한다.
외부 라이브러리 없이 표준 라이브러리(json, time, re, os, sys)만 사용한다.

모드
  1. 사용자 입력 (3x3)  : 필터 A, B와 패턴을 콘솔로 입력받아 판정
  2. data.json 분석     : 5x5 / 13x13 / 25x25 필터와 패턴을 일괄 판정, PASS/FAIL 집계
  3. 보너스             : N×N 패턴 생성기 + 2차원/1차원 MAC 성능 비교
"""

import json
import os
import re
import sys
import time

# ---------------------------------------------------------------------------
# 정책 상수
# ---------------------------------------------------------------------------
EPSILON = 1e-9          # 점수 비교 허용오차: |a - b| < EPSILON 이면 동점
EPSILON_TEXT = "1e-9"
REPEAT = 10             # 성능 측정 반복 횟수 (최소 기준 10회)
PERF_SIZES = (3, 5, 13, 25)

LABEL_CROSS = "Cross"
LABEL_X = "X"
UNDECIDED = "UNDECIDED"

# 표준 라벨 정규화 표: 소문자/앞뒤 공백 제거 후 찾는다.
#   expected 값 : '+' -> Cross, 'x' -> X
#   filter 키   : 'cross' -> Cross, 'x' -> X
LABEL_ALIASES = {
    "+": LABEL_CROSS,
    "cross": LABEL_CROSS,
    "x": LABEL_X,
}

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

SIZE_KEY_RE = re.compile(r"^size_(\d+)$")
PATTERN_KEY_RE = re.compile(r"^size_(\d+)_(\d+)$")

LINE = "#" + "-" * 39


# ---------------------------------------------------------------------------
# 데이터 구조
# ---------------------------------------------------------------------------
class Matrix:
    """n×n 정사각 2차원 배열. 위치별 값을 저장하고 읽을 수 있다."""

    def __init__(self, n, fill=0.0):
        if n <= 0:
            raise ValueError("크기는 1 이상이어야 합니다.")
        self.n = n
        self.rows = [[float(fill)] * n for _ in range(n)]

    @classmethod
    def from_rows(cls, rows, expected_n=None):
        """2차원 리스트를 검증해 Matrix로 만든다. 문제가 있으면 ValueError."""
        if not isinstance(rows, list) or not rows:
            raise ValueError("2차원 배열(리스트의 리스트)이 아닙니다.")
        n = len(rows)
        for r, row in enumerate(rows):
            if not isinstance(row, list):
                raise ValueError(f"{r + 1}행이 배열이 아닙니다.")
            if len(row) != n:
                raise ValueError(f"정사각 배열이 아닙니다: {n}행인데 {r + 1}행의 열 수가 {len(row)}개")
            for c, v in enumerate(row):
                # bool은 int의 하위 타입이라 따로 막는다.
                if isinstance(v, bool) or not isinstance(v, (int, float)):
                    raise ValueError(f"({r + 1},{c + 1}) 값이 숫자가 아닙니다: {v!r}")
        if expected_n is not None and n != expected_n:
            raise ValueError(f"크기 불일치: {expected_n}×{expected_n} 이 필요한데 {n}×{n} 입니다.")
        m = cls(n)
        for r in range(n):
            for c in range(n):
                m.set(r, c, rows[r][c])
        return m

    def get(self, r, c):
        return self.rows[r][c]

    def set(self, r, c, value):
        self.rows[r][c] = float(value)

    def flatten(self):
        """보너스: 길이 N² 의 1차원 배열로 변환 (행 우선)."""
        flat = []
        for row in self.rows:
            flat.extend(row)
        return flat

    def format(self, indent="  "):
        lines = []
        for row in self.rows:
            lines.append(indent + " ".join(_fmt_cell(v) for v in row))
        return "\n".join(lines)


def _fmt_cell(v):
    return str(int(v)) if float(v).is_integer() else str(v)


# ---------------------------------------------------------------------------
# MAC 연산 / 판정
# ---------------------------------------------------------------------------
def mac(pattern, flt):
    """위치별로 곱해서 모두 더한다. 반복문으로 직접 계산 (N² 번의 곱셈 + 덧셈)."""
    n = pattern.n
    if flt.n != n:
        raise ValueError(f"크기 불일치: 패턴 {n}×{n}, 필터 {flt.n}×{flt.n}")
    total = 0.0
    p_rows = pattern.rows
    f_rows = flt.rows
    for i in range(n):
        p_row = p_rows[i]
        f_row = f_rows[i]
        for j in range(n):
            total += p_row[j] * f_row[j]
    return total


def mac_flat(pattern_flat, filter_flat):
    """보너스: 1차원(길이 N²) 배열 버전 MAC. 이중 인덱싱 없이 한 번의 반복."""
    if len(pattern_flat) != len(filter_flat):
        raise ValueError("크기 불일치")
    total = 0.0
    for k in range(len(pattern_flat)):
        total += pattern_flat[k] * filter_flat[k]
    return total


def is_tie(a, b, eps=EPSILON):
    return abs(a - b) < eps


def decide(score_a, score_b, label_a, label_b):
    """epsilon 기반 비교. 동점이면 UNDECIDED."""
    if is_tie(score_a, score_b):
        return UNDECIDED
    return label_a if score_a > score_b else label_b


def normalize_label(raw):
    """여러 표기('+', 'x', 'cross', 'X' ...)를 표준 라벨(Cross / X)로 바꾼다. 모르면 None."""
    if not isinstance(raw, str):
        return None
    return LABEL_ALIASES.get(raw.strip().lower())


def measure_ms(func, *args, repeat=REPEAT):
    """연산 함수 호출 구간만 repeat 번 측정해 평균(ms)을 돌려준다. I/O 는 포함하지 않는다."""
    func(*args)  # 워밍업 1회 (측정 제외)
    elapsed = 0.0
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        elapsed += time.perf_counter() - start
    return elapsed / repeat * 1000.0


# ---------------------------------------------------------------------------
# 패턴 생성기 (보너스) — 성능 분석에도 재사용
# ---------------------------------------------------------------------------
def make_cross(n):
    m = Matrix(n)
    mid = n // 2
    for i in range(n):
        m.set(mid, i, 1)
        m.set(i, mid, 1)
    return m


def make_x(n):
    m = Matrix(n)
    for i in range(n):
        m.set(i, i, 1)
        m.set(i, n - 1 - i, 1)
    return m


# ---------------------------------------------------------------------------
# 콘솔 입출력 도우미
# ---------------------------------------------------------------------------
def section(title):
    print()
    print(LINE)
    print(f"# {title}")
    print(LINE)


def read_line(prompt=""):
    try:
        return input(prompt)
    except EOFError:
        print("\n입력이 끝나 프로그램을 종료합니다.")
        sys.exit(0)


def read_matrix(title, n=3):
    """n줄을 공백 구분으로 입력받는다. 형식이 틀리면 안내 후 그 행렬을 처음부터 다시 받는다."""
    while True:
        print(f"{title} ({n}줄 입력, 공백 구분)")
        rows = []
        error = None
        for r in range(n):
            tokens = read_line().split()
            if len(tokens) != n:
                error = (f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요. "
                         f"({r + 1}번째 줄에 {len(tokens)}개 입력됨)")
                break
            try:
                rows.append([float(t) for t in tokens])
            except ValueError:
                error = f"입력 형식 오류: {r + 1}번째 줄에 숫자가 아닌 값이 있습니다. 숫자만 입력하세요."
                break
        if error is None:
            return Matrix.from_rows(rows, expected_n=n)
        print(error)
        print("→ 처음 줄부터 다시 입력하세요.\n")


def print_perf_table(sizes, repeat=REPEAT):
    """크기별로 Cross 패턴 × Cross 필터 MAC 시간을 재서 표로 출력한다."""
    print(f"{'크기':<10}{'평균 시간(ms)':>14}{'연산 횟수(N²)':>16}")
    print("-" * 42)
    rows = []
    for n in sizes:
        pattern = make_cross(n)
        flt = make_cross(n)
        avg = measure_ms(mac, pattern, flt, repeat=repeat)
        rows.append((n, avg))
        print(f"{f'{n}×{n}':<10}{avg:>14.4f}{n * n:>16}")
    return rows


# ---------------------------------------------------------------------------
# 모드 1: 사용자 입력 (3x3)
# ---------------------------------------------------------------------------
def run_user_mode():
    n = 3
    section("[1] 필터 입력")
    filter_a = read_matrix("필터 A", n)
    print()
    filter_b = read_matrix("필터 B", n)

    print("\n✓ 필터 저장 완료")
    print("필터 A:")
    print(filter_a.format())
    print("필터 B:")
    print(filter_b.format())

    section("[2] 패턴 입력")
    pattern = read_matrix("패턴", n)

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    avg_ms = (measure_ms(mac, pattern, filter_a) + measure_ms(mac, pattern, filter_b)) / 2
    verdict = decide(score_a, score_b, "A", "B")

    section("[3] MAC 결과")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/{REPEAT}회): {avg_ms:.4f} ms")
    if verdict == UNDECIDED:
        print(f"판정: 판정 불가 (|A-B| < {EPSILON_TEXT})")
    else:
        print(f"판정: {verdict}")

    section(f"[4] 성능 분석 (평균/{REPEAT}회)")
    print_perf_table((n,))


# ---------------------------------------------------------------------------
# 모드 2: data.json 분석
# ---------------------------------------------------------------------------
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"파일을 찾을 수 없습니다: {path}"
    except json.JSONDecodeError as e:
        return None, f"JSON 형식 오류: {e}"
    except OSError as e:
        return None, f"파일을 읽을 수 없습니다: {e}"


def load_filters(data):
    """filters 섹션을 읽어 {N: {"Cross": Matrix, "X": Matrix}} 로 만든다. 문제는 경고만 남긴다."""
    filters = {}
    raw = data.get("filters") if isinstance(data, dict) else None
    if not isinstance(raw, dict):
        print("✗ 'filters' 항목이 없거나 객체가 아닙니다.")
        return filters

    def sort_key(k):
        m = SIZE_KEY_RE.match(k)
        return (0, int(m.group(1))) if m else (1, k)

    for key in sorted(raw, key=sort_key):
        m = SIZE_KEY_RE.match(key)
        if not m:
            print(f"✗ {key}: 필터 키 형식 오류 (size_N 형태가 아님) — 건너뜀")
            continue
        n = int(m.group(1))
        group = raw[key]
        if not isinstance(group, dict):
            print(f"✗ {key}: 필터 묶음이 객체가 아님 — 건너뜀")
            continue
        loaded = {}
        broken = set()
        problems = []
        for label_key, rows in group.items():
            label = normalize_label(label_key)
            if label is None:
                problems.append(f"알 수 없는 필터 키 '{label_key}'")
                continue
            try:
                loaded[label] = Matrix.from_rows(rows, expected_n=n)
            except ValueError as e:
                broken.add(label)
                problems.append(f"{label_key}: {e}")
        for label in (LABEL_CROSS, LABEL_X):
            if label not in loaded and label not in broken:
                problems.append(f"{label} 필터 없음")
        if loaded:
            filters[n] = loaded
        mark = "✓" if not problems else "△"
        names = ", ".join(lbl for lbl in (LABEL_CROSS, LABEL_X) if lbl in loaded) or "없음"
        print(f"{mark} {key:<8} 필터 로드 {'완료' if not problems else '일부 실패'} ({names})")
        for p in problems:
            print(f"    - {p}")
    return filters


def evaluate_case(key, item, filters):
    """패턴 한 건을 판정한다. 어떤 문제든 예외 대신 FAIL 결과로 돌려준다."""
    result = {"key": key, "cross": None, "x": None, "verdict": None,
              "expected": None, "passed": False, "reason": None}

    m = PATTERN_KEY_RE.match(key)
    if not m:
        result["reason"] = "키 형식 오류 (size_N_idx 형태가 아님)"
        return result
    n = int(m.group(1))

    if not isinstance(item, dict):
        result["reason"] = "패턴 항목이 객체가 아님"
        return result

    raw_expected = item.get("expected")
    expected = normalize_label(raw_expected)
    result["expected"] = expected if expected else repr(raw_expected)

    flt = filters.get(n)
    if flt is None:
        result["reason"] = f"size_{n} 필터 없음"
        return result
    if LABEL_CROSS not in flt or LABEL_X not in flt:
        result["reason"] = f"size_{n} 필터 묶음에 Cross/X 중 일부가 없음"
        return result

    if "input" not in item:
        result["reason"] = "input 항목 없음 (스키마 오류)"
        return result
    try:
        pattern = Matrix.from_rows(item["input"])
    except ValueError as e:
        result["reason"] = f"input 형식 오류: {e}"
        return result
    if pattern.n != n:
        result["reason"] = f"크기 불일치: 필터 {n}×{n}, 패턴 {pattern.n}×{pattern.n}"
        return result

    result["cross"] = mac(pattern, flt[LABEL_CROSS])
    result["x"] = mac(pattern, flt[LABEL_X])
    result["verdict"] = decide(result["cross"], result["x"], LABEL_CROSS, LABEL_X)

    if expected is None:
        result["reason"] = f"expected 라벨 정규화 실패: {raw_expected!r}"
    elif result["verdict"] == UNDECIDED:
        result["reason"] = f"동점(|Cross-X| < {EPSILON_TEXT}) → UNDECIDED 처리 규칙에 따라 FAIL"
    elif result["verdict"] != expected:
        result["reason"] = f"판정 {result['verdict']} ≠ expected {expected}"
    else:
        result["passed"] = True
    return result


def pattern_sort_key(key):
    m = PATTERN_KEY_RE.match(key)
    return (0, int(m.group(1)), int(m.group(2))) if m else (1, 0, 0, key)


def run_json_mode(path=DEFAULT_DATA_PATH):
    section("[1] 필터 로드")
    data, err = load_json(path)
    if err:
        print(f"✗ {err}")
        print("data.json 을 main.py 와 같은 폴더에 두거나, python main.py <경로> 로 실행하세요.")
        return
    filters = load_filters(data)

    section("[2] 패턴 분석 (라벨 정규화 적용)")
    patterns = data.get("patterns") if isinstance(data, dict) else None
    results = []
    if not isinstance(patterns, dict):
        print("✗ 'patterns' 항목이 없거나 객체가 아닙니다.")
        patterns = {}

    for key in sorted(patterns, key=pattern_sort_key):
        r = evaluate_case(key, patterns[key], filters)
        results.append(r)
        print(f"--- {key} ---")
        if r["cross"] is not None:
            print(f"Cross 점수: {r['cross']}")
            print(f"X 점수: {r['x']}")
            status = "PASS" if r["passed"] else f"FAIL ({r['reason']})"
            print(f"판정: {r['verdict']} | expected: {r['expected']} | {status}")
        else:
            print(f"FAIL ({r['reason']})")

    section(f"[3] 성능 분석 (평균/{REPEAT}회)")
    print_perf_table(PERF_SIZES)

    section("[4] 결과 요약")
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed
    print(f"총 테스트: {len(results)}개")
    print(f"통과: {passed}개")
    print(f"실패: {failed}개")
    if failed:
        print("\n실패 케이스:")
        for r in results:
            if not r["passed"]:
                print(f"- {r['key']}: {r['reason']}")
    print('\n(상세 원인 분석 및 복잡도 설명은 README.md 의 "결과 리포트" 섹션 참고)')
    return results


# ---------------------------------------------------------------------------
# 모드 3 (보너스): 패턴 생성기 + 1차원 최적화 비교
# ---------------------------------------------------------------------------
def read_size():
    while True:
        raw = read_line("생성할 크기 N (1~200): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 200:
            return int(raw)
        print("입력 형식 오류: 1~200 사이의 정수를 입력하세요.")


def run_bonus_mode():
    section("[1] 패턴 생성기")
    n = read_size()
    cross, x = make_cross(n), make_x(n)
    if n <= 25:
        print(f"\nCross {n}×{n}:")
        print(cross.format())
        print(f"\nX {n}×{n}:")
        print(x.format())
    else:
        print("(25 초과 크기는 출력을 생략합니다)")

    section("[2] 생성 패턴 판정 (Cross 필터 / X 필터)")
    for name, pattern in (("Cross 패턴", cross), ("X 패턴", x)):
        sc, sx = mac(pattern, cross), mac(pattern, x)
        print(f"{name}: Cross 점수 {sc}, X 점수 {sx} → {decide(sc, sx, LABEL_CROSS, LABEL_X)}")

    section(f"[3] 2차원 vs 1차원 MAC (평균/{REPEAT}회, 동일 입력)")
    sizes = sorted(set(PERF_SIZES) | {n})
    print(f"{'크기':<10}{'2D(ms)':>12}{'1D(ms)':>12}{'1D/2D':>10}{'N²':>8}")
    print("-" * 52)
    for size in sizes:
        p, f = make_cross(size), make_cross(size)
        pf, ff = p.flatten(), f.flatten()
        t2 = measure_ms(mac, p, f)
        t1 = measure_ms(mac_flat, pf, ff)
        ratio = t1 / t2 if t2 > 0 else float("nan")
        print(f"{f'{size}×{size}':<10}{t2:>12.4f}{t1:>12.4f}{ratio:>10.2f}{size * size:>8}")
    print("\n※ 1D/2D < 1 이면 1차원 버전이 더 빠름. 반복 10회라 작은 크기는 오차가 큽니다.")


# ---------------------------------------------------------------------------
# 진입점
# ---------------------------------------------------------------------------
def choose_mode():
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    print("3. 보너스: 패턴 생성기 + 1차원 최적화 비교")
    while True:
        choice = read_line("선택: ").strip()
        if choice in ("1", "2", "3"):
            return choice
        print("1, 2, 3 중 하나를 입력하세요.")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    data_path = argv[0] if argv else DEFAULT_DATA_PATH
    print("=== Mini NPU Simulator ===\n")
    choice = choose_mode()
    if choice == "1":
        run_user_mode()
    elif choice == "2":
        run_json_mode(data_path)
    else:
        run_bonus_mode()


if __name__ == "__main__":
    main()
