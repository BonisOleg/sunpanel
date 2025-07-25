/**
 * Shopping Cart Functionality for GreenSolarTech
 */

class ShoppingCart {
    constructor() {
        this.items = [];
        this.total = 0;
        this.modal = document.getElementById('cart-modal');
        this.overlay = document.getElementById('cart-overlay');
        this.closeBtn = document.getElementById('cart-close');
        this.cartBtn = document.getElementById('cart-btn');
        this.cartCount = document.getElementById('cart-count');
        this.cartItems = document.getElementById('cart-items');
        this.cartTotal = document.getElementById('cart-total');

        this.init();
    }

    init() {
        this.loadFromLocalStorage();
        this.updateCartDisplay();
        this.bindEvents();
    }

    bindEvents() {
        // Open cart modal
        if (this.cartBtn) {
            this.cartBtn.addEventListener('click', () => this.openModal());
        }

        // Close cart modal
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.closeModal());
        }

        if (this.overlay) {
            this.overlay.addEventListener('click', () => this.closeModal());
        }

        // Add to cart buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('add-to-cart-btn')) {
                e.preventDefault();
                this.addItem(e.target);
            }
        });

        // Close modal on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });

        // Handle order form submission
        const orderForm = document.getElementById('order-form');
        if (orderForm) {
            orderForm.addEventListener('submit', (e) => this.submitOrder(e));
        }
    }

    addItem(button) {
        const productId = button.dataset.productId;
        const productName = button.dataset.productName;
        const productPrice = parseFloat(button.dataset.productPrice);
        const productImage = button.dataset.productImage;

        if (!productId || !productName || !productPrice) {
            this.showMessage('Помилка: неповні дані товару', 'error');
            return;
        }

        // Check if item already exists
        const existingItem = this.items.find(item => item.id === productId);

        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.items.push({
                id: productId,
                name: productName,
                price: productPrice,
                image: productImage,
                quantity: 1
            });
        }

        this.saveToLocalStorage();
        this.updateCartDisplay();
        this.showMessage(`${productName} додано до кошика!`, 'success');

        // Animate button
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = 'scale(1)';
        }, 150);
    }

    removeItem(productId) {
        this.items = this.items.filter(item => item.id !== productId);
        this.saveToLocalStorage();
        this.updateCartDisplay();
        this.renderCartItems();
    }

    updateQuantity(productId, quantity) {
        const item = this.items.find(item => item.id === productId);
        if (item) {
            if (quantity <= 0) {
                this.removeItem(productId);
            } else {
                item.quantity = quantity;
                this.saveToLocalStorage();
                this.updateCartDisplay();
                this.renderCartItems();
            }
        }
    }

    calculateTotal() {
        this.total = this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        return this.total;
    }

    updateCartDisplay() {
        const totalItems = this.items.reduce((sum, item) => sum + item.quantity, 0);
        const total = this.calculateTotal();

        if (this.cartCount) {
            this.cartCount.textContent = totalItems;
            this.cartCount.style.display = totalItems > 0 ? 'block' : 'none';
        }

        if (this.cartTotal) {
            this.cartTotal.textContent = `₴${total.toLocaleString('uk-UA')}`;
        }

        this.renderCartItems();
    }

    renderCartItems() {
        if (!this.cartItems) return;

        if (this.items.length === 0) {
            this.cartItems.innerHTML = `
                <div class="cart-empty">
                    <p>Кошик порожній</p>
                    <p>Додайте товари з каталогу</p>
                </div>
            `;
            return;
        }

        const itemsHTML = this.items.map(item => `
            <div class="cart-item" data-id="${item.id}">
                <div class="cart-item__image">
                    <img src="${item.image || '/static/images/no-image.jpg'}" alt="${item.name}">
                </div>
                <div class="cart-item__details">
                    <h4 class="cart-item__name">${item.name}</h4>
                    <div class="cart-item__price">₴${item.price.toLocaleString('uk-UA')}</div>
                </div>
                <div class="cart-item__controls">
                    <div class="quantity-controls">
                        <button class="quantity-btn minus" onclick="window.cart.updateQuantity('${item.id}', ${item.quantity - 1})">-</button>
                        <span class="quantity">${item.quantity}</span>
                        <button class="quantity-btn plus" onclick="window.cart.updateQuantity('${item.id}', ${item.quantity + 1})">+</button>
                    </div>
                    <button class="remove-btn" onclick="window.cart.removeItem('${item.id}')" title="Видалити">×</button>
                </div>
                <div class="cart-item__subtotal">
                    ₴${(item.price * item.quantity).toLocaleString('uk-UA')}
                </div>
            </div>
        `).join('');

        this.cartItems.innerHTML = itemsHTML;
    }

    openModal() {
        if (this.modal) {
            this.modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            this.renderCartItems();
        }
    }

    closeModal() {
        if (this.modal) {
            this.modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    clearCart() {
        this.items = [];
        this.saveToLocalStorage();
        this.updateCartDisplay();
        this.showMessage('Кошик очищено', 'info');
    }

    clearLocalStorage() {
        if (confirm('Ви впевнені, що хочете очистити кошик?')) {
            this.clearCart();
        }
    }

    saveToLocalStorage() {
        try {
            localStorage.setItem('greensolartech_cart', JSON.stringify(this.items));
        } catch (e) {
            console.warn('Не вдалося зберегти кошик у localStorage:', e);
        }
    }

    loadFromLocalStorage() {
        try {
            const stored = localStorage.getItem('greensolartech_cart');
            if (stored) {
                this.items = JSON.parse(stored);
            }
        } catch (e) {
            console.warn('Не вдалося завантажити кошик з localStorage:', e);
            this.items = [];
        }
    }

    submitOrder(e) {
        e.preventDefault();

        if (this.items.length === 0) {
            this.showMessage('Кошик порожній', 'error');
            return;
        }

        const formData = new FormData(e.target);
        const orderData = {
            items: this.items,
            total: this.total,
            customer: {
                name: formData.get('name'),
                phone: formData.get('phone'),
                email: formData.get('email'),
                message: formData.get('message')
            }
        };

        // Send order to server
        fetch('/api/orders/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(orderData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showMessage('Замовлення успішно відправлено! Ми зв\'яжемося з вами найближчим часом.', 'success');
                    this.clearCart();
                    this.closeModal();
                    e.target.reset();
                } else {
                    this.showMessage('Помилка відправки замовлення. Спробуйте ще раз.', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.showMessage('Помилка з\'єднання. Спробуйте ще раз.', 'error');
            });
    }

    showMessage(message, type = 'info') {
        // Create notification
        const notification = document.createElement('div');
        notification.className = `cart-notification cart-notification--${type}`;
        notification.innerHTML = `
            <div class="cart-notification__content">
                <span class="cart-notification__message">${message}</span>
                <button class="cart-notification__close">&times;</button>
            </div>
        `;

        document.body.appendChild(notification);

        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);

        // Auto hide after 5 seconds
        const hideTimeout = setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);

        // Manual close
        notification.querySelector('.cart-notification__close').addEventListener('click', () => {
            clearTimeout(hideTimeout);
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        });
    }
}

// Initialize cart when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cart = new ShoppingCart();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ShoppingCart;
} 