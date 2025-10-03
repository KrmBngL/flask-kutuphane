document.addEventListener('DOMContentLoaded', function() {
    // Elementleri seçme
    const fileListDiv = document.getElementById('file-list');
    const searchBox = document.getElementById('search-box');
    const searchResultsDiv = document.getElementById('search-results');
    const resultsList = document.getElementById('results-list');
    const homeButton = document.getElementById('home-button');
    const welcomeMessage = document.querySelector('.welcome-message');
    const documentViewer = document.getElementById('document-viewer');
    const documentHeader = document.getElementById('document-header');
    const documentContent = document.getElementById('document-content');

    // --- OLAY DİNLEYİCİLERİ ---
    homeButton.addEventListener('click', showWelcomeMessage);
    searchBox.addEventListener('input', handleSearch);

    document.querySelectorAll('.accordion-toggle').forEach(item => {
        item.addEventListener('click', () => {
            item.classList.toggle('active');
            item.nextElementSibling.classList.toggle('hidden');
        });
    });

    document.querySelectorAll('.file-item').forEach(item => {
        item.addEventListener('click', () => {
            fetchContent(item.dataset.path, ''); 
        });
    });

    // --- FONKSİYONLAR ---
    function showWelcomeMessage() {
        welcomeMessage.style.display = 'flex';
        documentViewer.style.display = 'none';
    }

    async function fetchContent(path, searchTerm) {
        welcomeMessage.style.display = 'none';
        documentViewer.style.display = 'flex';
        documentContent.innerHTML = '<p style="color: #555; padding: 1.5rem;">Yükleniyor...</p>';
        documentHeader.textContent = '';
        
        try {
            // 1. DOKÜMAN BAŞLIĞINI GÖSTER
            const filename = path.split('/').pop();
            documentHeader.textContent = filename;

            // 2. İÇERİĞİ GETİR
            const response = await fetch(`/get_content?path=${encodeURIComponent(path)}`);
            if (!response.ok) throw new Error('Dosya yüklenemedi.');
            
            const data = await response.json();
            const content = data.content;
            const escapedContent = content.replace(/</g, "&lt;").replace(/>/g, "&gt;");
            
            // 3. SYNTAX HIGHLIGHTING İÇİN HAZIRLA
            let languageClass = path.endsWith('.sql') ? 'language-sql' : 'language-plaintext';
            const codeElement = document.createElement('code');
            codeElement.className = languageClass;
            codeElement.innerHTML = escapedContent; // Henüz mark etiketi yok

            const preElement = document.createElement('pre');
            preElement.className = languageClass;
            preElement.appendChild(codeElement);
            
            documentContent.innerHTML = '';
            documentContent.appendChild(preElement);

            // 4. PRISM'İ ÇALIŞTIR
            Prism.highlightAll();

            // 5. ARAMA KELİMESİNİ VURGULA (Prism'den SONRA)
            if (searchTerm) {
                const regex = new RegExp(searchTerm, 'gi');
                // Prism'in oluşturduğu HTML üzerinde arama ve değiştirme yap
                const highlightedHtml = documentContent.innerHTML.replace(regex, (match) => `<mark>${match}</mark>`);
                documentContent.innerHTML = highlightedHtml;
            }

        } catch (error) {
            documentContent.innerHTML = `<p style="color:red; padding: 1.5rem;">Hata: ${error.message}</p>`;
        }
    }

    async function handleSearch(e) {
        const query = e.target.value.trim();

        if (query.length < 2) {
            fileListDiv.style.display = 'block';
            searchResultsDiv.style.display = 'none';
            return;
        }

        const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();

        fileListDiv.style.display = 'none';
        searchResultsDiv.style.display = 'block';
        resultsList.innerHTML = ''; 

        if (results.length === 0) {
            resultsList.innerHTML = '<li style="cursor: default; background: none;">Sonuç bulunamadı.</li>';
        } else {
            results.forEach(result => {
                const li = document.createElement('li');
                li.dataset.path = result.path;
                li.textContent = result.path.replace('Kütüphanem/', '').replace('Kütüphanem\\', '');
                li.addEventListener('click', () => fetchContent(result.path, query));
                resultsList.appendChild(li);
            });
        }
    }
});