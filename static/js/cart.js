// Корзина товарів
class ShoppingCart {
    constructor() {
        this.cart = this.loadCart();
        this.initEventListeners();
        this.updateCartDisplay();
    }

    // Завантаження корзини з localStorage
    loadCart() {
        const savedCart = localStorage.getItem('shoppingCart');
        return savedCart ? JSON.parse(savedCart) : [];
    }

    // Збереження корзини в localStorage
    saveCart() {
        localStorage.setItem('shoppingCart', JSON.stringify(this.cart));
    }

    // Додавання товару в корзину
    addToCart(product) {
        const existingItem = this.cart.find(item => item.id === product.id);

        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.cart.push({
                id: product.id,
                name: product.name,
                price: parseFloat(product.price),
                image: product.image || '',
                quantity: 1
            });
        }

        this.saveCart();
        this.updateCartDisplay();
        this.showAddToCartNotification(product.name);
    }

    // Видалення товару з корзини
    removeFromCart(productId) {
        this.cart = this.cart.filter(item => item.id !== productId);
        this.saveCart();
        this.updateCartDisplay();
        this.renderCartItems();
    }

    // Зміна кількості товару
    updateQuantity(productId, newQuantity) {
        const item = this.cart.find(item => item.id === productId);
        if (item) {
            if (newQuantity <= 0) {
                this.removeFromCart(productId);
            } else {
                item.quantity = newQuantity;
                this.saveCart();
                this.updateCartDisplay();
                this.renderCartItems();
            }
        }
    }

    // Отримання загальної кількості товарів
    getTotalQuantity() {
        return this.cart.reduce((total, item) => total + item.quantity, 0);
    }

    // Отримання загальної суми
    getTotalPrice() {
        return this.cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    }

    // Оновлення відображення корзини
    updateCartDisplay() {
        const cartCount = document.getElementById('cart-count');
        const cartTotal = document.getElementById('cart-total');

        if (cartCount) {
            const totalQuantity = this.getTotalQuantity();
            cartCount.textContent = totalQuantity;
            cartCount.style.display = totalQuantity > 0 ? 'block' : 'none';
        }

        if (cartTotal) {
            cartTotal.textContent = `₴${this.getTotalPrice().toFixed(2)}`;
        }
    }

    // Рендер товарів в корзині
    renderCartItems() {
        const cartItemsContainer = document.getElementById('cart-items');
        if (!cartItemsContainer) return;

        if (this.cart.length === 0) {
            cartItemsContainer.innerHTML = `
                <div class="cart-empty">
                    <p>Корзина порожня</p>
                    <p>Додайте товари з каталогу</p>
                </div>
            `;
            return;
        }

        cartItemsContainer.innerHTML = this.cart.map(item => `
            <div class="cart-item" data-product-id="${item.id}">
                <div class="cart-item__image">
                    ${item.image ?
                `<img src="${item.image}" alt="${item.name}" class="cart-item__img">` :
                `<div class="cart-item__placeholder">Немає фото</div>`
            }
                </div>
                <div class="cart-item__content">
                    <h4 class="cart-item__name">${item.name}</h4>
                    <div class="cart-item__price">₴${item.price.toFixed(2)}</div>
                </div>
                <div class="cart-item__controls">
                    <div class="quantity-controls">
                        <button class="quantity-btn minus" data-product-id="${item.id}">-</button>
                        <span class="quantity-value">${item.quantity}</span>
                        <button class="quantity-btn plus" data-product-id="${item.id}">+</button>
                    </div>
                    <button class="remove-btn" data-product-id="${item.id}">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M4 4L12 12M4 12L12 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
                <div class="cart-item__total">₴${(item.price * item.quantity).toFixed(2)}</div>
            </div>
        `).join('');
    }

    // Показати сповіщення про додавання товару
    showAddToCartNotification(productName) {
        const notification = document.createElement('div');
        notification.className = 'cart-notification';
        notification.innerHTML = `
            <div class="cart-notification__content">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10 0C4.5 0 0 4.5 0 10s4.5 10 10 10 10-4.5 10-10S15.5 0 10 0zm4.2 7.7l-5 5c-.2.2-.4.3-.7.3s-.5-.1-.7-.3l-2.5-2.5c-.4-.4-.4-1 0-1.4s1-.4 1.4 0L8.5 11l4.3-4.3c.4-.4 1-.4 1.4 0s.4 1 0 1.4z"/>
                </svg>
                <span>Товар "${productName}" додано в корзину</span>
            </div>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 100);

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Ініціалізація слухачів подій
    initEventListeners() {
        // Відкриття корзини
        document.addEventListener('click', (e) => {
            if (e.target.closest('#cart-btn')) {
                this.openCart();
            }
        });

        // Закриття корзини
        document.addEventListener('click', (e) => {
            if (e.target.matches('#cart-close') || e.target.matches('#cart-overlay')) {
                this.closeCart();
            }
        });

        // Додавання товарів в корзину
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('add-to-cart-btn')) {
                e.preventDefault();
                const button = e.target;
                const product = {
                    id: button.dataset.productId,
                    name: button.dataset.productName,
                    price: button.dataset.productPrice,
                    image: button.dataset.productImage
                };
                this.addToCart(product);
            }
        });

        // Керування кількістю товарів в корзині
        document.addEventListener('click', (e) => {
            const productId = e.target.dataset.productId;

            if (e.target.classList.contains('plus')) {
                const item = this.cart.find(item => item.id === productId);
                if (item) {
                    this.updateQuantity(productId, item.quantity + 1);
                }
            }

            if (e.target.classList.contains('minus')) {
                const item = this.cart.find(item => item.id === productId);
                if (item) {
                    this.updateQuantity(productId, item.quantity - 1);
                }
            }

            if (e.target.classList.contains('remove-btn') || e.target.closest('.remove-btn')) {
                this.removeFromCart(productId);
            }
        });

        // Обробка форми замовлення
        document.addEventListener('submit', (e) => {
            if (e.target.matches('#checkout-form')) {
                e.preventDefault();
                this.handleCheckout(e.target);
            }
        });

        // Закриття корзини клавішею Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeCart();
            }
        });
    }

    // Відкриття корзини
    openCart() {
        const modal = document.getElementById('cart-modal');
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            this.renderCartItems();
        }
    }

    // Закриття корзини
    closeCart() {
        const modal = document.getElementById('cart-modal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    // Обробка замовлення
    async handleCheckout(form) {
        const formData = new FormData(form);
        const orderData = {
            name: formData.get('name'),
            phone: formData.get('phone'),
            email: formData.get('email'),
            comment: formData.get('comment'),
            items: this.cart,
            total: this.getTotalPrice()
        };

        try {
            // Тут можна відправити дані на сервер
            console.log('Дані замовлення:', orderData);

            // Симуляція відправки
            await this.simulateOrderSubmission(orderData);

            // Очищення корзини після успішного замовлення
            this.clearCart();
            this.closeCart();
            this.showOrderSuccessMessage();

        } catch (error) {
            console.error('Помилка при оформленні замовлення:', error);
            alert('Помилка при оформленні замовлення. Спробуйте ще раз.');
        }
    }

    // Симуляція відправки замовлення (можна замінити на реальний API)
    simulateOrderSubmission(orderData) {
        return new Promise((resolve) => {
            setTimeout(() => {
                // Тут можна відправити дані на сервер
                // fetch('/api/orders', { method: 'POST', body: JSON.stringify(orderData) })
                resolve();
            }, 1000);
        });
    }

    // Очищення корзини
    clearCart() {
        this.cart = [];
        this.saveCart();
        this.updateCartDisplay();
    }

    // Показати повідомлення про успішне замовлення
    showOrderSuccessMessage() {
        const notification = document.createElement('div');
        notification.className = 'order-success-notification';
        notification.innerHTML = `
            <div class="order-success-notification__content">
                <div class="success-icon">✓</div>
                <h3>Замовлення оформлено!</h3>
                <p>Ми зв'яжемося з вами найближчим часом</p>
            </div>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '1';
        }, 100);

        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
}

