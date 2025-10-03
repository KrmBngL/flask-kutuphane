from flask import Flask, render_template, request, jsonify
import os
import fitz # PyMuPDF
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

# Normalde Tkinter de bu işi bir exe ile görürdü ama flask ile web gui yapma açısında daha rahat ve konforlü oldu.

app = Flask(__name__)

KUTUPHANE_DIR = 'Kütüphanem'
INDEX_DIR = 'indexdir'

def get_file_tree():
    tree = []
    # Her bir teknoloji için logo ekledim. 
    tech_logos = {
        "Oracle": "oracle.png",
        "PostgreSQL": "postgresql.png",
        "SQL Server": "sql_server.png"
    }
    
    # Her teknoloji için bir klasör açtım ve bunları buton tarzında sıraladım. tech_folders ın bir diğer amacı da, iç klasörleri de tutması için.
    tech_folders = sorted(os.listdir(KUTUPHANE_DIR))

    for tech in tech_folders:
        tech_path = os.path.join(KUTUPHANE_DIR, tech)
        if os.path.isdir(tech_path):
            files = [f for f in os.listdir(tech_path) if os.path.isfile(os.path.join(tech_path, f))]
            tree.append({
                "name": tech,
                "logo": tech_logos.get(tech, 'default.png'), # Burada bir ekstra durum belirttim. Mesela images klasöründe tech_logos ta olan bir png yoksa, default bir logo koy dedim. Ya boş ya da saçma sapan görünecek.
                "files": files
            })
    return tree

# İndex.html kısmının entegre edildiği yer. Burada txt ve pdf leri baz aldım. Herhangi birinin açılmama ya da karakter sorunu olduğunda belirtecek.

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


# Bu kısım arama kısmı. Dokümanlar içinde belirli bir kelime ile arayınca hem o dosyaları getiriyor hem de sağ tarafta o kelimeleri vurguluyor. Detayı css ve js de.

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
    app.run(debug=True, port=5003)   # Buradaki port spesifik olabilir. Normalde flask 5000 i alıyrdu. Benim localde patroni 5000 olduğu için ben de kafadan bir port salladım.