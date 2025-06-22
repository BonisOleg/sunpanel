// Arkuda Pellet - Відео та анімації
// Оптимізована система для всіх відео

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // Універсальна система для всіх відео
    window.VideoSystem = {
        videos: new Map(),

        init: function () {
            // Ініціалізуємо всі відео
            this.initVideo('hero-video', { playOnce: false });
            this.initVideo('capacity-video', { playOnce: false, showGlass: true });
            this.initVideo('production-video', { playOnce: false });
        },

        initVideo: function (videoId, options = {}) {
            const video = document.getElementById(videoId);
            if (!video) return;

            // Встановлюємо iOS-сумісність
            if (window.AppGlobals && window.AppGlobals.isIOS) {
                video.setAttribute('playsinline', '');
                video.setAttribute('webkit-playsinline', '');
            }

            // Зберігаємо відео в системі
            this.videos.set(videoId, {
                element: video,
                options: options,
                isPlaying: false
            });

            // Створюємо observer для відео
            this.createVideoObserver(videoId);
        },

        createVideoObserver: function (videoId) {
            const videoData = this.videos.get(videoId);
            if (!videoData) return;

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.playVideo(videoId);
                    } else {
                        this.pauseVideo(videoId);
                    }
                });
            }, { threshold: 0.3 });

            observer.observe(videoData.element);
        },

        playVideo: function (videoId) {
            const videoData = this.videos.get(videoId);
            if (!videoData || videoData.isPlaying) return;

            const video = videoData.element;

            // Перезапускаємо відео з початку для плавного відтворення
            video.currentTime = 0;

            const playPromise = video.play();
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    videoData.isPlaying = true;

                    // Показуємо glass ефект якщо потрібно
                    if (videoData.options.showGlass) {
                        this.showGlassEffect(videoId);
                    }
                }).catch(() => {
                    // Мовчки обробляємо помилку автоплею
                    if (videoData.options.showGlass) {
                        this.showGlassEffect(videoId);
                    }
                });
            }

            // Обробляємо закінчення відео
            video.addEventListener('ended', () => {
                videoData.isPlaying = false;
                // Залишаємо на останньому кадрі для плавності
                if (video.duration && video.duration > 0) {
                    video.currentTime = video.duration;
                }
            });
        },

        pauseVideo: function (videoId) {
            const videoData = this.videos.get(videoId);
            if (!videoData) return;

            const video = videoData.element;
            if (!video.paused) {
                video.pause();
                videoData.isPlaying = false;
            }
        },

        showGlassEffect: function (videoId) {
            const glassContainer = document.getElementById(videoId.replace('-video', '-glass'));
            if (glassContainer && !glassContainer.classList.contains('show')) {
                requestAnimationFrame(() => {
                    glassContainer.classList.add('show');
                });
            }
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
                        setTimeout(() => {
                            // Для production використовуємо 'show' клас
                            if (entry.target.id === 'production-glass') {
                                entry.target.classList.add('show');
                            } else {
                                entry.target.classList.add('animate');
                            }
                        }, 200);
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