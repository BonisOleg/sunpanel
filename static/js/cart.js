// Корзина товарів
class ShoppingCart {
    constructor() {
        console.log('ShoppingCart constructor викликано');
        this.cart = this.loadCart();
        this.initEventListeners();
        this.updateCartDisplay();

        // Якщо є товари в корзині - одразу рендеримо їх
        if (this.cart.length > 0) {
            console.log('Знайдено товари в корзині при ініціалізації, рендерю...');
            setTimeout(() => {
                this.renderCartItems();
            }, 100);
        }

        console.log('ShoppingCart ініціалізовано з корзиною:', this.cart);
    }

    // Завантаження корзини з localStorage
    loadCart() {
        const savedCart = localStorage.getItem('shoppingCart');
        console.log('localStorage shoppingCart:', savedCart);
        const cart = savedCart ? JSON.parse(savedCart) : [];
        console.log('Завантажена корзина:', cart);
        return cart;
    }

    // Збереження корзини в localStorage
    saveCart() {
        localStorage.setItem('shoppingCart', JSON.stringify(this.cart));
    }

    // Додавання товару в корзину
    addToCart(product) {
        console.log('addToCart викликано з:', product);
        const existingItem = this.cart.find(item => item.id === product.id);

        if (existingItem) {
            console.log('Товар вже існує, збільшую кількість');
            existingItem.quantity += 1;
        } else {
            console.log('Додаю новий товар');
            this.cart.push({
                id: product.id,
                name: product.name,
                price: parseFloat(product.price),
                image: product.image || '',
                quantity: 1
            });
        }

        console.log('Корзина після додавання:', this.cart);
        this.saveCart();
        this.updateCartDisplay();
        this.showAddToCartNotification(product.name);
    }

    // Видалення товару з корзини
    removeFromCart(productId) {
        console.log('removeFromCart викликано для:', productId);
        console.log('Корзина до видалення:', this.cart);
        this.cart = this.cart.filter(item => item.id !== productId);
        console.log('Корзина після видалення:', this.cart);
        this.saveCart();
        this.updateCartDisplay();
        this.renderCartItems();
    }

