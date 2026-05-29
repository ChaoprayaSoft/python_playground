import re

with open('datavis_capstone_app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace multi-line double-quoted strings with backticks
content = re.sub(r'example:\s*\"(.*?)\",\s*task:', lambda m: f'example: `{m.group(1)}`,\n        task:', content, flags=re.DOTALL)
content = re.sub(r'initialCode:\s*\"(.*?)\",\s*datasetName:', lambda m: f'initialCode: `{m.group(1)}`,\n        datasetName:', content, flags=re.DOTALL)

with open('datavis_capstone_app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
