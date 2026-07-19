from pypdf import PdfReader
from pathlib import Path
path = Path(r'c:\Users\prafu\OneDrive\Desktop\Faym\SDE Intern Assignment.pdf')
reader = PdfReader(str(path))
print('pages', len(reader.pages))
for i, page in enumerate(reader.pages, 1):
    text = page.extract_text() or ''
    print(f'--- PAGE {i} ---')
    print(text)
    print()
