// Arkuda Pellet - Відео та анімації
// Оптимізована система для всіх відео

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // Система відео - ОДИН РАЗ НА СЕСІЮ
    window.VideoSystem = {
        playedVideos: new Set(),

        init: function () {
            this.initVideo('hero-video');
            this.initVideo('capacity-video', { showGlass: true });
            this.initVideo('production-video');
        },

        initVideo: function (videoId, options = {}) {
            const video = document.getElementById(videoId);
            if (!video) return;

            video.setAttribute('playsinline', '');
            video.setAttribute('webkit-playsinline', '');

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !this.playedVideos.has(videoId)) {
                        this.playVideoOnce(videoId, options);
                    }
                });
            }, { threshold: 0.3 });

            observer.observe(video);
        },

        playVideoOnce: function (videoId, options) {
            const video = document.getElementById(videoId);
            if (!video || this.playedVideos.has(videoId)) return;

            // Позначаємо як відтворене
            this.playedVideos.add(videoId);

            // Відтворюємо відео
            video.play().then(() => {
                if (options.showGlass) {
                    const glassContainer = document.getElementById(videoId.replace('-video', '-glass'));
                    if (glassContainer) {
                        glassContainer.classList.add('show');
                    }
                }
            }).catch(() => {
                if (options.showGlass) {
                    const glassContainer = document.getElementById(videoId.replace('-video', '-glass'));
                    if (glassContainer) {
                        glassContainer.classList.add('show');
                    }
                }
            });

            // Коли закінчується - зависає на останньому кадрі НАЗАВЖДИ
            video.addEventListener('ended', () => {
                video.currentTime = video.duration;
            }, { once: true });
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
                'advantages-glass',
                'production-glass',
                'contacts-glass'
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

    // Система лічильників
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