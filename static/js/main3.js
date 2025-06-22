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

    // Glass Container Animations - Оновлено для всіх секцій (без production)
    window.GlassAnimations = {
        init: function () {
            this.glassContainers = document.querySelectorAll(
                '.capacity__glass-container, .about__glass-container, .advantages__glass-container, .contacts__glass-container'
            );
            this.setupScrollTriggers();
        },

        setupScrollTriggers: function () {
            const observer = AnimationUtils.createObserver((entries) => {
                entries.forEach(entry => {
                    const glassContainer = entry.target.querySelector(
                        '.capacity__glass-container, .about__glass-container, .advantages__glass-container, .contacts__glass-container'
                    );

                    if (glassContainer) {
                        if (entry.isIntersecting) {
                            setTimeout(() => {
                                glassContainer.classList.add('show');
                            }, 300);
                        } else {
                            glassContainer.classList.remove('show');
                        }
                    }
                });
            });

            if (observer) {
                // Спостерігаємо за секціями, а не за glass контейнерами (без production)
                const sections = document.querySelectorAll('.capacity, .about, .advantages, .contacts');
                sections.forEach(section => {
                    observer.observe(section);
                });
            }
        }
    };

    // Scroll Animations - Оновлено (без production)
    window.ScrollAnimations = {
        init: function () {
            this.animatedElements = document.querySelectorAll(
                '.advantage-card, .capacity__stat-card, .advantages__stat-card, .advantages__type-card, .contacts__certificate-card, .contacts__phone-card, .contacts__address-card, .contacts__messengers-card'
            );
            this.setupIntersectionObserver();
        },

        setupIntersectionObserver: function () {
            const observer = AnimationUtils.createObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate');

                        // Анімація лічильників для різних типів карток
                        if (entry.target.classList.contains('capacity__stat-card') ||
                            entry.target.classList.contains('advantages__stat-card')) {
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
            const numberEl = card.querySelector('.stat-card__number, .capacity-counter');
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

    // Performance Optimizations - Оновлено (без production)
    window.Performance = {
        init: function () {
            // Додаємо will-change для елементів з анімаціями
            const animatedElements = document.querySelectorAll(
                '.advantage-card, .capacity__stat-card, .advantages__stat-card, .advantages__type-card, .contacts__certificate-card, .capacity__glass-container, .about__glass-container, .advantages__glass-container, .contacts__glass-container'
            );

            animatedElements.forEach(el => {
                el.style.willChange = 'transform, opacity';
            });

            // Перевіряємо prefers-reduced-motion
            if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                document.documentElement.style.setProperty('--transition-normal', '0.01ms');
                document.documentElement.style.setProperty('--transition-fast', '0.01ms');
                document.documentElement.style.setProperty('--transition-slow', '0.01ms');
            }
        }
    };

    // Lightbox Modal
    window.LightboxModal = {
        init: function () {
            this.lightbox = document.getElementById('lightbox');
            if (!this.lightbox) return;

            this.lightboxImage = document.getElementById('lightbox-image');

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

    // Ініціалізація модулів - Оновлено
    window.GlassAnimations.init();
    window.ScrollAnimations.init();
    window.MagneticButtons.init();
    window.Performance.init();
    window.LightboxModal.init();

    // Production Video Background
    const ProductionVideo = {
        init() {
            const video = document.getElementById('production-video');
            if (!video) return;

            let options = {
                root: null,
                rootMargin: '0px',
                threshold: 0.1
            };

            let observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        if (video.paused) {
                            video.play().catch(() => {
                                console.log('Video autoplay failed');
                            });
                        }
                    } else {
                        if (!video.paused) {
                            video.pause();
                        }
                    }
                });
            }, options);

            observer.observe(video);
        }
    };

    // Initialize production video
    ProductionVideo.init();

    // Advantages section glass container animation
    const advantagesGlassContainer = document.getElementById('advantages-glass');

    if (advantagesGlassContainer) {
        const advantagesObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate');
                }
            });
        }, {
            threshold: 0.2,
            rootMargin: '0px 0px -50px 0px'
        });

        advantagesObserver.observe(advantagesGlassContainer);
    }

    // Production section glass container animation
    const productionGlassContainer = document.getElementById('production-glass');

    if (productionGlassContainer) {
        const productionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('show');
                }
            });
        }, {
            threshold: 0.2,
            rootMargin: '0px 0px -50px 0px'
        });

        productionObserver.observe(productionGlassContainer);
    }

    // Contacts section glass container animation
    const contactsGlassContainer = document.getElementById('contacts-glass');

    if (contactsGlassContainer) {
        const contactsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate');
                }
            });
        }, {
            threshold: 0.2,
            rootMargin: '0px 0px -50px 0px'
        });

        contactsObserver.observe(contactsGlassContainer);
    }
}); 