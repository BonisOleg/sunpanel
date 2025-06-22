// Arkuda Pellet Landing Page JavaScript - Частина 1
// Утиліти та навігація

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // Глобальні змінні
    window.AppGlobals = {
        isMobile: window.innerWidth <= 768,
        isTablet: window.innerWidth <= 1024 && window.innerWidth > 768,
        isIOS: /iPad|iPhone|iPod/.test(navigator.userAgent)
    };

    // Утиліти
    window.AppUtils = {
        // Throttle функція для оптимізації scroll подій
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

        // Debounce функція для resize подій
        debounce: function (func, wait, immediate) {
            let timeout;
            return function () {
                const context = this;
                const args = arguments;
                const later = function () {
                    timeout = null;
                    if (!immediate) func.apply(context, args);
                };
                const callNow = immediate && !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
                if (callNow) func.apply(context, args);
            };
        },



        // Smooth scroll до елемента
        scrollTo: function (element, duration = 1000) {
            const targetPosition = element.offsetTop - 80; // 80px для навігації
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
        }
    };

    // Навігація
    window.Navigation = {
        init: function () {
            this.nav = document.getElementById('nav');
            this.navToggle = document.getElementById('nav-toggle');
            this.navMenu = document.getElementById('nav-menu');
            this.navLinks = document.querySelectorAll('.nav__link');

            this.bindEvents();
            this.handleScroll();
        },

        bindEvents: function () {
            // Toggle мобільного меню
            if (this.navToggle) {
                this.navToggle.addEventListener('click', () => {
                    this.toggleMobileMenu();
                });
            }

            // Клік по nav links
            this.navLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const targetId = link.getAttribute('href');
                    const targetElement = document.querySelector(targetId);

                    if (targetElement) {
                        window.AppUtils.scrollTo(targetElement);
                        this.closeMobileMenu();
                    }
                });
            });

            // Scroll event для зміни стилю навігації
            window.addEventListener('scroll', window.AppUtils.throttle(() => {
                this.handleScroll();
            }, 16));

            // Закриття меню при кліку поза ним
            document.addEventListener('click', (e) => {
                if (this.nav && !this.nav.contains(e.target)) {
                    this.closeMobileMenu();
                }
            });
        },

        toggleMobileMenu: function () {
            if (this.navMenu) {
                this.navMenu.classList.toggle('active');
            }
            if (this.navToggle) {
                this.navToggle.classList.toggle('active');
            }

            // Блокуємо scroll коли меню відкрите
            if (this.navMenu && this.navMenu.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        },

        closeMobileMenu: function () {
            if (this.navMenu) {
                this.navMenu.classList.remove('active');
            }
            if (this.navToggle) {
                this.navToggle.classList.remove('active');
            }
            document.body.style.overflow = '';
        },

        handleScroll: function () {
            if (!this.nav) return;

            const scrolled = window.pageYOffset > 50;

            if (scrolled) {
                this.nav.style.background = 'rgba(255, 255, 255, 0.98)';
                this.nav.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
            } else {
                this.nav.style.background = 'rgba(255, 255, 255, 0.95)';
                this.nav.style.boxShadow = 'none';
            }
        }
    };

    // Ініціалізація навігації
    window.Navigation.init();
}); 