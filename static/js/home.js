/* ===== ГОЛОВНА СТОРІНКА JAVASCRIPT ===== */

// Модуль головної сторінки
window.app.home = {
    init() {
        this.bindEvents();
        this.initAnimations();
        this.initVideoOptimization();
        this.initContactForm();
    },

    bindEvents() {
        // Плавна прокрутка для внутрішніх посилань
        document.addEventListener('click', (e) => {
            if (e.target.matches('a[href^="#"]')) {
                e.preventDefault();
                const targetId = e.target.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);

                if (targetElement) {
                    window.app.utils.scrollTo(targetElement, 80);
                }
            }
        });

        // Обробка прокрутки для анімацій (БЕЗ паралаксу для відео)
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.animateCounters();
                    ticking = false;
                });
                ticking = true;
            }
        });
    },

    initAnimations() {
        // Intersection Observer для анімацій з'явлення
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Додавання спостереження для елементів з анімацією
        const animatedElements = document.querySelectorAll('.fade-in, .slide-up');
        animatedElements.forEach(el => {
            observer.observe(el);
        });
    },

    animateCounters() {
        const stats = document.querySelectorAll('.stat__number');

        stats.forEach(stat => {
            if (this.isElementInViewport(stat) && !stat.classList.contains('animated')) {
                stat.classList.add('animated');
                this.animateCounter(stat);
            }
        });
    },

    animateCounter(element) {
        const text = element.textContent;
        const number = parseInt(text.replace(/\D/g, ''));
        const suffix = text.replace(/\d/g, '');

        if (isNaN(number)) return;

        let current = 0;
        const increment = number / 50;
        const duration = 2000;
        const stepTime = duration / 50;

        const timer = setInterval(() => {
            current += increment;
            if (current >= number) {
                current = number;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current) + suffix;
        }, stepTime);
    },

    isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    },

    initVideoOptimization() {
        // Налаштування мобільних/десктопних версій відео
        this.setupVideoSources();

        // Запуск відео при появі на екрані
        this.initVideoPlayback();
    },

    setupVideoSources() {
        const videos = document.querySelectorAll('video[data-mobile-src][data-desktop-src]');

        videos.forEach(video => {
            // КРИТИЧНО: відразу забороняємо loop до будь-якого запуску
            video.loop = false;
            video.removeAttribute('loop');

            const isMobile = window.app.utils.isMobile();
            const mobileSource = video.getAttribute('data-mobile-src');
            const desktopSource = video.getAttribute('data-desktop-src');

            // Встановлюємо правильний source
            const source = video.querySelector('source');
            if (source) {
                if (isMobile && mobileSource) {
                    source.src = mobileSource;
                    video.src = mobileSource;
                } else if (desktopSource) {
                    source.src = desktopSource;
                    video.src = desktopSource;
                }
            }

            // Обробник завантаження відео - ще раз забороняємо loop
            video.addEventListener('loadeddata', () => {
                video.loop = false;
            });

            // Обробник коли відео готове до відтворення
            video.addEventListener('canplay', () => {
                video.loop = false;
            });

            // ГОЛОВНЕ: зупинка на останньому кадрі
            video.addEventListener('ended', () => {
                video.pause();
                video.currentTime = video.duration;
            });

            // Додатковий контроль: зупинка коли відео майже закінчилось
            video.addEventListener('timeupdate', () => {
                if (video.currentTime >= video.duration - 0.1) {
                    video.pause();
                    video.currentTime = video.duration;
                }
            });

            // iOS оптимізація
            if (window.app.utils.isMobile()) {
                video.setAttribute('webkit-playsinline', 'true');
                video.setAttribute('playsinline', 'true');
            }
        });
    },

    initVideoPlayback() {
        const videos = document.querySelectorAll('video');

        // Простий IntersectionObserver для запуску відео
        const videoObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const video = entry.target;

                if (entry.isIntersecting) {
                    // Відео з'явилося - запускаємо негайно
                    this.playVideo(video);
                }
            });
        }, {
            threshold: 0.1
        });

        videos.forEach(video => {
            videoObserver.observe(video);

            // Також запускаємо відео коли воно готове
            video.addEventListener('canplay', () => {
                if (this.isElementInViewport(video)) {
                    this.playVideo(video);
                }
            });

            // Запуск відео одразу якщо воно вже готове
            if (video.readyState >= 2 && this.isElementInViewport(video)) {
                this.playVideo(video);
            }
        });
    },

    playVideo(video) {
        if (video.paused) {
            video.play().catch(e => {
                console.warn('Автозапуск відео заблоковано:', e);
                // Fallback для iOS
                this.setupUserInteractionFallback(video);
            });
        }
    },

    setupUserInteractionFallback(video) {
        const playOnInteraction = () => {
            video.play().catch(e => console.warn('Не вдається запустити відео:', e));
            document.removeEventListener('touchstart', playOnInteraction);
            document.removeEventListener('click', playOnInteraction);
        };

        document.addEventListener('touchstart', playOnInteraction, { once: true });
        document.addEventListener('click', playOnInteraction, { once: true });
    },

    initContactForm() {
        const contactForm = document.querySelector('.contact-form');
        if (contactForm) {
            contactForm.addEventListener('submit', (e) => {
                this.handleContactForm(e);
            });
        }
    },

    async handleContactForm(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');

        // Показування стану завантаження
        const originalBtnText = submitBtn.textContent;
        submitBtn.textContent = 'Відправляємо...';
        submitBtn.disabled = true;

        try {
            const response = await fetch(window.location.pathname, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': window.app.utils.getCSRFToken()
                }
            });

            if (response.ok) {
                this.showContactSuccess();
                form.reset();
            } else {
                throw new Error('Помилка відправки');
            }
        } catch (error) {
            console.error('Помилка:', error);
            this.showContactError();
        } finally {
            submitBtn.textContent = originalBtnText;
            submitBtn.disabled = false;
        }
    },

    showContactSuccess() {
        // Використання системи сповіщень з base.js
        if (window.app.cart && window.app.cart.showNotification) {
            window.app.cart.showNotification('Дякуємо! Ваша заявка відправлена. Ми зв\'яжемося з вами найближчим часом.', 'success');
        } else {
            alert('Дякуємо! Ваша заявка відправлена.');
        }
    },

    showContactError() {
        if (window.app.cart && window.app.cart.showNotification) {
            window.app.cart.showNotification('Помилка відправки заявки. Спробуйте пізніше або зателефонуйте нам.', 'error');
        } else {
            alert('Помилка відправки заявки. Спробуйте пізніше.');
        }
    }
};

// Додаткові утиліти для головної сторінки
window.app.homeUtils = {
    // Перевірка підтримки відео
    supportsVideoFormat(format) {
        const video = document.createElement('video');
        return video.canPlayType(`video/${format}`) !== '';
    },

    // Оптимізація завантаження зображень
    lazyLoadImages() {
        const images = document.querySelectorAll('img[data-src]');

        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    },

    // Детекція тематики користувача (темна/світла)
    detectColorScheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
        }
    }
};

// Ініціалізація при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    window.app.home.init();
    window.app.homeUtils.lazyLoadImages();
    window.app.homeUtils.detectColorScheme();
});

// Експорт для використання в інших модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        home: window.app.home,
        homeUtils: window.app.homeUtils
    };
} 