// static/js/PopularProducts.js
async function loadPopularProducts() {
    const response = await fetch('/api/popular?max=12');
    const products = await response.json();
    
    const container = document.getElementById('popular-products');
    products.forEach(product => {
        container.innerHTML += `
            <div class="product-card">
                <img src="${product.image_url}" alt="${product.name}">
                <h3>${product.name}</h3>
                <p class="price">${product.price} ₽</p>
                <button class="cart-btn">В корзину</button>
            </div>
        `;
    });
}