    // Зміна кількості товару
    updateQuantity(productId, newQuantity) {
        console.log('updateQuantity викликано для:', productId, 'нова кількість:', newQuantity);
        const item = this.cart.find(item => item.id === productId);
        if (item) {
            if (newQuantity <= 0) {
                console.log('Кількість <= 0, видаляю товар');
                this.removeFromCart(productId);
            } else {
                console.log('Оновлюю кількість з', item.quantity, 'на', newQuantity);
                item.quantity = newQuantity;
                this.saveCart();
                this.updateCartDisplay();
                this.renderCartItems();
            }
        } else {
            console.log('Товар не знайдено в корзині:', productId);
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
        console.log('updateCartDisplay викликано');
        const cartCount = document.getElementById('cart-count');
        const cartTotal = document.getElementById('cart-total');

        if (cartCount) {
            const totalQuantity = this.getTotalQuantity();
            console.log('Оновлюю кількість товарів:', totalQuantity);
            cartCount.textContent = totalQuantity;
            cartCount.style.display = totalQuantity > 0 ? 'block' : 'none';
        } else {
            console.log('Елемент cart-count не знайдено');
        }

        if (cartTotal) {
            const totalPrice = this.getTotalPrice();
            console.log('Оновлюю загальну суму:', totalPrice);
            cartTotal.textContent = `₴${totalPrice.toFixed(2)}`;
        } else {
            console.log('Елемент cart-total не знайдено');
        }
    }

    // Рендер товарів в корзині
    renderCartItems() {
        console.log('renderCartItems викликано');
        const cartItemsContainer = document.getElementById('cart-items');
        const cartModal = document.getElementById('cart-modal');
        const cartContent = cartModal?.querySelector('.cart-modal__content');

        console.log('cartItemsContainer:', cartItemsContainer);
        console.log('this.cart:', this.cart);

        if (!cartItemsContainer) {
            console.error('Не знайдено елемент cart-items');
            return;
        }

        // Встановлюємо режим перегляду корзини
        if (cartContent) {
            cartContent.className = 'cart-modal__content cart-view';
        }

        if (this.cart.length === 0) {
            console.log('Корзина порожня');
            cartItemsContainer.innerHTML = `
                <div class="cart-empty">
                    <p>Корзина порожня</p>
                    <p>Додайте товари з каталогу</p>
                </div>
            `;
            return;
        }

        console.log('Рендерю товари:', this.cart.length);

        // Рендеримо товари
        const itemsHTML = this.cart.map(item => `
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

        // Додаємо кнопку оформлення замовлення
        const checkoutButton = `
            <div style="padding: 1.5rem; text-align: center;">
                <button class="cart-checkout-btn" id="checkout-btn" ${this.cart.length === 0 ? 'disabled' : ''}>
                    <span>🛒</span> Оформити замовлення
                </button>
            </div>
        `;

        cartItemsContainer.innerHTML = itemsHTML + checkoutButton;

        console.log('HTML згенеровано:', cartItemsContainer.innerHTML.length, 'символів');

        // Додаємо обробник для кнопки оформлення
        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', () => {
                this.showCheckoutForm();
            });
        }
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

        // Закриття корзини - поліпшена версія
        document.addEventListener('click', (e) => {
            // Закриття по кліку на хрестик
            if (e.target.matches('#cart-close') || e.target.closest('#cart-close')) {
                e.preventDefault();
                this.closeCart();
                return;
            }

            // Закриття по кліку на оверлей
            if (e.target.matches('#cart-overlay')) {
                e.preventDefault();
                this.closeCart();
                return;
            }
        });

        // Додавання товарів в корзину
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('add-to-cart-btn')) {
                e.preventDefault();
                const button = e.target;
                console.log('Натиснуто кнопку додавання товару');
                console.log('Кнопка:', button);
                console.log('Dataset:', button.dataset);

                const product = {
                    id: button.dataset.productId,
                    name: button.dataset.productName,
                    price: button.dataset.productPrice,
                    image: button.dataset.productImage
                };

                console.log('Дані товару:', product);

                // Перевіряємо чи всі дані є
                if (!product.id || !product.name || !product.price) {
                    console.error('Відсутні обов\'язкові дані товару:', product);
                    alert('Помилка: не вдалося додати товар до корзини (відсутні дані)');
                    return;
                }

                this.addToCart(product);
            }
        });

        // Керування кількістю товарів в корзині
        document.addEventListener('click', (e) => {
            // Знаходимо productId з правильного елемента
            let productId = e.target.dataset.productId;
            let button = null;

            // Для кнопки плюс
            if (e.target.classList.contains('plus')) {
                productId = e.target.dataset.productId;
                console.log('Натиснуто плюс для товару:', productId);
                const item = this.cart.find(item => item.id === productId);
                if (item) {
                    this.updateQuantity(productId, item.quantity + 1);
                }
            }

            // Для кнопки мінус
            if (e.target.classList.contains('minus')) {
                productId = e.target.dataset.productId;
                console.log('Натиснуто мінус для товару:', productId);
                const item = this.cart.find(item => item.id === productId);
                if (item) {
                    this.updateQuantity(productId, item.quantity - 1);
                }
            }

            // Для кнопки видалення (обробляємо SVG та саму кнопку)
            button = e.target.closest('.remove-btn');
            if (button) {
                productId = button.dataset.productId;
                console.log('Натиснуто видалення для товару:', productId);
                if (productId) {
                    this.removeFromCart(productId);
                }
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
        console.log('Відкриваю корзину...');
        const modal = document.getElementById('cart-modal');
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            console.log('Корзина відкрита, класи:', modal.classList.toString());

            // Завжди показуємо спочатку список товарів
            this.showCartItems();

        } else {
            console.error('Не знайдено елемент cart-modal');
        }
    }

    // Закриття корзини
    closeCart() {
        console.log('Закриваю корзину...');
        const modal = document.getElementById('cart-modal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
            console.log('Корзина закрита, класи:', modal.classList.toString());
        } else {
            console.error('Не знайдено елемент cart-modal');
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

    // Відправка замовлення на сервер
    async simulateOrderSubmission(orderData) {
        // Отримання CSRF токена
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            document.querySelector('meta[name="csrf-token"]')?.content;

        const response = await fetch('/api/orders/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                ...orderData,
                csrfmiddlewaretoken: csrfToken
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Помилка сервера');
        }

        return await response.json();
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

    // Методи для відлагодження (доступні через консоль)
    debugCart() {
        console.log('=== ВІДЛАГОДЖЕННЯ КОРЗИНИ ===');
        console.log('Корзина:', this.cart);
        console.log('Загальна кількість:', this.getTotalQuantity());
        console.log('Загальна сума:', this.getTotalPrice());
        console.log('LocalStorage:', localStorage.getItem('shoppingCart'));

        const modal = document.getElementById('cart-modal');
        const cartItems = document.getElementById('cart-items');
        console.log('Модальне вікно:', modal);
        console.log('Контейнер товарів:', cartItems);
        console.log('Модальне вікно активне:', modal?.classList.contains('active'));

        if (cartItems) {
            console.log('HTML контейнера товарів:', cartItems.innerHTML);
        }
    }

    clearDebugCart() {
        localStorage.removeItem('shoppingCart');
        this.cart = [];
        this.updateCartDisplay();
        console.log('Корзина очищена');
    }

    // Метод для швидкого тестування
    addTestItems() {
        console.log('Додаю тестові товари...');
        const testProducts = [
            {
                id: 'test1',
                name: 'Тестовий інвертор',
                price: '15000',
                image: '/static/images/test1.jpg'
            },
            {
                id: 'test2',
                name: 'Тестова панель',
                price: '5000',
                image: '/static/images/test2.jpg'
            }
        ];

        testProducts.forEach(product => {
            this.addToCart(product);
        });

        console.log('Тестові товари додані');
        return this.cart;
    }

    // Примусовий рендеринг для тестування
    forceRender() {
        console.log('=== ПРИМУСОВИЙ РЕНДЕРИНГ ===');
        const cartItems = document.getElementById('cart-items');
        console.log('Контейнер cart-items:', cartItems);
        console.log('Товари в корзині:', this.cart);

        if (!cartItems) {
            console.error('ПОМИЛКА: Контейнер cart-items не знайдено!');
            return;
        }

        if (this.cart.length === 0) {
            console.log('Корзина порожня - додаю тестові товари...');
            this.addTestItems();
        }

        // Примусово очищаємо та рендеримо
        cartItems.innerHTML = '';
        this.renderCartItems();

        console.log('Після рендерингу:');
        console.log('HTML:', cartItems.innerHTML);
        console.log('Видимість:', cartItems.style.display);
        console.log('Висота:', cartItems.offsetHeight);

        return cartItems.innerHTML;
    }

    // Показати форму оформлення замовлення
    showCheckoutForm() {
        console.log('Показую форму оформлення замовлення');
        const cartModal = document.getElementById('cart-modal');
        const cartContent = cartModal?.querySelector('.cart-modal__content');

        if (cartContent) {
            cartContent.className = 'cart-modal__content order-view';
        }

        // Оновлюємо форму з інформацією про замовлення
        this.updateOrderForm();
    }

    // Показати список товарів корзини  
    showCartItems() {
        console.log('Показую список товарів');
        const cartModal = document.getElementById('cart-modal');
        const cartContent = cartModal?.querySelector('.cart-modal__content');

        if (cartContent) {
            cartContent.className = 'cart-modal__content cart-view';
        }

        // Перерендерюємо товари
        this.renderCartItems();
    }

    // Оновлення форми замовлення з резюме
    updateOrderForm() {
        const orderForm = document.getElementById('order-form');
        if (!orderForm) return;

        const totalQuantity = this.getTotalQuantity();
        const totalPrice = this.getTotalPrice();

        // Створюємо резюме замовлення
        const orderSummary = `
            <div class="order-form__header">
                <h3 class="order-form__title">Оформлення замовлення</h3>
                <p class="order-form__subtitle">Заповніть ваші контактні дані для оформлення замовлення</p>
            </div>
            
            <div class="order-form__summary">
                <div class="order-form__summary-title">Резюме замовлення:</div>
                <div class="order-form__summary-items">Товарів у кошику: ${totalQuantity} шт.</div>
                <div class="order-form__summary-total">До сплати: ₴${totalPrice.toFixed(2)}</div>
            </div>
        `;

        // Знаходимо форму та додаємо резюме перед нею
        const form = orderForm.querySelector('#checkout-form');
        if (form) {
            // Видаляємо старе резюме якщо є
            const existingSummary = orderForm.querySelector('.order-form__header');
            if (existingSummary) {
                existingSummary.remove();
            }
            const existingSummaryBlock = orderForm.querySelector('.order-form__summary');
            if (existingSummaryBlock) {
                existingSummaryBlock.remove();
            }

            // Додаємо нове резюме
            form.insertAdjacentHTML('beforebegin', orderSummary);

            // Додаємо кнопку "Назад до корзини" якщо її немає
            this.addBackToCartButton(form);
        }
    }

    // Додавання кнопки повернення до корзини
    addBackToCartButton(form) {
        // Перевіряємо чи вже є кнопка
        const existingBackBtn = form.querySelector('.back-to-cart-btn');
        if (existingBackBtn) return;

        // Знаходимо кнопку відправити
        const submitBtn = form.querySelector('.order-btn');
        if (submitBtn) {
            // Створюємо контейнер для кнопок
            const buttonsContainer = document.createElement('div');
            buttonsContainer.className = 'form-buttons';

            // Створюємо кнопку назад
            const backBtn = document.createElement('button');
            backBtn.type = 'button';
            backBtn.className = 'back-to-cart-btn';
            backBtn.innerHTML = '← Назад до корзини';
            backBtn.addEventListener('click', () => {
                this.showCartItems();
            });

            // Переносимо кнопки в контейнер
            buttonsContainer.appendChild(backBtn);
            buttonsContainer.appendChild(submitBtn.cloneNode(true));

            // Замінюємо стару кнопку новим контейнером
            submitBtn.parentNode.replaceChild(buttonsContainer, submitBtn);
        }
    }
}

// Ініціалізація корзини при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    window.shoppingCart = new ShoppingCart();

    // Інструкції для відлагодження в консолі
    console.log('%c=== КОРЗИНА ІНІЦІАЛІЗОВАНА ===', 'color: green; font-weight: bold;');
    console.log('%c🛒 Нова функціональність: Двостанова корзина!', 'color: blue; font-weight: bold;');
    console.log('Доступні команди для відлагодження:');
    console.log('- shoppingCart.debugCart() - показати стан корзини');
    console.log('- shoppingCart.clearDebugCart() - очистити корзину');
    console.log('- shoppingCart.addTestItems() - додати тестові товари');
    console.log('- shoppingCart.forceRender() - 🔥 ПРИМУСОВИЙ РЕНДЕРИНГ');
    console.log('- shoppingCart.showCartItems() - 📦 ПОКАЗАТИ ТОВАРИ');
    console.log('- shoppingCart.showCheckoutForm() - 📋 ПОКАЗАТИ ФОРМУ');
    console.log('- shoppingCart.openCart() - відкрити корзину');
    console.log('- shoppingCart.closeCart() - закрити корзину');
});

// Стилі тепер підключаються через окремий CSS файл cart-modal.css 