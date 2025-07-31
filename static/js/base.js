/* ===== БАЗОВИЙ JAVASCRIPT ===== */

// Глобальні змінні
window.app = {
    cart: null,
    nav: null,
    utils: {}
};

// Утиліти
window.app.utils = {
    // Дебаунс функція
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Форматування ціни
    formatPrice(price) {
        if (typeof price === 'string') {
            price = parseFloat(price.replace(/[^\d.,]/g, '').replace(',', '.'));
        }
        return price.toLocaleString('uk-UA') + ' ₴';
    },

    // Отримання CSRF токена
    getCSRFToken() {
        return document.querySelector('[name=csrf-token]')?.content ||
            document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            '';
    },

    // Перевірка на мобільний пристрій
    isMobile() {
        return window.innerWidth <= 768;
    },

    // Плавна прокрутка до елемента
    scrollTo(element, offset = 0) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            const elementPosition = element.offsetTop - offset;
            window.scrollTo({
                top: elementPosition,
                behavior: 'smooth'
            });
        }
    }
};

// ===== НАВІГАЦІЯ =====
// Використовуємо новий оптимізований мобільний меню
window.app.nav = window.mobileMenu;

// ===== КОШИК =====
window.app.cart = {
    items: [],
    isOpen: false,

    init() {
        this.loadFromStorage();
        this.bindEvents();
        this.updateUI();
    },

    bindEvents() {
        const cartBtn = document.getElementById('cart-btn');
        const cartModal = document.getElementById('cart-modal');
        const cartClose = document.getElementById('cart-close');
        const cartOverlay = document.getElementById('cart-overlay');
        const checkoutForm = document.getElementById('checkout-form');

        if (cartBtn) {
            cartBtn.addEventListener('click', () => this.toggleModal());
        }

        if (cartClose) {
            cartClose.addEventListener('click', () => this.closeModal());
        }

        if (cartOverlay) {
            cartOverlay.addEventListener('click', () => this.closeModal());
        }

        if (checkoutForm) {
            checkoutForm.addEventListener('submit', (e) => this.handleCheckout(e));
        }

        // Закриття модалки клавішею Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeModal();
            }
        });
    },

    addItem(productData) {
        const existingItem = this.items.find(item => item.id === productData.id);

        if (existingItem) {
            existingItem.quantity += productData.quantity || 1;
        } else {
            this.items.push({
                id: productData.id,
                name: productData.name,
                price: productData.price,
                image: productData.image,
                quantity: productData.quantity || 1
            });
        }

        this.saveToStorage();
        this.updateUI();
        this.showNotification(`${productData.name} додано до кошика`);
    },

    removeItem(productId) {
        this.items = this.items.filter(item => item.id !== productId);
        this.saveToStorage();
        this.updateUI();
    },

    updateQuantity(productId, quantity) {
        const item = this.items.find(item => item.id === productId);
        if (item) {
            if (quantity <= 0) {
                this.removeItem(productId);
            } else {
                item.quantity = quantity;
                this.saveToStorage();
                this.updateUI();
            }
        }
    },

    clearCart() {
        this.items = [];
        this.saveToStorage();
        this.updateUI();
    },

    getTotal() {
        return this.items.reduce((total, item) => {
            const price = typeof item.price === 'string'
                ? parseFloat(item.price.replace(/[^\d.,]/g, '').replace(',', '.'))
                : item.price;
            return total + (price * item.quantity);
        }, 0);
    },

    getItemCount() {
        return this.items.reduce((count, item) => count + item.quantity, 0);
    },

    saveToStorage() {
        try {
            localStorage.setItem('cart', JSON.stringify(this.items));
        } catch (e) {
            console.warn('Не вдалося зберегти кошик:', e);
        }
    },

    loadFromStorage() {
        try {
            const saved = localStorage.getItem('cart');
            this.items = saved ? JSON.parse(saved) : [];
        } catch (e) {
            console.warn('Не вдалося завантажити кошик:', e);
            this.items = [];
        }
    },

    clearLocalStorage() {
        try {
            localStorage.removeItem('cart');
            this.items = [];
            this.updateUI();
            this.showNotification('Кошик очищено');
        } catch (e) {
            console.warn('Не вдалося очистити кошик:', e);
        }
    },

    updateUI() {
        this.updateCartCount();
        this.updateCartModal();
    },

    updateCartCount() {
        const cartCount = document.getElementById('cart-count');
        if (cartCount) {
            const count = this.getItemCount();
            cartCount.textContent = count;
            cartCount.style.display = count > 0 ? 'flex' : 'none';
        }
    },

    updateCartModal() {
        const cartItems = document.getElementById('cart-items');
        const cartTotal = document.getElementById('cart-total');
        const orderForm = document.getElementById('order-form');

        if (!cartItems) return;

        if (this.items.length === 0) {
            cartItems.innerHTML = '<div class="cart-empty">Кошик порожній</div>';
            if (orderForm) orderForm.style.display = 'none';
        } else {
            cartItems.innerHTML = this.items.map(item => this.renderCartItem(item)).join('');
            if (orderForm) orderForm.style.display = 'block';

            // Прив'язка подій для кнопок
            this.bindCartItemEvents();
        }

        if (cartTotal) {
            cartTotal.textContent = window.app.utils.formatPrice(this.getTotal());
        }
    },

    renderCartItem(item) {
        return `
      <div class="cart-item" data-id="${item.id}">
        <img src="${item.image}" alt="${item.name}" class="cart-item__image">
        <div class="cart-item__info">
          <h4 class="cart-item__title">${item.name}</h4>
          <div class="cart-item__price">${window.app.utils.formatPrice(item.price)}</div>
          <div class="cart-item__controls">
            <button class="cart-item__qty-btn cart-item__minus" data-id="${item.id}">−</button>
            <span class="cart-item__quantity">${item.quantity}</span>
            <button class="cart-item__qty-btn cart-item__plus" data-id="${item.id}">+</button>
            <button class="cart-item__remove" data-id="${item.id}">Видалити</button>
          </div>
        </div>
      </div>
    `;
    },

    bindCartItemEvents() {
        const cartItems = document.getElementById('cart-items');
        if (!cartItems) return;

        cartItems.addEventListener('click', (e) => {
            const productId = parseInt(e.target.dataset.id);

            if (e.target.classList.contains('cart-item__plus')) {
                const item = this.items.find(item => item.id === productId);
                if (item) {
                    this.updateQuantity(productId, item.quantity + 1);
                }
            }

            if (e.target.classList.contains('cart-item__minus')) {
                const item = this.items.find(item => item.id === productId);
                if (item) {
                    this.updateQuantity(productId, item.quantity - 1);
                }
            }

            if (e.target.classList.contains('cart-item__remove')) {
                this.removeItem(productId);
            }
        });
    },

    toggleModal() {
        if (this.isOpen) {
            this.closeModal();
        } else {
            this.openModal();
        }
    },

    openModal() {
        const cartModal = document.getElementById('cart-modal');
        if (cartModal) {
            cartModal.classList.add('active');
            this.isOpen = true;
            document.body.style.overflow = 'hidden';
            this.updateCartModal();
        }
    },

    closeModal() {
        const cartModal = document.getElementById('cart-modal');
        if (cartModal) {
            cartModal.classList.remove('active');
            this.isOpen = false;
            document.body.style.overflow = '';
        }
    },

    async handleCheckout(e) {
        e.preventDefault();

        if (this.items.length === 0) {
            this.showNotification('Кошик порожній', 'error');
            return;
        }

        const formData = new FormData(e.target);
        const orderData = {
            items: this.items,
            customer: {
                name: formData.get('name'),
                phone: formData.get('phone'),
                email: formData.get('email'),
                comment: formData.get('comment')
            },
            total: this.getTotal()
        };

        try {
            const response = await fetch('/api/orders/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.app.utils.getCSRFToken()
                },
                body: JSON.stringify(orderData)
            });

            if (response.ok) {
                this.showNotification('Замовлення успішно відправлено!', 'success');
                this.clearCart();
                this.closeModal();
                e.target.reset();
            } else {
                throw new Error('Помилка відправки замовлення');
            }
        } catch (error) {
            console.error('Помилка:', error);
            this.showNotification('Помилка відправки замовлення. Спробуйте пізніше.', 'error');
        }
    },

    showNotification(message, type = 'success') {
        // Створення та показ сповіщення
        const notification = document.createElement('div');
        notification.className = `notification notification--${type}`;
        notification.textContent = message;

        // Стилі для сповіщення
        Object.assign(notification.style, {
            position: 'fixed',
            top: '100px',
            right: '20px',
            background: type === 'success' ? '#10b981' : '#ef4444',
            color: 'white',
            padding: '12px 20px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            zIndex: getComputedStyle(document.documentElement).getPropertyValue('--z-notification').trim() || '9800',
            fontSize: '14px',
            fontWeight: '500',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease'
        });

        document.body.appendChild(notification);

        // Анімація появи
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Видалення через 3 секунди
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
};

// ===== iOS SAFARI VIEWPORT FIX =====
function fixIOSViewport() {
    // Простіший fix для viewport проблем на iOS
    function setVH() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    setVH();
    window.addEventListener('resize', setVH);
    window.addEventListener('orientationchange', () => {
        setTimeout(setVH, 100);
    });
}

// ===== ІНІЦІАЛІЗАЦІЯ =====
document.addEventListener('DOMContentLoaded', () => {
    // Ініціалізуємо компоненти
    window.app.nav.init();
    window.app.cart.init();

    // iOS viewport fix
    fixIOSViewport();

    // Глобальні функції для зворотної сумісності
    window.cart = window.app.cart;
    window.addToCart = (productData) => window.app.cart.addItem(productData);
});

// Експорт для використання в інших модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.app;
} 