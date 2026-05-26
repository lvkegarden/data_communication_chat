from difflib import SequenceMatcher

def normalize_code(code: str) -> str:
    if not code:
        return ''
    return code.upper().replace('-', '').replace('_', '').replace(' ', '')

doubao1 = "RG-S5750-24GT4XS-P-L"
our1 = "RG-S5750V2-L"

doubao2 = "RG-S5760-24GT4XS-P"
our2 = "RG-S5760-L"

print(f"豆包1: {doubao1}")
print(f"我们1: {our1}")
print(f"相似度: {SequenceMatcher(None, normalize_code(doubao1), normalize_code(our1)).ratio():.4f}")

print(f"\n豆包2: {doubao2}")
print(f"我们2: {our2}")
print(f"相似度: {SequenceMatcher(None, normalize_code(doubao2), normalize_code(our2)).ratio():.4f}")

print("\n让我们试试前缀匹配:")

def prefix_match(code1, code2):
    # 取前8个字符匹配
    norm1 = normalize_code(code1)
    norm2 = normalize_code(code2)
    prefix1 = norm1[:8]
    prefix2 = norm2[:8]
    return prefix1 == prefix2

print(f"豆包1 vs 我们1 前缀匹配: {prefix_match(doubao1, our1)}")
print(f"豆包2 vs 我们2 前缀匹配: {prefix_match(doubao2, our2)}")
