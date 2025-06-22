// Arkuda Pellet Landing Page JavaScript - Частина 2
// Hero та Scroll Video модулі

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // Спільна логіка для всіх відео
    const VideoBase = {
        setupIOS: function (video) {
            if (window.AppGlobals && window.AppGlobals.isIOS) {
                video.setAttribute('playsinline', '');
                video.setAttribute('webkit-playsinline', '');
            }
        },

        setToLastFrame: function (video) {
            if (video.duration && video.duration > 0) {
                video.currentTime = video.duration;
            }
        },

        createObserver: function (callback, threshold = 0.5) {
            if (typeof IntersectionObserver === 'undefined') return null;
            return new IntersectionObserver(callback, { threshold });
        }
    };

    // Hero Video - Оптимізовано
    window.HeroVideo = {
        init: function () {
            this.video = document.getElementById('hero-video');
            this.heroBtn = document.getElementById('hero-btn');
            this.hasPlayed = false;

            if (!this.video) return;

            this.setupVideo();
            this.bindEvents();
        },

        setupVideo: function () {
            VideoBase.setupIOS(this.video);

            const observer = VideoBase.createObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        if (!this.hasPlayed) {
                            this.playVideo();
                        } else {
                            VideoBase.setToLastFrame(this.video);
                        }
                    }
                });
            });

            if (observer) observer.observe(this.video);
        },

        playVideo: function () {
            if (this.video.paused && !this.hasPlayed) {
                this.hasPlayed = true;
                const playPromise = this.video.play();
                if (playPromise !== undefined) {
                    playPromise.catch(() => {
                        // Мовчки обробляємо помилку автоплею
                    });
                }
            }
        },

        bindEvents: function () {
            // Кнопка прокрутки
            if (this.heroBtn) {
                this.heroBtn.addEventListener('click', () => {
                    const aboutSection = document.getElementById('about');
                    if (aboutSection && window.AppUtils) {
                        window.AppUtils.scrollTo(aboutSection);
                    }
                });
            }

            // Події відео
            this.video.addEventListener('ended', () => {
                VideoBase.setToLastFrame(this.video);
            });

            this.video.addEventListener('loadedmetadata', () => {
                if (this.hasPlayed) {
                    VideoBase.setToLastFrame(this.video);
                }
            });
        }
    };

    // Scroll Video - Оптимізовано
    window.ScrollVideo = {
        init: function () {
            this.video = document.getElementById('scroll-video-element');
            this.hasPlayed = false;

            if (!this.video) return;
            this.setupVideo();
        },

        setupVideo: function () {
            VideoBase.setupIOS(this.video);

            const observer = VideoBase.createObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        if (!this.hasPlayed) {
                            this.playVideo();
                        } else {
                            VideoBase.setToLastFrame(this.video);
                        }
                    }
                });
            });

            if (observer) observer.observe(this.video);

            // Події відео
            this.video.addEventListener('ended', () => {
                VideoBase.setToLastFrame(this.video);
            });

            this.video.addEventListener('loadedmetadata', () => {
                if (this.hasPlayed) {
                    VideoBase.setToLastFrame(this.video);
                }
            });
        },

        playVideo: function () {
            if (this.video.paused && !this.hasPlayed) {
                this.hasPlayed = true;
                const playPromise = this.video.play();
                if (playPromise !== undefined) {
                    playPromise.catch(() => {
                        // Мовчки обробляємо помилку автоплею
                    });
                }
            }
        }
    };

    // Capacity Video - Оптимізовано
    window.CapacityVideo = {
        init: function () {
            this.video = document.getElementById('capacity-video');
            this.hasPlayed = false;

            if (!this.video) return;

            this.setupVideo();
            // Показуємо glass одразу
            this.showGlassEffect();
        },

        setupVideo: function () {
            VideoBase.setupIOS(this.video);

            const observer = VideoBase.createObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        if (!this.hasPlayed) {
                            this.playVideo();
                        } else {
                            VideoBase.setToLastFrame(this.video);
                            this.showGlassEffect();
                        }
                    }
                });
            });

            if (observer) observer.observe(this.video);

            // Події відео
            this.video.addEventListener('ended', () => {
                VideoBase.setToLastFrame(this.video);
            });

            this.video.addEventListener('loadedmetadata', () => {
                if (this.hasPlayed) {
                    VideoBase.setToLastFrame(this.video);
                }
            });
        },

        playVideo: function () {
            if (this.video.paused && !this.hasPlayed) {
                this.hasPlayed = true;
                const playPromise = this.video.play();
                if (playPromise !== undefined) {
                    playPromise.then(() => {
                        this.showGlassEffect();
                    }).catch(() => {
                        this.showGlassEffect();
                    });
                } else {
                    this.showGlassEffect();
                }
            }
        },

        showGlassEffect: function () {
            const glassContainer = document.getElementById('capacity-glass');
            if (glassContainer && !glassContainer.classList.contains('show')) {
                requestAnimationFrame(() => {
                    glassContainer.classList.add('show');
                });
            }
        }
    };

    // Production Snake Animation - Спрощена версія
    window.ProductionSnake = {
        init: function () {
            const productionSection = document.getElementById('production');
            if (!productionSection) return;

            // Спрощена анімація через CSS
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate');
                    }
                });
            }, { threshold: 0.3 });

            observer.observe(productionSection);
        }
    };

    // Ініціалізація модулів
    window.HeroVideo.init();
    window.ScrollVideo.init();
    window.CapacityVideo.init();
    window.ProductionSnake.init();

    // About section glass container animation
    const aboutGlassContainer = document.getElementById('about-glass');

    if (aboutGlassContainer) {
        const aboutObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate');
                }
            });
        }, {
            threshold: 0.2,
            rootMargin: '0px 0px -50px 0px'
        });

        aboutObserver.observe(aboutGlassContainer);
    }
}); 