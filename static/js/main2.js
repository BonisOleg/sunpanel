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

    // Production Snake Animation
    window.ProductionSnake = {
        init: function () {
            this.snakeItems = document.querySelectorAll('.snake-item');
            this.snakeLines = document.querySelectorAll('.snake-line');
            this.hasAnimated = false;

            if (!this.snakeItems.length) return;

            this.setupObserver();
            this.addInitialStyles();
        },

        addInitialStyles: function () {
            // Спочатку приховуємо всі елементи
            this.snakeItems.forEach((item, index) => {
                item.style.opacity = '0';
                item.style.transform = 'translateY(30px) scale(0.9)';
                item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            });

            this.snakeLines.forEach(line => {
                line.style.opacity = '0';
                line.style.transform = 'scaleX(0)';
                line.style.transformOrigin = 'left center';
                line.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            });
        },

        setupObserver: function () {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !this.hasAnimated) {
                        this.animateSnake();
                        this.hasAnimated = true;
                    }
                });
            }, { threshold: 0.3 });

            const productionSection = document.getElementById('production');
            if (productionSection) {
                observer.observe(productionSection);
            }
        },

        animateSnake: function () {
            // Анімуємо блоки по черзі
            this.snakeItems.forEach((item, index) => {
                setTimeout(() => {
                    item.style.opacity = '1';
                    item.style.transform = 'translateY(0) scale(1)';
                }, index * 200);
            });

            // Анімуємо лінії з затримкою
            setTimeout(() => {
                this.snakeLines.forEach((line, index) => {
                    setTimeout(() => {
                        line.style.opacity = '0.6';
                        line.style.transform = 'scaleX(1)';
                    }, index * 100);
                });
            }, this.snakeItems.length * 200 + 300);

            // Додаємо hover ефекти після завершення анімації
            setTimeout(() => {
                this.addHoverEffects();
            }, this.snakeItems.length * 200 + this.snakeLines.length * 100 + 500);
        },

        addHoverEffects: function () {
            this.snakeItems.forEach(item => {
                item.addEventListener('mouseenter', () => {
                    this.highlightPath(item);
                });

                item.addEventListener('mouseleave', () => {
                    this.resetHighlight();
                });
            });
        },

        highlightPath: function (item) {
            const step = parseInt(item.dataset.step);

            // Підсвітити поточний блок
            item.style.transform = 'translateY(-8px) scale(1.05)';
            item.style.boxShadow = '0 15px 40px rgba(255, 107, 53, 0.3)';

            // Підсвітити пов'язані лінії
            this.snakeLines.forEach(line => {
                const lineClass = line.className;
                if (lineClass.includes(`--${step}-`) || lineClass.includes(`-${step}`)) {
                    line.style.opacity = '1';
                    line.style.background = 'linear-gradient(90deg, #ff6b35, #f7931e)';
                    line.style.height = '4px';
                }
            });
        },

        resetHighlight: function () {
            this.snakeItems.forEach(item => {
                item.style.transform = '';
                item.style.boxShadow = '';
            });

            this.snakeLines.forEach(line => {
                line.style.opacity = '0.6';
                line.style.background = 'linear-gradient(90deg, var(--primary-color), var(--secondary-color))';
                line.style.height = '3px';
            });
        }
    };

    // Ініціалізація модулів
    window.HeroVideo.init();
    window.ScrollVideo.init();
    window.CapacityVideo.init();
    window.ProductionSnake.init();
}); 