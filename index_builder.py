import os
import fitz  # PyMuPDF
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID

KUTUPHANE_DIR = 'Kütüphanem'
INDEX_DIR = 'indexdir'

def get_document_content(path):
    if path.endswith(".pdf"):
        try:
            doc = fitz.open(path)
            content = ""
            for page in doc:
                content += page.get_text()
            return content
        except Exception as e:
            print(f"PDF okuma hatası: {path} - {e}")
            return ""
    elif path.endswith((".txt", ".sql")):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Metin okuma hatası: {path} - {e}")
            return ""
    return ""

def create_index():
    schema = Schema(path=ID(stored=True, unique=True), content=TEXT(stored=True))

    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)

    ix = create_in(INDEX_DIR, schema)
    writer = ix.writer()

    print("İndeksleme başlıyor...")
    for root, dirs, files in os.walk(KUTUPHANE_DIR):
        for filename in files:
            path = os.path.join(root, filename)
            # Whoosh'un Windows yollarını işlemesi için yolları düzeltelim
            path = path.replace("\\", "/")
            print(f"{path} dosyası işleniyor...")
            content = get_document_content(path)
            if content:
                writer.add_document(path=path, content=content)

    print("İndeksleme tamamlandı. Değişiklikler kaydediliyor...")
    writer.commit()

if __name__ == '__main__':
    create_index()