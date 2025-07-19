/**
 * GreenSolarTech - Optimized JavaScript Bundle
 * Combined and optimized from main1.js, main2.js, main3.js
 * No duplicates, better performance, cleaner code
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
        // Throttle для оптимізації performance-critical подій
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

        // Debounce для events що не потребують миттєвого виконання
        debounce: function (func, wait) {
            let timeout;
            return function () {
                const context = this;
                const args = arguments;
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(context, args), wait);
            };
        },

        // Smooth scroll з врахуванням різних секцій
        scrollTo: function (element, duration = 1000) {
            if (!element) return;

            let targetPosition;
            if (element.id === 'hero') {
                targetPosition = 0;
            } else {
                const rect = element.getBoundingClientRect();
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                targetPosition = rect.top + scrollTop - 80; // 80px для навігації
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

        // Оптимізований intersection observer
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
            this.nav = document.getElementById('nav');
            this.navToggle = document.getElementById('nav-toggle');
            this.navMenu = document.getElementById('nav-menu');
            this.navLinks = document.querySelectorAll('.nav__link');

            if (!this.nav) return;

            this.bindEvents();
            this.handleScroll();
        },

        bindEvents: function () {
            // Mobile menu toggle
            if (this.navToggle) {
                this.navToggle.addEventListener('click', () => this.toggleMobileMenu());
            }

            // Navigation links
            this.navLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    const href = link.getAttribute('href');

                    if (href.startsWith('#')) {
                        e.preventDefault();
                        const targetElement = document.querySelector(href);
                        if (targetElement) {
                            Utils.scrollTo(targetElement);
                            this.closeMobileMenu();
                        }
                    } else if (href.includes('#') && window.location.pathname === href.split('#')[0]) {
                        e.preventDefault();
                        const anchor = '#' + href.split('#')[1];
                        const targetElement = document.querySelector(anchor);
                        if (targetElement) {
                            Utils.scrollTo(targetElement);
                            this.closeMobileMenu();
                        }
                    } else {
                        this.closeMobileMenu();
                    }
                });
            });

            // Scroll handling з throttle
            window.addEventListener('scroll', Utils.throttle(() => {
                this.handleScroll();
            }, 16));

            // Закриття меню при кліку поза ним
            document.addEventListener('click', (e) => {
                if (this.nav && !this.nav.contains(e.target)) {
                    this.closeMobileMenu();
                }
            });

            // Escape key для закриття меню
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeMobileMenu();
                }
            });
        },

        toggleMobileMenu: function () {
            if (!this.navMenu || !this.navToggle) return;

            const isActive = this.navMenu.classList.toggle('active');
            this.navToggle.classList.toggle('active', isActive);
            document.body.style.overflow = isActive ? 'hidden' : '';
        },

        closeMobileMenu: function () {
            if (this.navMenu) this.navMenu.classList.remove('active');
            if (this.navToggle) this.navToggle.classList.remove('active');
            document.body.style.overflow = '';
        },

        handleScroll: function () {
            if (!this.nav) return;

            const scrolled = window.pageYOffset > 50;
            this.nav.style.background = scrolled
                ? 'rgba(255, 255, 255, 0.98)'
                : 'rgba(255, 255, 255, 0.95)';
            this.nav.style.boxShadow = scrolled
                ? '0 2px 20px rgba(0, 0, 0, 0.1)'
                : 'none';
        }
    };

    // =================================
    // Video System - Optimized
    // =================================
    const VideoSystem = {
        playedVideos: new Set(),
        observers: new Map(),

        init: function () {
            // Ініціалізуємо тільки наявні відео
            const videos = [
                { id: 'hero-video', options: {} },
                { id: 'capacity-video', options: { showGlass: true } },
                { id: 'production-video', options: {} }
            ];

            videos.forEach(({ id, options }) => {
                const video = document.getElementById(id);
                if (video) {
                    this.initVideo(id, options);
                }
            });
        },

        initVideo: function (videoId, options = {}) {
            const video = document.getElementById(videoId);
            if (!video) return;

            // iOS сумісність
            video.setAttribute('playsinline', '');
            video.setAttribute('webkit-playsinline', '');
            video.muted = true;
            video.playbackRate = 1.0;

            // Обробка закінчення відео
            video.addEventListener('ended', () => {
                console.log(`${videoId} закінчено - залишається на останньому кадрі`);
                this.playedVideos.add(videoId);
            });

            // Обробка завантаження метаданих
            video.addEventListener('loadedmetadata', () => {
                if (this.playedVideos.has(videoId)) {
                    video.currentTime = video.duration;
                }
            });

            // Intersection Observer для відео
            const observer = Utils.createObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        if (!this.playedVideos.has(videoId)) {
                            this.playVideo(videoId, options);
                        } else {
                            this.handleGlassEffect(videoId, options);
                        }
                    }
                });
            });

            observer.observe(video);
            this.observers.set(videoId, observer);
        },

        playVideo: function (videoId, options = {}) {
            const video = document.getElementById(videoId);
            if (!video || this.playedVideos.has(videoId)) return;

            const playPromise = video.play();

            if (playPromise !== undefined) {
                playPromise.then(() => {
                    video.playbackRate = 1.0;
                    console.log(`${videoId} почав відтворення`);
                    this.handleGlassEffect(videoId, options);
                }).catch((error) => {
                    console.warn(`Не вдалося запустити ${videoId}:`, error);
                    this.handleGlassEffect(videoId, options);
                });
            }
        },

        handleGlassEffect: function (videoId, options) {
            if (options.showGlass) {
                const glassContainer = document.getElementById(videoId.replace('-video', '-glass'));
                if (glassContainer) {
                    glassContainer.classList.add('show');
                }
            }
        }
    };

    // =================================
    // Animation System - Optimized
    // =================================
    const AnimationSystem = {
        init: function () {
            // Якщо користувач вимкнув анімації
            if (AppConfig.reducedMotion) {
                this.disableAnimations();
                return;
            }

            this.initGlassContainers();
            this.initCounters();
            this.initCardAnimations();
            this.initHeroButton();
        },

        disableAnimations: function () {
            document.documentElement.style.setProperty('--transition-normal', '0.01ms');
            document.documentElement.style.setProperty('--transition-fast', '0.01ms');
            document.documentElement.style.setProperty('--transition-slow', '0.01ms');
        },

        initGlassContainers: function () {
            const containers = ['about', 'production-glass'];

            containers.forEach(containerId => {
                const container = document.getElementById(containerId);
                if (!container) return;

                const observer = Utils.createObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const className = entry.target.id === 'production-glass' ? 'show' : 'animate';
                            entry.target.classList.add(className);
                            observer.unobserve(entry.target);
                        }
                    });
                });

                observer.observe(container);
            });
        },

        initCounters: function () {
            const counters = document.querySelectorAll('.capacity-counter');
            if (counters.length === 0) return;

            const observer = Utils.createObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCounter(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.4 });

            counters.forEach(counter => observer.observe(counter));
        },

        animateCounter: function (element) {
            if (element.hasAttribute('data-animated')) return;
            element.setAttribute('data-animated', 'true');

            const target = parseInt(element.getAttribute('data-target'));
            if (!target || target <= 0) return;

            const duration = 1500;
            const increment = target / (duration / 50);
            let current = 0;

            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                element.textContent = Math.floor(current).toLocaleString();
            }, 50);
        },

        initCardAnimations: function () {
            const cards = document.querySelectorAll('.capacity__stat-card');
            if (cards.length === 0) return;

            const observer = Utils.createObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate');
                    }
                });
            }, { threshold: 0.1 });

            cards.forEach(card => observer.observe(card));
        },

        initHeroButton: function () {
            const heroBtn = document.getElementById('hero-btn');
            if (!heroBtn) return;

            heroBtn.addEventListener('click', () => {
                window.location.href = '/catalog/';
            });
        }
    };

    // =================================
    // Performance Optimization
    // =================================
    const Performance = {
        init: function () {
            this.optimizeForDevice();
            this.prefetchImportantResources();
        },

        optimizeForDevice: function () {
            // iOS Safari оптимізації
            if (AppConfig.isIOS) {
                document.documentElement.classList.add('ios-device');

                // Оптимізація видео для iOS
                const videos = document.querySelectorAll('video');
                videos.forEach(video => {
                    video.style.webkitTransform = 'translateZ(0)';
                    video.style.transform = 'translateZ(0)';
                });
            }

            // Мобільні оптимізації
            if (AppConfig.isMobile) {
                document.documentElement.classList.add('mobile-device');

                // Вимикаємо складні анімації на мобільних
                const glassElements = document.querySelectorAll('.capacity__glass-backdrop, .production__glass-backdrop');
                glassElements.forEach(element => {
                    element.style.backdropFilter = 'none';
                    element.style.webkitBackdropFilter = 'none';
                });
            }
        },

        prefetchImportantResources: function () {
            // Prefetch важливих ресурсів для наступних сторінок
            const prefetchLinks = [
                '/catalog/',
                '/portfolio/',
                '/reviews/'
            ];

            prefetchLinks.forEach(url => {
                const link = document.createElement('link');
                link.rel = 'prefetch';
                link.href = url;
                document.head.appendChild(link);
            });
        }
    };

    // =================================
    // Error Handling & Logging
    // =================================
    const ErrorHandler = {
        init: function () {
            window.addEventListener('error', (e) => {
                console.warn('JavaScript error:', e.error);
            });

            window.addEventListener('unhandledrejection', (e) => {
                console.warn('Unhandled promise rejection:', e.reason);
            });
        }
    };

    // =================================
    // Initialization Sequence
    // =================================
    function initializeApp() {
        try {
            // Критичні системи першими
            Navigation.init();
            ErrorHandler.init();

            // Системи що залежать від DOM
            VideoSystem.init();
            AnimationSystem.init();

            // Оптимізації в кінці
            Performance.init();

            console.log('✅ GreenSolarTech app initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing app:', error);
        }
    }

    // Запуск після повного завантаження DOM
    initializeApp();

    // =================================
    // Global API для зовнішнього використання
    // =================================
    window.GreenSolarTech = {
        Utils,
        Navigation,
        VideoSystem,
        AnimationSystem,
        version: '2.0.0'
    };
});

// =================================
// CSS-in-JS для критичних стилів (якщо потрібно)
// =================================
function injectCriticalStyles() {
    const styles = `
        /* Critical performance styles */
        .mobile-device .capacity__stat-card,
        .mobile-device .production__step-card {
            box-shadow: none;
            backdrop-filter: none;
            -webkit-backdrop-filter: none;
        }
        
        .ios-device video {
            -webkit-transform: translateZ(0);
            transform: translateZ(0);
        }
        
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }
        }
    `;

    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
}

// Inject critical styles immediately
injectCriticalStyles(); 