// Ініціалізація корзини при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    window.shoppingCart = new ShoppingCart();
});

// Стилі для сповіщень
const cartStyles = `
<style>
.cart-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #28a745;
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    z-index: 10000;
    opacity: 0;
    transform: translateY(-20px);
    transition: all 0.3s ease;
}

.cart-notification__content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.order-success-notification {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    z-index: 10000;
    opacity: 0;
    transition: opacity 0.3s ease;
    text-align: center;
    min-width: 300px;
}

.success-icon {
    width: 60px;
    height: 60px;
    background: #28a745;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    font-weight: bold;
    margin: 0 auto 1rem;
}

.cart-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 9999;
    display: none;
}

.cart-modal.active {
    display: block;
}

.cart-modal__overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
}

.cart-modal__content {
    position: absolute;
    top: 0;
    right: 0;
    width: 100%;
    max-width: 400px;
    height: 100%;
    background: white;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
}

.cart-modal__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #e1e5e9;
}

.cart-modal__title {
    font-size: 1.3rem;
    font-weight: 600;
    margin: 0;
}

.cart-modal__close {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 6px;
    transition: background 0.3s ease;
}

.cart-modal__close:hover {
    background: #f8f9fa;
}

.cart-modal__items {
    flex: 1;
    padding: 1rem;
}

.cart-empty {
    text-align: center;
    padding: 2rem;
    color: #666;
}

.cart-item {
    display: grid;
    grid-template-columns: 60px 1fr auto auto;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid #f0f0f0;
    align-items: center;
}

.cart-item__image {
    width: 60px;
    height: 60px;
    border-radius: 8px;
    overflow: hidden;
}

.cart-item__img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.cart-item__placeholder {
    width: 100%;
    height: 100%;
    background: #f8f9fa;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    color: #666;
}

.cart-item__name {
    font-size: 0.9rem;
    font-weight: 500;
    margin: 0 0 0.25rem 0;
    line-height: 1.3;
}

.cart-item__price {
    font-size: 0.8rem;
    color: #666;
}

.cart-item__controls {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    align-items: center;
}

.quantity-controls {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.quantity-btn {
    width: 24px;
    height: 24px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
}

.quantity-value {
    font-size: 0.8rem;
    font-weight: 500;
    min-width: 20px;
    text-align: center;
}

.remove-btn {
    background: none;
    border: none;
    cursor: pointer;
    color: #dc3545;
    padding: 0.25rem;
    border-radius: 4px;
    transition: background 0.3s ease;
}

.remove-btn:hover {
    background: #f8f9fa;
}

.cart-item__total {
    font-weight: 600;
    font-size: 0.9rem;
    color: #007bff;
}

.cart-modal__total {
    padding: 1rem 1.5rem;
    border-top: 1px solid #e1e5e9;
    background: #f8f9fa;
}

.cart-total {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1.1rem;
    font-weight: 600;
}

.cart-total__amount {
    color: #007bff;
}

.cart-modal__order-form {
    padding: 1.5rem;
    border-top: 1px solid #e1e5e9;
}

.order-form__title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    font-size: 0.9rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: #333;
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #e1e5e9;
    border-radius: 6px;
    font-size: 0.9rem;
    transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #007bff;
}

.order-btn {
    width: 100%;
    padding: 0.75rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.3s ease;
}

.order-btn:hover {
    background: #0056b3;
}

.nav__cart {
    position: relative;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 6px;
    transition: background 0.3s ease;
}

.nav__cart:hover {
    background: rgba(255, 255, 255, 0.1);
}

.nav__cart-count {
    position: absolute;
    top: 0;
    right: 0;
    background: #ff6b35;
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.2rem 0.4rem;
    border-radius: 10px;
    min-width: 18px;
    text-align: center;
    display: none;
}

@media (max-width: 768px) {
    .cart-modal__content {
        max-width: 100%;
        width: 100%;
    }
    
    .cart-item {
        grid-template-columns: 50px 1fr auto;
        gap: 0.75rem;
    }
    
    .cart-item__image {
        width: 50px;
        height: 50px;
    }
    
    .cart-item__total {
        grid-column: 2;
        justify-self: start;
        margin-top: 0.5rem;
    }
    
    .cart-item__controls {
        grid-column: 3;
        grid-row: 1;
    }
}
</style>
`;

// Додавання стилів на сторінку
document.head.insertAdjacentHTML('beforeend', cartStyles); 