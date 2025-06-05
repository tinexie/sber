// static/js/ProductCard.js
function createProductCard(product) {
    return `
        <div class="product-card" data-id="${product.product_id}">
            <img src="${product.image_url}" alt="${product.name}">
            <h3>${product.name}</h3>
            <div class="price-block">
                <span class="current-price">${product.price} ₽</span>
                ${product.original_price ? `<span class="old-price">${product.original_price} ₽</span>` : ''}
            </div>
            <button class="cart-btn">В корзину</button>
        </div>
    `;
}
