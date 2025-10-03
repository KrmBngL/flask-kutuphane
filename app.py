from flask import Flask, render_template, request, jsonify
import os
import fitz # PyMuPDF
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

app = Flask(__name__)

KUTUPHANE_DIR = 'Kütüphanem'
INDEX_DIR = 'indexdir'

def get_file_tree():
    tree = []
    # Teknoloji isimleri ve logo dosyalarını eşleştirelim
    tech_logos = {
        "Oracle": "oracle.png",
        "PostgreSQL": "postgresql.png",
        "SQL Server": "sql_server.png"
    }
    
    # Klasör isimlerine göre sıralama yapabiliriz
    tech_folders = sorted(os.listdir(KUTUPHANE_DIR))

    for tech in tech_folders:
        tech_path = os.path.join(KUTUPHANE_DIR, tech)
        if os.path.isdir(tech_path):
            files = [f for f in os.listdir(tech_path) if os.path.isfile(os.path.join(tech_path, f))]
            tree.append({
                "name": tech,
                "logo": tech_logos.get(tech, 'default.png'), # Logo bulunamazsa default bir ikon kullanılabilir
                "files": files
            })
    return tree

@app.route('/')
def index():
    file_tree = get_file_tree()
    return render_template('index.html', file_tree=file_tree)

@app.route('/get_content')
def get_content():
    file_path = request.args.get('path', '').strip()
    if '..' in file_path or not file_path.startswith(KUTUPHANE_DIR):
        return jsonify({'error': 'Geçersiz dosya yolu'}), 400

    content = ""
    if os.path.exists(file_path):
        if file_path.endswith(".pdf"):
            try:
                doc = fitz.open(file_path)
                for page in doc:
                    content += page.get_text()
            except Exception as e:
                return jsonify({'error': f'PDF okuma hatası: {e}'}), 500
        else: # .txt, .sql, etc.
             with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        return jsonify({'content': content})
    return jsonify({'error': 'Dosya bulunamadı'}), 404

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    try:
        ix = open_dir(INDEX_DIR)
    except Exception as e:
        return jsonify({'error': f'Arama indeksi açılamadı: {e}'}), 500
        
    results_list = []
    with ix.searcher() as searcher:
        query_parser = QueryParser("content", ix.schema)
        parsed_query = query_parser.parse(query)
        results = searcher.search(parsed_query, limit=50)

        for hit in results:
            results_list.append({
                'path': hit['path'],
                'highlight': hit.highlights("content")
            })
            
    return jsonify(results_list)

if __name__ == '__main__':
    app.run(debug=True, port=5003)