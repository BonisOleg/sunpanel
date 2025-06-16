// Arkuda Pellet Landing Page JavaScript - Частина 3
// Scroll Animations, Magnetic Buttons та інші модулі

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // Scroll Animations
    window.ScrollAnimations = {
        init: function () {
            this.animatedElements = document.querySelectorAll('.timeline-item__content, .advantage-card, .type-card, .stat-card');
            this.timeline = document.getElementById('timeline-line');

            this.setupIntersectionObserver();
            this.animateOnScroll();
        },

        setupIntersectionObserver: function () {
            if (typeof IntersectionObserver === 'undefined') return;

            const options = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };

            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate');

                        // Спеціальна анімація для статистики
                        if (entry.target.classList.contains('stat-card')) {
                            this.animateCounter(entry.target);
                        }
                    }
                });
            }, options);

            this.animatedElements.forEach(el => {
                this.observer.observe(el);
            });
        },

        animateCounter: function (card) {
            const numberEl = card.querySelector('.stat-card__number');
            if (!numberEl) return;

            const target = parseInt(numberEl.getAttribute('data-target'));
            if (isNaN(target)) return;

            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;

            const timer = setInterval(() => {
                current += step;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                numberEl.textContent = Math.floor(current);
            }, 16);
        },

        animateOnScroll: function () {
            window.addEventListener('scroll', window.AppUtils.throttle(() => {
                this.updateTimelineProgress();
            }, 16));
        },

        updateTimelineProgress: function () {
            if (!this.timeline) return;

            const timelineSection = this.timeline.closest('.production');
            if (!timelineSection) return;

            const rect = timelineSection.getBoundingClientRect();
            const windowHeight = window.innerHeight;

            let progress = 0;
            if (rect.top <= windowHeight && rect.bottom >= 0) {
                progress = (windowHeight - rect.top) / (windowHeight + rect.height);
                progress = Math.max(0, Math.min(1, progress));
            }

            // Анімація лінії таймлайну
            this.timeline.style.background = `linear-gradient(to bottom, 
                var(--primary-color) 0%, 
                var(--primary-color) ${progress * 100}%, 
                var(--bg-light) ${progress * 100}%, 
                var(--bg-light) 100%)`;
        }
    };

    // Magnetic Buttons
    window.MagneticButtons = {
        init: function () {
            if (window.AppGlobals.isMobile) return; // Вимикаємо на мобільних

            this.buttons = document.querySelectorAll('.btn-magnetic');
            this.bindEvents();
        },

        bindEvents: function () {
            this.buttons.forEach(button => {
                button.addEventListener('mouseenter', (e) => {
                    this.addMagneticEffect(e.target);
                });

                button.addEventListener('mouseleave', (e) => {
                    this.removeMagneticEffect(e.target);
                });

                button.addEventListener('mousemove', (e) => {
                    this.updateMagneticEffect(e, e.target);
                });
            });
        },

        addMagneticEffect: function (button) {
            button.style.transition = 'transform 0.1s ease';
        },

        removeMagneticEffect: function (button) {
            button.style.transition = 'transform 0.3s ease';
            button.style.transform = 'translate(0, 0)';
        },

        updateMagneticEffect: function (e, button) {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            const strength = 0.3;
            const moveX = x * strength;
            const moveY = y * strength;

            button.style.transform = `translate(${moveX}px, ${moveY}px)`;
        }
    };

    // Responsive Table
    window.ResponsiveTable = {
        init: function () {
            this.tables = document.querySelectorAll('.fuel-table');
            this.setupMobileScroll();
        },

        setupMobileScroll: function () {
            this.tables.forEach(table => {
                const wrapper = table.closest('.comparison__table-wrapper');
                if (wrapper && window.AppGlobals.isMobile) {
                    wrapper.style.overflowX = 'auto';
                    wrapper.style.webkitOverflowScrolling = 'touch';

                    // Показуємо hint для скролу на мобільних
                    this.addScrollHint(wrapper);
                }
            });
        },

        addScrollHint: function (wrapper) {
            const hint = document.createElement('div');
            hint.className = 'table-scroll-hint';
            hint.textContent = '← Прокрутіть для перегляду →';
            hint.style.cssText = `
                text-align: center;
                font-size: 0.8rem;
                color: #666;
                padding: 0.5rem;
                background: rgba(244, 185, 66, 0.1);
                border-radius: 4px;
                margin-bottom: 1rem;
            `;

            wrapper.parentNode.insertBefore(hint, wrapper);

            // Видаляємо hint після першого скролу
            wrapper.addEventListener('scroll', () => {
                hint.style.display = 'none';
            }, { once: true });
        }
    };

    // Performance Optimizations
    window.Performance = {
        init: function () {
            this.lazyLoadImages();
            this.optimizeAnimations();
        },

        lazyLoadImages: function () {
            const images = document.querySelectorAll('img[loading="lazy"]');

            if ('IntersectionObserver' in window) {
                const imageObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const img = entry.target;
                            if (img.dataset.src) {
                                img.src = img.dataset.src;
                            }
                            img.classList.remove('lazy');
                            imageObserver.unobserve(img);
                        }
                    });
                });

                images.forEach(img => imageObserver.observe(img));
            }
        },

        optimizeAnimations: function () {
            // Вимикаємо анімації для користувачів з prefers-reduced-motion
            if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                const style = document.createElement('style');
                style.textContent = `
                    *, *::before, *::after {
                        animation-duration: 0.01ms !important;
                        animation-iteration-count: 1 !important;
                        transition-duration: 0.01ms !important;
                        scroll-behavior: auto !important;
                    }
                `;
                document.head.appendChild(style);
            }
        }
    };

    // Error Handler
    window.ErrorHandler = {
        init: function () {
            this.handleVideoErrors();
        },

        handleVideoErrors: function () {
            const videos = document.querySelectorAll('video');
            videos.forEach(video => {
                // Додаємо логування для діагностики
                video.addEventListener('loadstart', () => {
                    console.log('Video loadstart:', video.id);
                });

                video.addEventListener('canplay', () => {
                    console.log('Video canplay:', video.id);
                });

                video.addEventListener('play', () => {
                    console.log('Video started playing:', video.id);
                });

                video.addEventListener('pause', () => {
                    console.log('Video paused:', video.id);
                });

                video.addEventListener('ended', () => {
                    console.log('Video ended:', video.id);
                });

                video.addEventListener('error', (e) => {
                    console.warn('Video error:', video.id, e);
                    // Не приховуємо відео при помилці, тільки логуємо
                });
            });
        }
    };

    // Lightbox Modal
    window.LightboxModal = {
        init: function () {
            this.lightbox = document.getElementById('lightbox');
            this.lightboxImage = document.getElementById('lightbox-image');
            this.lightboxClose = document.getElementById('lightbox-close');
            this.lightboxOverlay = this.lightbox ? this.lightbox.querySelector('.lightbox__overlay') : null;

            this.bindEvents();
        },

        bindEvents: function () {
            // Закриття модального вікна
            if (this.lightboxClose) {
                this.lightboxClose.addEventListener('click', () => {
                    this.close();
                });
            }

            if (this.lightboxOverlay) {
                this.lightboxOverlay.addEventListener('click', () => {
                    this.close();
                });
            }

            // ESC для закриття
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.close();
                }
            });

            // Клік по зображенням для відкриття lightbox
            document.querySelectorAll('.certificate-slide img, .capacity__photo img').forEach(img => {
                img.addEventListener('click', (e) => {
                    this.open(e.target.src, e.target.alt);
                });
            });
        },

        open: function (src, alt) {
            if (!this.lightbox) return;

            this.lightboxImage.src = src;
            this.lightboxImage.alt = alt;
            this.lightbox.classList.add('active');
            document.body.style.overflow = 'hidden';
        },

        close: function () {
            if (!this.lightbox) return;

            this.lightbox.classList.remove('active');
            document.body.style.overflow = '';
        }
    };

    // Counter Animation for Capacity Section
    window.CapacityCounter = {
        init: function () {
            this.counters = document.querySelectorAll('.capacity-counter');
            this.animated = false;
            this.bindEvents();
        },

        bindEvents: function () {
            // Intersection Observer для запуску анімації при скролі
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !this.animated) {
                        this.startCounting();
                        this.animated = true;
                    }
                });
            }, { threshold: 0.5 });

            // Спостерігаємо за секцією capacity
            const capacitySection = document.querySelector('.capacity');
            if (capacitySection) {
                observer.observe(capacitySection);
            }
        },

        startCounting: function () {
            this.counters.forEach(counter => {
                const target = parseInt(counter.getAttribute('data-target'));
                const duration = 2000; // 2 секунди
                const increment = target / (duration / 16); // 60fps
                let current = 0;

                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        counter.textContent = target.toLocaleString();
                        clearInterval(timer);
                    } else {
                        counter.textContent = Math.floor(current).toLocaleString();
                    }
                }, 16);
            });
        }
    };

    // Ініціалізація модулів третьої частини
    window.ScrollAnimations.init();
    window.MagneticButtons.init();
    window.ResponsiveTable.init();
    window.Performance.init();
    window.ErrorHandler.init();
    window.LightboxModal.init();
    window.CapacityCounter.init();

    console.log('Arkuda Pellet Landing: Part 3 modules initialized');
}); 