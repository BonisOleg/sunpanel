/* ===== КАТАЛОГ JAVASCRIPT ===== */

// Модуль каталогу
window.app.catalog = {
    currentView: 'grid',

    init() {
        this.bindEvents();
        this.initFilters();
        this.initViewToggle();
    },

    bindEvents() {
        // Додавання товарів до кошика
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('add-to-cart-btn')) {
                this.handleAddToCart(e.target);
            }
        });

        // Сортування
        const sortSelect = document.querySelector('.catalog-sort');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.handleSort(e.target.value);
            });
        }

        // Мобільний фільтр
        if (window.app.utils.isMobile()) {
            this.initMobileFilters();
        }
    },

    handleAddToCart(button) {
        const productData = {
            id: parseInt(button.dataset.productId),
            name: button.dataset.productName,
            price: button.dataset.productPrice,
            image: button.dataset.productImage
        };

        window.app.cart.addItem(productData);

        // Анімація кнопки
        const originalText = button.textContent;
        button.textContent = 'Додано!';
        button.disabled = true;

        setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
        }, 1500);
    },

    initFilters() {
        const filtersForm = document.getElementById('filters-form');
        if (filtersForm) {
            // Автоматичне застосування фільтрів
            const filterSelects = filtersForm.querySelectorAll('.filter-select');
            filterSelects.forEach(select => {
                select.addEventListener('change', () => {
                    setTimeout(() => {
                        filtersForm.submit();
                    }, 300);
                });
            });
        }
    },

    initViewToggle() {
        const toggleBtns = document.querySelectorAll('.view-toggle-btn');
        const productsGrid = document.getElementById('products-grid');

        if (toggleBtns && productsGrid) {
            toggleBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const view = btn.dataset.view;
                    this.switchView(view, toggleBtns, productsGrid);
                });
            });
        }
    },

    switchView(view, toggleBtns, productsGrid) {
        if (this.currentView === view) return;

        this.currentView = view;

        // Оновлення активної кнопки
        toggleBtns.forEach(btn => {
            if (btn.dataset.view === view) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Зміна класу сітки
        if (view === 'list') {
            productsGrid.classList.add('products-grid--list');
            productsGrid.querySelectorAll('.product-card').forEach(card => {
                card.classList.add('product-card--list');
            });
        } else {
            productsGrid.classList.remove('products-grid--list');
            productsGrid.querySelectorAll('.product-card').forEach(card => {
                card.classList.remove('product-card--list');
            });
        }

        // Збереження в localStorage
        try {
            localStorage.setItem('catalog-view', view);
        } catch (e) {
            console.warn('Не вдалося зберегти вигляд каталогу:', e);
        }
    },

    handleSort(sortValue) {
        if (!sortValue) return;

        const url = new URL(window.location);
        url.searchParams.set('sort', sortValue);
        window.location.href = url.toString();
    },

    initMobileFilters() {
        // Фільтри тепер завжди видимі на мобілці - не потрібно створювати кнопку
        // Залишаємо метод для сумісності, але не створюємо кнопку
        const sidebar = document.querySelector('.catalog-sidebar');
        
        if (sidebar) {
            // Переконуємося що фільтри видимі
            sidebar.classList.add('active');
        }
    },

    toggleMobileFilters(sidebar) {
        const isOpen = sidebar.classList.contains('active');

        if (isOpen) {
            this.closeMobileFilters(sidebar);
        } else {
            this.openMobileFilters(sidebar);
        }
    },

    openMobileFilters(sidebar) {
        sidebar.classList.add('active');
        document.body.style.overflow = 'hidden';
    },

    closeMobileFilters(sidebar) {
        sidebar.classList.remove('active');
        document.body.style.overflow = '';
    },

    // Завантаження з localStorage
    loadUserPreferences() {
        try {
            const savedView = localStorage.getItem('catalog-view');
            if (savedView && ['grid', 'list'].includes(savedView)) {
                const toggleBtns = document.querySelectorAll('.view-toggle-btn');
                const productsGrid = document.getElementById('products-grid');
                this.switchView(savedView, toggleBtns, productsGrid);
            }
        } catch (e) {
            console.warn('Не вдалося завантажити налаштування каталогу:', e);
        }
    },

    // Анімації з'явлення карток
    animateCards() {
        const cards = document.querySelectorAll('.product-card');

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, index * 100);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        cards.forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(card);
        });
    }
};

// Фільтри
window.app.filters = {
    init() {
        this.bindEvents();
    },

    bindEvents() {
        // Очищення фільтрів
        const clearBtns = document.querySelectorAll('.filter-btn--clear');
        clearBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.clearFilters();
            });
        });
    },

    clearFilters() {
        const url = new URL(window.location);
        url.search = '';
        window.location.href = url.toString();
    }
};

// Ініціалізація при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    window.app.catalog.init();
    window.app.filters.init();

    // Завантаження користувацьких налаштувань
    window.app.catalog.loadUserPreferences();

    // Анімації (тільки якщо немає налаштування зменшення анімацій)
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        window.app.catalog.animateCards();
    }
});

// Експорт для використання в інших модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        catalog: window.app.catalog,
        filters: window.app.filters
    };
} 