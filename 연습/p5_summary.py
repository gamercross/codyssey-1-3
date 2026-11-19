"""
문제 5. 케이스 요약                                파일: p5_summary.py

summarize(data) 함수를 만든다. data는 미션의 data.json을 읽은 모양의 dict다.

    data = {
        "filters": {
            "size_3": {"cross": [[0,1,0],[1,1,1],[0,1,0]],
                       "x":     [[1,0,1],[0,1,0],[1,0,1]]}
        },
        "patterns": {
            "size_3_0": {"input": [[0,1,0],[1,1,1],[0,1,0]], "expected": "+"},
            "size_3_1": {"input": [[1,0,1],[0,1,0],[1,0,1]], "expected": " X "},
            "size_3_2": {"input": [[0,0,0],[0,1,0],[0,0,0]], "expected": "cross"},
            "size_5_0": {"input": [[0]*5 for _ in range(5)], "expected": "x"}
        }
    }

규칙
- 필터 묶음 안의 키("cross", "Cross", "x" ...)와 expected는 문제 4처럼 정리한다.
- 패턴 키는 size_N_번호 꼴이다. N으로 필터 size_N을 찾는다.
- 판정은 문제 3과 같다 (eps = 1e-9).
- 판정이 정리한 expected와 같으면 PASS. 아래는 모두 FAIL이다.
    · 판정이 "UNDECIDED"
    · 필터 size_N이 없거나, 그 안에 Cross · X 중 하나가 없다
    · 키 꼴이 size_N_번호가 아니다
    · input 크기가 N×N이 아니다
    · expected를 정리할 수 없다
- 케이스 하나가 잘못돼도 함수가 멈추면 안 된다 (예외를 밖으로 내지 않는다).
- data에 "filters"나 "patterns"가 없으면 빈 것으로 본다.

돌려줄 값
    {"total": 전체 수, "pass": 통과 수, "fail": 실패 수, "fails": [실패한 키]}
    fails는 N 숫자 순, 같은 N이면 번호 숫자 순이다.
    (문자열 순이 아니다: size_3_2 → size_3_10 → size_10_1)
    키 꼴이 틀린 것은 맨 뒤에 문자열 순으로 붙인다.

예시 결과
    {"total": 4, "pass": 2, "fail": 2, "fails": ["size_3_2", "size_5_0"]}

제약: import 없이. 다른 파일을 import하지 않는다 (필요한 함수는 이 파일에 다시 쓴다).
"""

# 여기부터 직접 쓴다.
