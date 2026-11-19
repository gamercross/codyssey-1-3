"""
문제 4. 라벨 정리                                  파일: p4_label.py

normalize(label) 함수를 만든다.

- 앞뒤 공백을 지우고 대소문자를 무시한다.
- "+" 또는 "cross" → "Cross"
- "x"             → "X"
- 그 밖의 글, 빈 글, 글이 아닌 값(None, 숫자 등) → None

예시
    normalize("+")       → "Cross"
    normalize(" X ")     → "X"
    normalize("CROSS")   → "Cross"
    normalize("o")       → None
    normalize(None)      → None

제약: import 없이.
"""

# 여기부터 직접 쓴다.
