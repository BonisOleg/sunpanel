/* ===== ОПТИМІЗОВАНЕ МОБІЛЬНЕ МЕНЮ ДЛЯ iOS SAFARI ===== */

window.mobileMenu = {
    isOpen: false,
    scrollPosition: 0,
    isIOS: false,
    isSafari: false,

    init() {
        this.detectBrowser();
        this.setupViewport();
        this.bindEvents();
        this.handleActiveLink();
    },

    detectBrowser() {
        // Детекція iOS Safari
        this.isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        this.isSafari = /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent);
        
        if (this.isIOS && this.isSafari) {
            document.documentElement.classList.add('ios-safari');
        }
    },

    setupViewport() {
        // iOS Safari viewport fix
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };

        setVH();
        
        // Обробка зміни орієнтації
        window.addEventListener('resize', this.debounce(setVH, 100));
        window.addEventListener('orientationchange', () => {
            setTimeout(setVH, 100);
        });
    },

    bindEvents() {
        const navToggle = document.getElementById('nav-toggle');
        const navMenu = document.getElementById('nav-menu');

        if (!navToggle || !navMenu) return;

        // Основна подія кліку
        navToggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleMenu();
        });

        // Touch події для iOS
        if (this.isIOS) {
            navToggle.addEventListener('touchstart', (e) => {
                e.preventDefault();
            }, { passive: false });

            navToggle.addEventListener('touchend', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleMenu();
            }, { passive: false });
        }

        // Закриття меню при кліку поза ним
        navMenu.addEventListener('click', (e) => {
            if (e.target === navMenu) {
                this.closeMenu();
            }
        });

        // Закриття меню при кліку на посилання
        const navLinks = navMenu.querySelectorAll('.nav__link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                setTimeout(() => {
                    this.closeMenu();
                }, 150);
            });

            // Touch події для посилань на iOS
            if (this.isIOS) {
                link.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                }, { passive: false });
            }
        });

        // Закриття меню клавішею Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeMenu();
            }
        });

        // Обробка зміни орієнтації
        window.addEventListener('orientationchange', () => {
            if (this.isOpen) {
                setTimeout(() => {
                    this.updateMenuPosition();
                }, 100);
            }
        });

        // Обробка зміни розміру вікна
        window.addEventListener('resize', this.debounce(() => {
            if (this.isOpen) {
                this.updateMenuPosition();
            }
        }, 100));
    },

    toggleMenu() {
        if (this.isOpen) {
            this.closeMenu();
        } else {
            this.openMenu();
        }
    },

    openMenu() {
        const navMenu = document.getElementById('nav-menu');
        const navToggle = document.getElementById('nav-toggle');

        if (!navMenu || !navToggle) return;

        // Зберігаємо позицію скролу
        this.scrollPosition = window.pageYOffset;

        // Активуємо меню
        navMenu.classList.add('active');
        navToggle.classList.add('active');
        navToggle.setAttribute('aria-expanded', 'true');
        navToggle.setAttribute('aria-label', 'Закрити меню');

        // Блокуємо скролл
        this.lockScroll();

        // Оновлюємо позицію меню
        this.updateMenuPosition();

        // Фокус для доступності
        setTimeout(() => {
            const firstLink = navMenu.querySelector('.nav__link');
            if (firstLink) {
                firstLink.focus();
            }
        }, 300);

        this.isOpen = true;

        // iOS Safari специфічні дії
        if (this.isIOS) {
            this.handleIOSOpen();
        }
    },

    closeMenu() {
        const navMenu = document.getElementById('nav-menu');
        const navToggle = document.getElementById('nav-toggle');

        if (!navMenu || !navToggle) return;

        // Деактивуємо меню
        navMenu.classList.remove('active');
        navToggle.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.setAttribute('aria-label', 'Відкрити меню');

        // Розблокуємо скролл
        this.unlockScroll();

        // Відновлюємо позицію скролу
        if (this.scrollPosition !== undefined) {
            window.scrollTo(0, this.scrollPosition);
            this.scrollPosition = undefined;
        }

        this.isOpen = false;

        // iOS Safari специфічні дії
        if (this.isIOS) {
            this.handleIOSClose();
        }
    },

    lockScroll() {
        document.documentElement.classList.add('nav-open');
        document.body.classList.add('nav-open');
        
        // Додаткове блокування для iOS
        if (this.isIOS) {
            document.body.style.position = 'fixed';
            document.body.style.top = `-${this.scrollPosition}px`;
            document.body.style.width = '100%';
        }
    },

    unlockScroll() {
        document.documentElement.classList.remove('nav-open');
        document.body.classList.remove('nav-open');
        
        // Відновлення для iOS
        if (this.isIOS) {
            document.body.style.position = '';
            document.body.style.top = '';
            document.body.style.width = '';
        }
    },

    updateMenuPosition() {
        const navMenu = document.getElementById('nav-menu');
        if (!navMenu) return;

        // Оновлюємо висоту для iOS Safari
        if (this.isIOS) {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
            
            // Оновлюємо safe area insets
            const safeAreaTop = getComputedStyle(document.documentElement).getPropertyValue('--safe-area-top') || '0px';
            const safeAreaBottom = getComputedStyle(document.documentElement).getPropertyValue('--safe-area-bottom') || '0px';
            
            navMenu.style.paddingTop = safeAreaTop;
            navMenu.style.paddingBottom = safeAreaBottom;
        }
    },

    handleIOSOpen() {
        // iOS Safari специфічні дії при відкритті
        const navMenu = document.getElementById('nav-menu');
        if (navMenu) {
            // Примусове оновлення layout
            navMenu.offsetHeight;
            
            // Додаємо клас для iOS
            navMenu.classList.add('ios-active');
        }
    },

    handleIOSClose() {
        // iOS Safari специфічні дії при закритті
        const navMenu = document.getElementById('nav-menu');
        if (navMenu) {
            navMenu.classList.remove('ios-active');
        }
    },

    handleActiveLink() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav__link');

        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPath || (currentPath.includes(href) && href !== '/')) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    },

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
    }
};

// Ініціалізація при завантаженні DOM
document.addEventListener('DOMContentLoaded', () => {
    window.mobileMenu.init();
});

// Експорт для використання в інших модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.mobileMenu;
} 