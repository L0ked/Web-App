import re

with open('example.txt', 'r', encoding='utf-8') as f:
    text = f.read()

words = re.findall(r'[а-яА-ЯёЁa-zA-Z]+', text)
max_len = max(len(w) for w in words)
result = []
for w in words:
    if len(w) == max_len and w not in result:
        result.append(w)

for w in result:
    print(w)
