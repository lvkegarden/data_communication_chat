from difflib import SequenceMatcher

def normalize_code(code):
    if not code:
        return ''
    return code.upper().replace('-', '').replace('_', '').replace(' ', '')

def code_similarity(code1, code2):
    norm1 = normalize_code(code1)
    norm2 = normalize_code(code2)
    
    if norm1 == norm2:
        return 1.0
    
    return SequenceMatcher(None, norm1, norm2).ratio()

test_cases = [
    ('S5130S-28P-EI', 'S5130S-EI'),
    ('S5130S-28P-EI', 'S5130S-LI'),
    ('S5130S-28P-EI', 'S5130S-SI'),
    ('S5735-L-V2', 'S5735-L-V2'),
    ('RG-S5750-24GT4XS-P-L', 'RG-S5750V2-L'),
    ('RG-S5750-24GT4XS-P-L', 'RG-S5310-E'),
]

print("代码相似度测试:")
print("=" * 80)
for c1, c2 in test_cases:
    sim = code_similarity(c1, c2)
    print(f"\n{c1} vs {c2}")
    print(f"  归一化: {normalize_code(c1)} vs {normalize_code(c2)}")
    print(f"  相似度: {sim:.4f}")
    print(f"  阈值 0.8: {'通过' if sim >= 0.8 else '未通过'}")
    print(f"  阈值 0.6: {'通过' if sim >= 0.6 else '未通过'}")
