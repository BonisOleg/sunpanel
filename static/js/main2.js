// Arkuda Pellet - Відео та анімації
// Система одноразового відтворення з залишенням на останньому кадрі

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // Система відео - ОДНОРАЗОВЕ ВІДТВОРЕННЯ З ОСТАННІМ КАДРОМ
    window.VideoSystem = {
        observers: new Map(),
        playedVideos: new Set(), // Трекінг відтворених відео

        init: function () {
            this.initVideo('hero-video');
            this.initVideo('capacity-video', { showGlass: true });
            this.initVideo('production-video');
        },

        initVideo: function (videoId, options = {}) {
            const video = document.getElementById(videoId);
            if (!video) return;

            // iOS сумісність без loop
            video.setAttribute('playsinline', '');
            video.setAttribute('webkit-playsinline', '');
            video.muted = true;

            // Встановлюємо вдвічі повільнішу швидкість відтворення
            video.playbackRate = 0.5;

            // Обробник закінчення відео - залишаємо на останньому кадрі
            video.addEventListener('ended', () => {
                console.log(`${videoId} закінчено - залишається на останньому кадрі`);
                this.playedVideos.add(videoId);
            });

            // Обробник завантаження метаданих для коректного позиціонування
            video.addEventListener('loadedmetadata', () => {
                // Якщо відео вже було відтворено, встановлюємо на останній кадр
                if (this.playedVideos.has(videoId)) {
                    video.currentTime = video.duration;
                }
            });

            // Створюємо observer для цього відео
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        // Відтворюємо тільки якщо ще не було відтворено
                        if (!this.playedVideos.has(videoId)) {
                            this.playVideo(videoId, options);
                        } else {
                            // Якщо вже відтворено, показуємо glass ефект якщо потрібно
                            this.handleGlassEffect(videoId, options);
                        }
                    }
                    // Видаляємо логіку паузи - відео залишається як є
                });
            }, { threshold: 0.3 });

            observer.observe(video);
            this.observers.set(videoId, observer);
        },

        playVideo: function (videoId, options = {}) {
            const video = document.getElementById(videoId);
            if (!video) return;

            // Перевіряємо чи вже було відтворено
            if (this.playedVideos.has(videoId)) {
                console.log(`${videoId} вже було відтворено`);
                return;
            }

            const playPromise = video.play();

            if (playPromise !== undefined) {
                playPromise.then(() => {
                    // Переконуємося що швидкість залишається повільною
                    video.playbackRate = 0.5;
                    console.log(`${videoId} почав одноразове відтворення зі швидкістю 0.5x`);
                    this.handleGlassEffect(videoId, options);
                }).catch((error) => {
                    console.warn(`Не вдалося запустити ${videoId}:`, error);
                    // Якщо відео не запускається, все одно показуємо glass
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
        },

        // Метод для перевірки стану відео
        isVideoPlayed: function (videoId) {
            return this.playedVideos.has(videoId);
        },

        // Метод для скидання стану (якщо потрібно для тестування)
        resetVideoState: function (videoId) {
            this.playedVideos.delete(videoId);
            const video = document.getElementById(videoId);
            if (video) {
                video.currentTime = 0;
            }
        },

        // Метод для очищення observers при потребі
        destroy: function () {
            this.observers.forEach((observer, videoId) => {
                observer.disconnect();
            });
            this.observers.clear();
            this.playedVideos.clear();
        }
    };

    // Hero кнопка прокрутки
    window.HeroActions = {
        init: function () {
            const heroBtn = document.getElementById('hero-btn');
            if (heroBtn) {
                heroBtn.addEventListener('click', () => {
                    const aboutSection = document.getElementById('about');
                    if (aboutSection && window.AppUtils) {
                        window.AppUtils.scrollTo(aboutSection);
                    }
                });
            }
        }
    };

    // Система анімацій для скляних блоків
    window.GlassSystem = {
        init: function () {
            const glassContainers = [
                'about',
                'advantages',
                'production-glass'
            ];

            glassContainers.forEach(containerId => {
                this.animateGlassContainer(containerId);
            });
        },

        animateGlassContainer: function (containerId) {
            const container = document.getElementById(containerId);
            if (!container) return;

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        // Для production використовуємо 'show' клас
                        if (entry.target.id === 'production-glass') {
                            entry.target.classList.add('show');
                        } else {
                            entry.target.classList.add('animate');
                        }
                    }
                });
            }, { threshold: 0.2 });

            observer.observe(container);
        }
    };

    // Система лічільників
    window.CounterSystem = {
        init: function () {
            const counters = document.querySelectorAll('.capacity-counter');

            if (counters.length > 0) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            this.animateCounter(entry.target);
                        }
                    });
                }, { threshold: 0.5 });

                counters.forEach(counter => observer.observe(counter));
            }
        },

        animateCounter: function (element) {
            // Перевіряємо чи вже анімовано
            if (element.hasAttribute('data-animated')) return;
            element.setAttribute('data-animated', 'true');

            const target = parseInt(element.getAttribute('data-target'));
            if (!target || target <= 0) return;

            const duration = 2000;
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

    // Ініціалізація всіх систем
    window.VideoSystem.init();
    window.HeroActions.init();
    window.GlassSystem.init();
    window.CounterSystem.init();
}); 