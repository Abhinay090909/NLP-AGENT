import json
import os

total = 6208
merged = [{"output": ""} for _ in range(total)]

files = [
    ('answers_0_1000.json', 0),
    ('answers_1000_2000.json', 1000),
    ('answers_2000_3000.json', 2000),
    ('answers_3000_4000.json', 3000),
    ('answers_4000_4120.json', 4000),
    ('answers_4120_5100.json', 4120),
    ('answers_5100_6208.json', 5100),
]

for filename, start in files:
    if os.path.exists(filename):
        data = json.load(open(filename))
        for i, item in enumerate(data):
            merged[start + i] = item
        print(f'{filename}: {len(data)} answers placed at index {start}')
    else:
        print(f'{filename}: not found, leaving empty')

filled = sum(1 for d in merged if d['output'])
print(f'\nCovered: {filled}/{total}')
print(f'Empty: {total - filled}')

json.dump(merged, open('cse_476_final_project_answers.json', 'w'), indent=2)
print('Merge done')