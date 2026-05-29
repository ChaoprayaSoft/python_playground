import re
html = open('datavis_capstone.html', encoding='utf-8').read()
ids = ['close-canvas-btn', 'close-console-btn', 'close-csv-btn']
missing = [i for i in ids if f'id="{i}"' not in html]
print('Missing:', missing)
