/**
 * GreenSolarTech - Index Page Optimized JavaScript Bundle
 * Об'єднані та оптимізовані JS файли для головної сторінки
 * Includes: main-optimized.js + cart.js + callback.js + ios-video-optimizer.js
 */

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // =================================
    // Global Configuration & Utilities
    // =================================
    const AppConfig = {
        isMobile: window.innerWidth <= 768,
        isTablet: window.innerWidth > 768 && window.innerWidth <= 1024,
        isIOS: /iPad|iPhone|iPod/.test(navigator.userAgent),
        reducedMotion: window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
    };

    const Utils = {
        throttle: function (func, limit) {
            let inThrottle;
            return function () {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            }
        },

        debounce: function (func, wait) {
            let timeout;
            return function () {
                const context = this;
                const args = arguments;
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(context, args), wait);
            };
        },

        scrollTo: function (element, duration = 1000) {
            if (!element) return;

            let targetPosition;
            if (element.id === 'hero') {
                targetPosition = 0;
            } else {
                const rect = element.getBoundingClientRect();
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                targetPosition = rect.top + scrollTop - 80;
            }

            const startPosition = window.pageYOffset;
            const distance = targetPosition - startPosition;
            let startTime = null;

            function animation(currentTime) {
                if (startTime === null) startTime = currentTime;
                const timeElapsed = currentTime - startTime;
                const run = ease(timeElapsed, startPosition, distance, duration);
                window.scrollTo(0, run);
                if (timeElapsed < duration) requestAnimationFrame(animation);
            }

            function ease(t, b, c, d) {
                t /= d / 2;
                if (t < 1) return c / 2 * t * t + b;
                t--;
                return -c / 2 * (t * (t - 2) - 1) + b;
            }

            requestAnimationFrame(animation);
        },

        createObserver: function (callback, options = {}) {
            const defaultOptions = {
                threshold: 0.3,
                rootMargin: '0px 0px -10% 0px'
            };
            return new IntersectionObserver(callback, { ...defaultOptions, ...options });
        }
    };

    // =================================
    // Navigation System
    // =================================
    const Navigation = {
        init: function () {
            console.log('🚀 Navigation init started');
            this.nav = document.getElementById('nav');
            this.navToggle = document.getElementById('nav-toggle');
            this.navMenu = document.getElementById('nav-menu');
            this.navLinks = document.querySelectorAll('.nav__link');

            console.log('📍 Navigation elements found:', {
                nav: !!this.nav,
                navToggle: !!this.navToggle,
                navMenu: !!this.navMenu,
                navLinksCount: this.navLinks.length
            });

            if (!this.nav) {
                console.error('❌ Navigation element not found');
                return;
            }

            this.bindEvents();
            this.handleScroll();
            console.log('✅ Navigation initialized successfully');
        },

        bindEvents: function () {
            if (this.navToggle) {
                this.navToggle.addEventListener('click', () => this.toggleMobileMenu());
            }

            this.navLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    // Завжди закриваємо меню при кліку на посилання
                    this.closeMobileMenu();

                    const href = link.getAttribute('href');

                    if (href.startsWith('#')) {
                        e.preventDefault();
                        const targetElement = document.querySelector(href);
                        if (targetElement) {
                            Utils.scrollTo(targetElement);
                        }
                    } else if (href.includes('#') && window.location.pathname === href.split('#')[0]) {
                        e.preventDefault();
                        const anchor = '#' + href.split('#')[1];
                        const targetElement = document.querySelector(anchor);
                        if (targetElement) {
                            Utils.scrollTo(targetElement);
                        }
                    }
                });
            });

            window.addEventListener('scroll', Utils.throttle(() => {
                this.handleScroll();
            }, 16));

            // Закриття меню при кліку поза ним
            document.addEventListener('click', (e) => {
                const navList = document.querySelector('.nav__list');
                if (navList && navList.classList.contains('active')) {
                    // Якщо клік по фону меню
                    if (e.target === navList) {
                        this.closeMobileMenu();
                    }
                    // Або якщо клік поза навігацією взагалі
                    else if (this.nav && !this.nav.contains(e.target)) {
                        this.closeMobileMenu();
                    }
                }
            });
        },

        toggleMobileMenu: function () {
            const navList = document.querySelector('.nav__list');
            const navMenu = document.querySelector('.nav__menu');

            if (!navList || !navMenu) {
                console.error('Navigation menu not found');
                return;
            }

            // Toggle всіх необхідних елементів
            const isActive = navList.classList.toggle('active');
            navMenu.classList.toggle('active', isActive);

            if (this.navToggle) {
                this.navToggle.classList.toggle('active', isActive);
            }

            document.body.classList.toggle('nav-open', isActive);

            console.log('Menu toggled:', isActive ? 'opened' : 'closed');
        },

        closeMobileMenu: function () {
            const navList = document.querySelector('.nav__list');
            const navMenu = document.querySelector('.nav__menu');

            if (navList) {
                navList.classList.remove('active');
            }
            if (navMenu) {
                navMenu.classList.remove('active');
            }
            if (this.navToggle) {
                this.navToggle.classList.remove('active');
            }
            document.body.classList.remove('nav-open');
        },

        handleScroll: function () {
            const scrollY = window.pageYOffset;
            if (scrollY > 100) {
                this.nav.style.background = 'rgba(255, 255, 255, 0.98)';
                this.nav.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
            } else {
                this.nav.style.background = 'rgba(255, 255, 255, 0.95)';
                this.nav.style.boxShadow = 'none';
            }
        }
    };

    // =================================
    // Video System with Full iOS Optimization (RESTORED)
    // =================================
    const VideoSystem = {
        init: function () {
            this.isMobile = this.isMobileDevice();
            this.isIOS = this.isIOSDevice();
            this.isSafari = this.isSafariBrowser();

            console.log('🚀 Ініціалізація Video System...');
            console.log('📱 Стан детекції:', {
                isMobile: this.isMobile,
                isIOS: this.isIOS,
                isSafari: this.isSafari,
                screenWidth: window.innerWidth,
                userAgent: navigator.userAgent
            });

            this.setupAllVideos();
            this.setupAllImages();
            this.setupVideoObserver();
            this.bindEvents();

            // Додаткова перевірка через 1 секунду
            setTimeout(() => {
                this.checkVideoStatus();
            }, 1000);
        },

        isMobileDevice: function () {
            if (window.innerWidth <= 768) {
                console.log('Мобільний пристрій детектовано за шириною екрана:', window.innerWidth);
                return true;
            }
            if (window.navigator.webdriver || window.chrome?.runtime?.onConnect) {
                console.log('Chrome DevTools емуляція детектована');
                if (window.innerWidth <= 768) return true;
            }
            if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
                console.log('Touch підтримка детектована');
                if (window.innerWidth <= 768) return true;
            }
            const userAgent = navigator.userAgent || navigator.vendor || window.opera;
            const mobileRegex = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile|mobile|phone/i;
            if (mobileRegex.test(userAgent)) {
                console.log('Мобільний пристрій детектовано за User Agent:', userAgent);
                return true;
            }
            console.log('Десктопний пристрій детектовано');
            return false;
        },

        isIOSDevice: function () {
            const userAgent = navigator.userAgent || navigator.vendor || window.opera;
            return /iPad|iPhone|iPod/.test(userAgent) && !window.MSStream;
        },

        isSafariBrowser: function () {
            const userAgent = navigator.userAgent || navigator.vendor || window.opera;
            return /Safari/.test(userAgent) && /Apple Computer/.test(navigator.vendor);
        },

        setVideoSource: function (video) {
            const videoId = video.id || 'unknown';
            const mobileSrc = video.getAttribute('data-mobile-src');
            const desktopSrc = video.getAttribute('data-desktop-src');

            console.log(`Налаштування відео ${videoId}:`, {
                isMobile: this.isMobile,
                screenWidth: window.innerWidth,
                mobileSrc,
                desktopSrc,
                currentSrc: video.src
            });

            let targetSrc = null;

            if (this.isMobile && mobileSrc) {
                targetSrc = mobileSrc;
                console.log(`✅ Встановлюю мобільне відео для ${videoId}: ${mobileSrc}`);
            } else if (!this.isMobile && desktopSrc) {
                targetSrc = desktopSrc;
                console.log(`✅ Встановлюю десктопне відео для ${videoId}: ${desktopSrc}`);
            } else if (desktopSrc) {
                targetSrc = desktopSrc;
                console.log(`⚠️ Fallback на десктопне відео для ${videoId}: ${desktopSrc}`);
            }

            if (targetSrc) {
                const currentSrc = video.src || video.querySelector('source')?.src;

                if (currentSrc !== targetSrc) {
                    console.log(`🔄 Змінюю джерело відео ${videoId} з "${currentSrc}" на "${targetSrc}"`);
                    video.pause();
                    video.src = targetSrc;
                    const source = video.querySelector('source');
                    if (source) source.src = targetSrc;
                    video.load();
                    console.log(`✅ Відео ${videoId} успішно оновлено`);
                } else {
                    console.log(`ℹ️ Відео ${videoId} вже має правильне джерело`);
                }
            } else {
                console.error(`❌ Не знайдено підходящого джерела для відео ${videoId}`);
            }
        },

        setImageSource: function (img) {
            const mobileSrc = img.getAttribute('data-mobile-src');
            const desktopSrc = img.getAttribute('data-desktop-src');

            let targetSrc = null;
            if (this.isMobile && mobileSrc) {
                targetSrc = mobileSrc;
            } else if (!this.isMobile && desktopSrc) {
                targetSrc = desktopSrc;
            } else if (desktopSrc) {
                targetSrc = desktopSrc;
            }

            if (targetSrc && img.src !== targetSrc) {
                console.log(`🔄 Змінюю зображення з "${img.src}" на "${targetSrc}"`);
                img.src = targetSrc;
            }
        },

        setupVideo: function (video) {
            this.setVideoSource(video);

            // Загальні налаштування
            video.muted = true;
            video.setAttribute('playsinline', 'true');
            video.removeAttribute('controls');
            video.controls = false;

            // Спеціальні налаштування для iOS
            if (this.isIOS) {
                this.setupVideoForIOS(video);
            }

            // Налаштування preload для мобільних
            if (this.isMobile) {
                video.setAttribute('preload', 'metadata');
            }

            // Обробники подій
            video.addEventListener('loadstart', function () {
                console.log(`Завантаження відео: ${video.id}`);
            });

            video.addEventListener('canplaythrough', function () {
                console.log(`Відео готове: ${video.id}`);
            });

            video.addEventListener('error', function (e) {
                console.error(`Помилка відео ${video.id}:`, e);
            });
        },

        setupVideoForIOS: function (video) {
            video.removeAttribute('controls');
            video.controls = false;
            video.setAttribute('playsinline', 'true');
            video.setAttribute('webkit-playsinline', 'true');
            video.setAttribute('x-webkit-airplay', 'allow');
            video.muted = true;
            video.autoplay = false;
            video.classList.add('ios-optimized');

            video.addEventListener('loadedmetadata', function () {
                if (video.paused) {
                    video.play().catch(error => {
                        console.log(`iOS Safari: не вдалося запустити відео ${video.id}:`, error.message);
                    });
                }
            });
        },

        setupAllVideos: function () {
            const videos = document.querySelectorAll('video');
            console.log(`📹 Знайдено ${videos.length} відео елементів`);

            if (videos.length === 0) {
                console.warn('⚠️ Відео елементи не знайдені!');
                return;
            }

            videos.forEach((video, index) => {
                console.log(`🎬 Налаштування відео ${index + 1}:`, video.id || 'без ID');
                this.setupVideo(video);
            });
        },

        setupAllImages: function () {
            const images = document.querySelectorAll('img[data-mobile-src]');
            console.log(`🖼️ Знайдено ${images.length} зображень з мобільними версіями`);

            images.forEach((img, index) => {
                console.log(`🎨 Налаштування зображення ${index + 1}`);
                this.setImageSource(img);
            });
        },

        setupVideoObserver: function () {
            if (!('IntersectionObserver' in window)) return;

            const videoObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    const video = entry.target;

                    if (entry.isIntersecting) {
                        // Відео в зоні видимості
                        if (video.readyState < 2) {
                            video.load();
                        }

                        if (video.paused) {
                            video.play().catch(error => {
                                console.log(`Не вдалося запустити відео ${video.id}:`, error.message);
                            });
                        }
                    } else {
                        // Відео поза зоною видимості - економимо ресурси
                        if (!video.paused && !this.isIOS) {
                            // На iOS краще не ставити на паузу через особливості Safari
                            video.pause();
                        }
                    }
                });
            }, {
                threshold: 0.25,
                rootMargin: '50px 0px'
            });

            // Додаємо всі відео до спостереження
            document.querySelectorAll('video').forEach(video => {
                videoObserver.observe(video);
            });
        },

        forceMobileSwitch: function () {
            if (window.innerWidth <= 768) {
                console.log('🎯 Примусове переключення на мобільні медіа для вузького екрана');

                // Переключаємо відео
                const videos = document.querySelectorAll('video[data-mobile-src]');
                videos.forEach(video => {
                    const mobileSrc = video.getAttribute('data-mobile-src');
                    if (mobileSrc && video.src !== mobileSrc) {
                        console.log(`🔄 Примусово змінюю відео ${video.id} на мобільну версію: ${mobileSrc}`);
                        video.pause();
                        video.src = mobileSrc;
                        const source = video.querySelector('source');
                        if (source) source.src = mobileSrc;
                        video.load();
                    }
                });

                // Переключаємо зображення
                const images = document.querySelectorAll('img[data-mobile-src]');
                images.forEach(img => {
                    const mobileSrc = img.getAttribute('data-mobile-src');
                    if (mobileSrc && img.src !== mobileSrc) {
                        console.log(`🔄 Примусово змінюю зображення на мобільну версію: ${mobileSrc}`);
                        img.src = mobileSrc;
                    }
                });
            }
        },

        handleResize: function () {
            const wasMobile = this.isMobile;
            this.isMobile = this.isMobileDevice();

            if (wasMobile !== this.isMobile) {
                console.log('Статус пристрою змінився:', { was: wasMobile, now: this.isMobile });

                document.querySelectorAll('video').forEach(video => {
                    this.setVideoSource(video);
                });

                document.querySelectorAll('img[data-mobile-src]').forEach(img => {
                    this.setImageSource(img);
                });
            }
        },

        checkVideoStatus: function () {
            console.log('🔍 Перевірка стану відео через 1 секунду...');
            const videos = document.querySelectorAll('video');
            videos.forEach(video => {
                console.log(`📊 Відео ${video.id}:`, {
                    src: video.src,
                    readyState: video.readyState,
                    paused: video.paused
                });
            });
        },

        bindEvents: function () {
            // Обробка зміни розміру вікна
            window.addEventListener('resize', Utils.debounce(() => this.handleResize(), 250));
            window.addEventListener('orientationchange', () => {
                setTimeout(() => this.handleResize(), 100);
            });

            // Додатковий запуск через 500мс для надійності
            setTimeout(() => {
                this.forceMobileSwitch();
                this.isMobile = this.isMobileDevice();
                console.log('🔄 Повторна детекція:', { isMobile: this.isMobile, width: window.innerWidth });

                document.querySelectorAll('video').forEach(video => this.setVideoSource(video));
                document.querySelectorAll('img[data-mobile-src]').forEach(img => this.setImageSource(img));
            }, 500);
        }
    };

    // =================================
    // Hero Section
    // =================================
    const HeroSection = {
        init: function () {
            this.heroBtn = document.getElementById('hero-btn');
            this.bindEvents();
        },

        bindEvents: function () {
            if (this.heroBtn) {
                this.heroBtn.addEventListener('click', () => {
                    window.location.href = '/catalog/';
                });
            }
        }
    };

    // =================================
    // Capacity Section & Counter Animation (RESTORED ORIGINAL)
    // =================================
    const CapacitySection = {
        init: function () {
            this.capacityGlass = document.getElementById('capacity-glass');
            this.counters = document.querySelectorAll('.capacity-counter');
            this.isAnimated = false;
            this.setupObserver();
        },

        setupObserver: function () {
            if (!this.capacityGlass) return;

            const observer = Utils.createObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        // Показуємо glass container з анімацією
                        setTimeout(() => {
                            this.capacityGlass.classList.add('show');
                        }, 200);

                        // Запускаємо лічільники
                        if (!this.isAnimated) {
                            setTimeout(() => {
                                this.animateCounters();
                            }, 600);
                            this.isAnimated = true;
                        }
                    }
                });
            }, { threshold: 0.3 });

            observer.observe(this.capacityGlass);
        },

        animateCounters: function () {
            if (this.counters.length === 0) return;

            this.counters.forEach(counter => {
                const target = parseFloat(counter.getAttribute('data-target'));
                const duration = 2000;
                const step = target / (duration / 16);
                let current = 0;

                const updateCounter = () => {
                    current += step;
                    if (current >= target) {
                        counter.textContent = target % 1 === 0 ? target.toString() : target.toFixed(1);
                    } else {
                        counter.textContent = current % 1 === 0 ? Math.floor(current).toString() : current.toFixed(1);
                        requestAnimationFrame(updateCounter);
                    }
                };

                updateCounter();
            });
        }
    };

    // =================================
    // Shopping Cart System
    // =================================
    class ShoppingCart {
        constructor() {
            this.cart = this.loadCart();
            this.validateCartItems();
            this.initEventListeners();
            this.updateCartDisplay();

            if (this.cart.length > 0) {
                setTimeout(() => this.renderCartItems(), 100);
            }
        }

        loadCart() {
            const savedCart = localStorage.getItem('shoppingCart');
            return savedCart ? JSON.parse(savedCart) : [];
        }

        validateCartItems() {
            const validCart = this.cart.filter(item => {
                return item.id && item.name && item.price && !isNaN(item.price);
            });

            if (validCart.length !== this.cart.length) {
                this.cart = validCart;
                this.saveCart();
            }
        }

        clearCart() {
            this.cart = [];
            this.saveCart();
            this.updateCartDisplay();
            this.renderCartItems();
        }

        clearLocalStorage() {
            localStorage.removeItem('shoppingCart');
            this.cart = [];
            this.updateCartDisplay();
            this.renderCartItems();
            console.log('✅ localStorage очищено! Кошик пустий.');
            alert('✅ Кошик очищено! Спробуйте додати нові товари з каталогу.');
        }

        saveCart() {
            localStorage.setItem('shoppingCart', JSON.stringify(this.cart));
        }

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

        removeFromCart(productId) {
            this.cart = this.cart.filter(item => item.id !== productId);
            this.saveCart();
            this.updateCartDisplay();
            this.renderCartItems();
        }

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

        getTotalQuantity() {
            return this.cart.reduce((total, item) => total + item.quantity, 0);
        }

        getTotalPrice() {
            return this.cart.reduce((total, item) => total + (item.price * item.quantity), 0);
        }

        updateCartDisplay() {
            const cartCount = document.getElementById('cart-count');
            const cartTotal = document.getElementById('cart-total');

            if (cartCount) {
                const totalQuantity = this.getTotalQuantity();
                cartCount.textContent = totalQuantity;
                cartCount.style.display = totalQuantity > 0 ? 'block' : 'none';
            }

            if (cartTotal) {
                const totalPrice = this.getTotalPrice();
                cartTotal.textContent = `₴${totalPrice.toFixed(2)}`;
            }
        }

        renderCartItems() {
            const cartItemsContainer = document.getElementById('cart-items');
            if (!cartItemsContainer) return;

            if (this.cart.length === 0) {
                cartItemsContainer.innerHTML = `
                    <div class="cart-empty">
                        <p>Корзина порожня</p>
                        <p>Додайте товари з каталогу</p>
                        <button class="clear-cart-btn" onclick="window.cart.clearLocalStorage()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: #dc3545; color: white; border: none; border-radius: 6px; cursor: pointer;">
                            Очистити localStorage
                        </button>
                    </div>
                `;
                return;
            }

            const itemsHtml = this.cart.map(item => `
                <div class="cart-item" data-id="${item.id}">
                    <div class="cart-item__image">
                        ${item.image ? `<img src="${item.image}" alt="${item.name}" class="cart-item__img" onerror="console.log('Image failed to load:', this.src); this.style.display='none'; this.nextElementSibling.style.display='flex';" style="display: block;"><div class="cart-item__no-image" style="display: none;">Немає фото</div>` : '<div class="cart-item__no-image">Немає фото</div>'}
                    </div>
                    <div class="cart-item__details">
                        <h4 class="cart-item__name">${item.name}</h4>
                        <div class="cart-item__price">₴${item.price.toFixed(2)}</div>
                    </div>
                    <div class="cart-item__controls">
                        <div class="quantity-controls">
                            <button class="quantity-btn quantity-btn--minus" data-id="${item.id}">−</button>
                            <span class="quantity-display">${item.quantity}</span>
                            <button class="quantity-btn quantity-btn--plus" data-id="${item.id}">+</button>
                        </div>
                        <button class="cart-item__remove" data-id="${item.id}">×</button>
                    </div>
                                </div>
            `).join('');

            cartItemsContainer.innerHTML = itemsHtml;
        }

        showAddToCartNotification(productName) {
            // Simple notification
            const notification = document.createElement('div');
            notification.className = 'cart-notification';
            notification.textContent = `${productName} додано до корзини`;
            notification.style.cssText = `
                position: fixed;
                top: 100px;
                right: 20px;
                background: #4CAF50;
                color: white;
                padding: 1rem 2rem;
                border-radius: 8px;
                z-index: 10000;
                font-weight: 500;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                animation: slideInRight 0.3s ease;
            `;

            document.body.appendChild(notification);

            setTimeout(() => {
                notification.style.animation = 'slideOutRight 0.3s ease forwards';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }

        initEventListeners() {
            // Cart modal controls
            const cartBtn = document.getElementById('cart-btn');
            const cartModal = document.getElementById('cart-modal');
            const cartClose = document.getElementById('cart-close');
            const cartOverlay = document.getElementById('cart-overlay');

            if (cartBtn) {
                cartBtn.addEventListener('click', () => {
                    cartModal?.classList.add('active');
                    this.renderCartItems();
                });
            }

            if (cartClose) {
                cartClose.addEventListener('click', () => {
                    cartModal?.classList.remove('active');
                });
            }

            if (cartOverlay) {
                cartOverlay.addEventListener('click', () => {
                    cartModal?.classList.remove('active');
                });
            }

            // Add to cart buttons
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

                    // Check if all required data exists
                    if (!product.id || !product.name || !product.price) {
                        console.error('Missing product data:', product);
                        alert('Помилка: не вдалося додати товар до корзини');
                        return;
                    }

                    this.addToCart(product);
                }
            });

            // Cart item controls
            document.addEventListener('click', (e) => {
                if (e.target.classList.contains('quantity-btn--plus')) {
                    const productId = parseInt(e.target.getAttribute('data-id'));
                    const item = this.cart.find(item => item.id === productId);
                    if (item) {
                        this.updateQuantity(productId, item.quantity + 1);
                    }
                }

                if (e.target.classList.contains('quantity-btn--minus')) {
                    const productId = parseInt(e.target.getAttribute('data-id'));
                    const item = this.cart.find(item => item.id === productId);
                    if (item) {
                        this.updateQuantity(productId, item.quantity - 1);
                    }
                }

                if (e.target.classList.contains('cart-item__remove')) {
                    const productId = parseInt(e.target.getAttribute('data-id'));
                    this.removeFromCart(productId);
                }
            });

            // Checkout form
            const checkoutForm = document.getElementById('checkout-form');
            if (checkoutForm) {
                checkoutForm.addEventListener('submit', (e) => this.handleCheckout(e));
            }
        }

        async handleCheckout(e) {
            e.preventDefault();

            const formData = new FormData(e.target);
            const orderData = {
                name: formData.get('name'),
                phone: formData.get('phone'),
                email: formData.get('email'),
                comment: formData.get('comment'),
                items: this.cart,
                total: this.getTotalPrice()
            };

            try {
                const response = await fetch('/api/orders/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(orderData)
                });

                const result = await response.json();

                if (response.ok) {
                    // Clear cart and show success
                    this.cart = [];
                    this.saveCart();
                    this.updateCartDisplay();
                    alert('Замовлення успішно відправлено!');
                    document.getElementById('cart-modal').classList.remove('active');
                } else {
                    alert(result.error || 'Помилка при відправці замовлення');
                }
            } catch (error) {
                console.error('Checkout error:', error);
                alert('Помилка мережі. Спробуйте ще раз.');
            }
        }
    }

    // =================================
    // Callback System
    // =================================
    class CallbackSystem {
        constructor() {
            this.modal = null;
            this.init();
        }

        init() {
            this.createCallButton();
            this.createModal();
            this.bindEvents();
        }

        createCallButton() {
            const button = document.createElement('button');
            button.className = 'call-button';
            button.id = 'call-button';
            button.setAttribute('aria-label', 'Зателефонувати мені');
            document.body.appendChild(button);
        }

        createModal() {
            const modalHTML = `
                <div class="callback-modal" id="callback-modal">
                    <div class="callback-modal__content">
                        <button class="callback-modal__close" id="modal-close">&times;</button>
                        
                        <div class="callback-options-screen" id="options-screen">
                            <h2 class="callback-modal__title">Як з вами зв'язатися?</h2>
                            <div class="callback-options">
                                <div class="callback-option" data-action="contact">
                                    <span class="callback-option__icon">💬</span>
                                    <div class="callback-option__title">Написати нам</div>
                                    <div class="callback-option__description">Отримайте нашу контактну інформацію</div>
                                </div>
                                <div class="callback-option" data-action="callback">
                                    <span class="callback-option__icon">📞</span>
                                    <div class="callback-option__title">Залишити заявку</div>
                                    <div class="callback-option__description">Ми зателефонуємо вам протягом 15 хвилин</div>
                                </div>
                            </div>
                        </div>

                        <div class="contact-info-screen" id="contact-screen" style="display: none;">
                            <button class="callback-form__back" id="back-to-options">← Назад</button>
                            <h2 class="callback-modal__title">Наші контакти</h2>
                            <div class="contact-info">
                                <div class="contact-item">
                                    <span class="contact-icon">📞</span>
                                    <div class="contact-details">
                                        <strong>Телефони:</strong><br>
                                        <a href="tel:+380500344881">+38 (050) 034-48-81</a><br>
                                        <a href="tel:+380634952145">+38 (063) 495-21-45</a>
                                    </div>
                                </div>
                                <div class="contact-item">
                                    <span class="contact-icon">📧</span>
                                    <div class="contact-details">
                                        <strong>Email:</strong><br>
                                        <a href="mailto:info@greensolartech.com">info@greensolartech.com</a>
                                    </div>
                                </div>
                                <div class="contact-item">
                                    <span class="contact-icon">📍</span>
                                    <div class="contact-details">
                                        <strong>Адреса:</strong><br>
                                        Київська область, м. Київ, Україна
                                    </div>
                                </div>
                                <div class="contact-item">
                                    <span class="contact-icon">🕒</span>
                                    <div class="contact-details">
                                        <strong>Режим роботи:</strong><br>
                                        Пн-Пт: 09:00-18:00<br>
                                        Сб: 10:00-16:00
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="callback-form" id="callback-form">
                            <button class="callback-form__back" id="back-to-options-form">← Назад</button>
                            <h2 class="callback-modal__title">Залишити заявку</h2>
                            <form id="callback-form-element">
                                <div class="form-group">
                                    <label for="callback-name">Ваше ім'я *</label>
                                    <input type="text" id="callback-name" name="name" required>
                                </div>
                                <div class="form-group">
                                    <label for="callback-phone">Номер телефону *</label>
                                    <input type="tel" id="callback-phone" name="phone" required>
                                </div>
                                <div class="form-group">
                                    <label for="callback-message">Повідомлення (необов'язково)</label>
                                    <textarea id="callback-message" name="message" placeholder="Розкажіть про ваш проект або питання..."></textarea>
                                </div>
                                <button type="submit" class="callback-submit" id="callback-submit">Відправити заявку</button>
                            </form>
                        </div>

                        <div class="success-message" id="success-message">
                            <div class="success-message__icon">✅</div>
                            <h2 class="success-message__title">Заявку відправлено!</h2>
                            <p class="success-message__text">
                                Дякуємо за звернення! Наш менеджер зв'яжеться з вами протягом 15 хвилин.
                            </p>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHTML);
            this.modal = document.getElementById('callback-modal');
        }

        bindEvents() {
            document.getElementById('call-button').addEventListener('click', () => this.openModal());
            document.getElementById('modal-close').addEventListener('click', () => this.closeModal());

            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) this.closeModal();
            });

            document.querySelectorAll('.callback-option').forEach(option => {
                option.addEventListener('click', (e) => {
                    const action = e.currentTarget.dataset.action;
                    this.handleOptionSelect(action);
                });
            });

            document.getElementById('back-to-options').addEventListener('click', () => this.showOptionsScreen());
            document.getElementById('back-to-options-form').addEventListener('click', () => this.showOptionsScreen());

            document.getElementById('callback-form-element').addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        openModal() {
            this.modal.classList.add('active');
            this.showOptionsScreen();
        }

        closeModal() {
            this.modal.classList.remove('active');
        }

        showOptionsScreen() {
            document.getElementById('options-screen').style.display = 'block';
            document.getElementById('contact-screen').style.display = 'none';
            document.getElementById('callback-form').style.display = 'none';
            document.getElementById('success-message').style.display = 'none';
        }

        handleOptionSelect(action) {
            if (action === 'contact') {
                document.getElementById('options-screen').style.display = 'none';
                document.getElementById('contact-screen').style.display = 'block';
            } else if (action === 'callback') {
                document.getElementById('options-screen').style.display = 'none';
                document.getElementById('callback-form').style.display = 'block';
            }
        }

        async handleFormSubmit(e) {
            e.preventDefault();

            const formData = new FormData(e.target);
            const callbackData = {
                name: formData.get('name'),
                phone: formData.get('phone'),
                message: formData.get('message')
            };

            try {
                const response = await fetch('/api/callback/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(callbackData)
                });

                const result = await response.json();

                if (response.ok) {
                    document.getElementById('callback-form').style.display = 'none';
                    document.getElementById('success-message').style.display = 'block';
                    e.target.reset();
                } else {
                    alert(result.error || 'Помилка при відправці заявки');
                }
            } catch (error) {
                console.error('Callback error:', error);
                alert('Помилка мережі. Спробуйте ще раз.');
            }
        }
    }

    // =================================
    // Initialize All Systems
    // =================================
    function initializeApp() {
        Navigation.init();
        VideoSystem.init();
        HeroSection.init();
        CapacitySection.init();

        // Initialize cart and callback systems
        // Global cart instance - доступний всюди
        window.cart = new ShoppingCart();

        // Automatic cleanup on page load
        console.log('🔄 Запуск автоматичної валідації кошика...');
        window.cart.validateCartItems();
        window.callbackSystem = new CallbackSystem();

        console.log('GreenSolarTech Index Page - All systems initialized');
    }

    // Start the application
    initializeApp();

    // Debug commands for console
    console.log('%c🛒 КОШИК ГОТОВИЙ ДО РОБОТИ!', 'color: green; font-weight: bold; font-size: 16px;');
    console.log('%c📱 МІНІМАЛІСТИЧНЕ МЕНЮ ГОТОВЕ!', 'color: #e67e22; font-weight: bold; font-size: 16px;');
    console.log('%c📦 Команди для відлагодження:', 'color: blue; font-weight: bold;');
    console.log('window.cart.clearLocalStorage() - 🗑️ Очистити localStorage');
    console.log('window.cart.cart - 📋 Показати вміст кошика');
    console.log('JSON.parse(localStorage.getItem("shoppingCart")) - 💾 Показати сирі дані');
    console.log('window.cart.renderCartItems() - 🔄 Перерендерити кошик');

    // Діагностика мобільного меню
    setTimeout(() => {
        const menuButton = document.getElementById('nav-toggle');
        const menuList = document.querySelector('.nav__list');
        console.log('%c📱 Мобільне меню:', 'color: orange; font-weight: bold;', {
            button: !!menuButton,
            list: !!menuList,
            buttonStyles: menuButton ? window.getComputedStyle(menuButton).display : 'not found',
            listPosition: menuList ? window.getComputedStyle(menuList).left : 'not found'
        });
    }, 100);



    // Add CSS animations for notifications
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}); 