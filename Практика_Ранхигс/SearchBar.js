// static/js/SearchBar.js
document.getElementById('search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = document.getElementById('search-input').value;
    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const products = await response.json();
    renderProducts(products); // Функция отрисовки результатов
});