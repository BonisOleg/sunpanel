// Оптимізований JavaScript для анімацій та інтерактивності

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // Утиліти для анімацій
    const AnimationUtils = {
        observerOptions: {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        },

        createObserver: function (callback) {
            if (typeof IntersectionObserver === 'undefined') return null;
            return new IntersectionObserver(callback, this.observerOptions);
        },

        animateCounter: function (element, target, duration = 2000) {
            const increment = target / (duration / 16);
            let current = 0;

            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                element.textContent = Math.floor(current).toLocaleString();
            }, 16);
        }
    };

    // Scroll Animations - Оптимізовано
    window.ScrollAnimations = {
        init: function () {
            this.animatedElements = document.querySelectorAll('.timeline-item, .advantage-card, .capacity__stat-card');
            this.setupIntersectionObserver();
        },

        setupIntersectionObserver: function () {
            const observer = AnimationUtils.createObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate');

                        // Анімація лічильників
                        if (entry.target.classList.contains('capacity__stat-card')) {
                            this.animateStatCard(entry.target);
                        }
                    }
                });
            });

            if (observer) {
                this.animatedElements.forEach(el => {
                    observer.observe(el);
                });
            }
        },

        animateStatCard: function (card) {
            const numberEl = card.querySelector('.stat-card__number');
            if (!numberEl) return;

            const target = parseInt(numberEl.getAttribute('data-target')) ||
                parseInt(numberEl.textContent.replace(/\D/g, ''));

            if (target && target > 0) {
                AnimationUtils.animateCounter(numberEl, target);
            }
        }
    };

    // Magnetic Buttons - Спрощено
    window.MagneticButtons = {
        init: function () {
            if (window.AppGlobals && window.AppGlobals.isMobile) return;

            this.buttons = document.querySelectorAll('.btn-magnetic');
            this.bindEvents();
        },

        bindEvents: function () {
            this.buttons.forEach(button => {
                button.addEventListener('mouseenter', () => {
                    button.style.transition = 'transform 0.1s ease';
                });

                button.addEventListener('mouseleave', () => {
                    button.style.transition = 'transform 0.3s ease';
                    button.style.transform = 'translate(0, 0)';
                });

                button.addEventListener('mousemove', (e) => {
                    const rect = button.getBoundingClientRect();
                    const x = (e.clientX - rect.left - rect.width / 2) * 0.3;
                    const y = (e.clientY - rect.top - rect.height / 2) * 0.3;
                    button.style.transform = `translate(${x}px, ${y}px)`;
                });
            });
        }
    };

    // Performance Optimizations - Спрощено
    window.Performance = {
        init: function () {
            this.optimizeAnimations();
            this.prefersReducedMotion();
        },

        optimizeAnimations: function () {
            // Додаємо will-change для елементів з анімаціями
            const animatedElements = document.querySelectorAll(
                '.advantage-card, .timeline-item, .capacity__stat-card, .capacity__glass-container'
            );

            animatedElements.forEach(el => {
                el.style.willChange = 'transform, opacity';
            });
        },

        prefersReducedMotion: function () {
            if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                const style = document.createElement('style');
                style.textContent = `
                    *, *::before, *::after {
                        animation-duration: 0.01ms !important;
                        transition-duration: 0.01ms !important;
                    }
                `;
                document.head.appendChild(style);
            }
        }
    };

    // Lightbox Modal - Спрощено
    window.LightboxModal = {
        init: function () {
            this.lightbox = document.getElementById('lightbox');
            if (!this.lightbox) return;

            this.lightboxImage = document.getElementById('lightbox-image');
            this.bindEvents();
        },

        bindEvents: function () {
            // Закриття
            this.lightbox.addEventListener('click', (e) => {
                if (e.target === this.lightbox || e.target.classList.contains('lightbox__close')) {
                    this.close();
                }
            });

            // ESC
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.lightbox.classList.contains('active')) {
                    this.close();
                }
            });

            // Відкриття зображень
            document.addEventListener('click', (e) => {
                if (e.target.matches('.capacity__photo img, .certificate-slide img')) {
                    this.open(e.target.src, e.target.alt);
                }
            });
        },

        open: function (src, alt) {
            if (this.lightboxImage) {
                this.lightboxImage.src = src;
                this.lightboxImage.alt = alt || '';
            }
            this.lightbox.classList.add('active');
            document.body.style.overflow = 'hidden';
        },

        close: function () {
            this.lightbox.classList.remove('active');
            document.body.style.overflow = '';
        }
    };

    // Responsive Table - Спрощено
    window.ResponsiveTable = {
        init: function () {
            const tables = document.querySelectorAll('.fuel-table');
            tables.forEach(table => {
                const wrapper = table.closest('.comparison__table-wrapper');
                if (wrapper && window.AppGlobals && window.AppGlobals.isMobile) {
                    wrapper.style.overflowX = 'auto';
                    wrapper.style.webkitOverflowScrolling = 'touch';
                }
            });
        }
    };

    // Ініціалізація модулів
    const modules = [
        window.ScrollAnimations,
        window.MagneticButtons,
        window.Performance,
        window.LightboxModal,
        window.ResponsiveTable
    ];

    modules.forEach(module => {
        if (module && module.init) {
            module.init();
        }
    });
}); 