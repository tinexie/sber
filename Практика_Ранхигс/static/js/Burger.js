// static/js/burger.js

document.addEventListener('DOMContentLoaded', function() {
    // Создаем элемент для затемнения фона
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    document.body.appendChild(overlay);
    
    // Получаем элементы управления
    const burgerBtn = document.querySelector('.burger-btn');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    // Функция для переключения меню
    function toggleMenu() {
        burgerBtn.classList.toggle('active');
        mobileMenu.classList.toggle('active');
        overlay.classList.toggle('active');
        document.body.classList.toggle('no-scroll');
    }
    
    // Обработчик для бургер-кнопки
    burgerBtn.addEventListener('click', function(e) {
        e.stopPropagation(); // Предотвращаем всплытие
        toggleMenu();
    });
    
    // Обработчик для оверлея
    overlay.addEventListener('click', toggleMenu);
    
    // Закрытие меню при клике на пункты
    const menuItems = document.querySelectorAll('.mobile-nav a');
    menuItems.forEach(item => {
        item.addEventListener('click', toggleMenu);
    });
    
    // Запрет скролла при открытом меню
    document.addEventListener('scroll', function() {
        if (mobileMenu.classList.contains('active')) {
            window.scrollTo(0, 0);
        }
    });
});