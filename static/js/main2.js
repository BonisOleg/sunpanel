// Arkuda Pellet Landing Page JavaScript - Частина 2
// Hero та Scroll Video модулі

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // Hero Video
    window.HeroVideo = {
        init: function () {
            this.video = document.getElementById('hero-video');
            this.heroBtn = document.getElementById('hero-btn');
            this.hasPlayed = false; // Флаг для відстеження відтворення

            if (!this.video) return;

            this.setupVideo();
            this.bindEvents();
        },

        setupVideo: function () {
            // Налаштування для iOS Safari
            if (window.AppGlobals.isIOS) {
                this.video.setAttribute('playsinline', '');
                this.video.setAttribute('webkit-playsinline', '');
            }

            // Автозапуск відео коли у viewport
            if (typeof IntersectionObserver !== 'undefined') {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            if (!this.hasPlayed) {
                                this.playVideo();
                            } else {
                                // Якщо відео вже програвалося, встановлюємо останній кадр
                                this.setToLastFrame();
                            }
                        }
                    });
                }, { threshold: 0.5 });

                observer.observe(this.video);
            }
        },

        playVideo: function () {
            if (this.video.paused && !this.hasPlayed) {
                this.hasPlayed = true; // Встановлюємо флаг
                const playPromise = this.video.play();
                if (playPromise !== undefined) {
                    playPromise.catch(error => {
                        console.log('Video autoplay prevented:', error);
                    });
                }
            }
        },

        setToLastFrame: function () {
            // Встановлюємо останній кадр
            if (this.video.duration && this.video.duration > 0) {
                this.video.currentTime = this.video.duration;
            }
        },

        bindEvents: function () {
            // Кнопка прокрутки
            if (this.heroBtn) {
                this.heroBtn.addEventListener('click', () => {
                    const aboutSection = document.getElementById('about');
                    if (aboutSection) {
                        window.AppUtils.scrollTo(aboutSection);
                    }
                });
            }

            // Зупинка відео на останньому кадрі
            this.video.addEventListener('ended', () => {
                this.video.currentTime = this.video.duration;
            });

            // Додаємо обробник для встановлення останнього кадру після завантаження метаданих
            this.video.addEventListener('loadedmetadata', () => {
                if (this.hasPlayed) {
                    this.setToLastFrame();
                }
            });
        }
    };

    // Scroll Video
    window.ScrollVideo = {
        init: function () {
            this.video = document.getElementById('scroll-video-element');
            this.hasPlayed = false; // Флаг для відстеження відтворення

            if (!this.video) {
                console.warn('Scroll video element not found');
                return;
            }
            console.log('Scroll video element found:', this.video);

            this.setupVideo();
        },

        setupVideo: function () {
            // Налаштування для iOS Safari
            if (window.AppGlobals.isIOS) {
                this.video.setAttribute('playsinline', '');
                this.video.setAttribute('webkit-playsinline', '');
                console.log('iOS video attributes set');
            }

            // Автозапуск відео коли у viewport
            if (typeof IntersectionObserver !== 'undefined') {
                console.log('Setting up IntersectionObserver for scroll video');
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            if (!this.hasPlayed) {
                                console.log('Scroll video is in viewport for first time');
                                this.playVideo();
                            } else {
                                // Якщо відео вже програвалося, встановлюємо останній кадр
                                console.log('Scroll video returning to viewport, setting last frame');
                                this.setToLastFrame();
                            }
                        }
                    });
                }, { threshold: 0.5 });

                observer.observe(this.video);
            }

            // Зупинка відео на останньому кадрі
            this.video.addEventListener('ended', () => {
                console.log('Scroll video ended, setting to last frame');
                this.video.currentTime = this.video.duration;
            });

            // Додаємо обробник для встановлення останнього кадру після завантаження метаданих
            this.video.addEventListener('loadedmetadata', () => {
                if (this.hasPlayed) {
                    console.log('Scroll video metadata loaded, setting to last frame');
                    this.setToLastFrame();
                }
            });
        },

        playVideo: function () {
            if (this.video.paused && !this.hasPlayed) {
                this.hasPlayed = true; // Встановлюємо флаг
                console.log('Attempting to play scroll video (first time only)');
                const playPromise = this.video.play();
                if (playPromise !== undefined) {
                    playPromise.catch(error => {
                        console.warn('Scroll video autoplay prevented:', error);
                    });
                }
            }
        },

        setToLastFrame: function () {
            // Встановлюємо останній кадр
            if (this.video.duration && this.video.duration > 0) {
                this.video.currentTime = this.video.duration;
                console.log('Scroll video set to last frame');
            }
        }
    };

    // Capacity Video
    window.CapacityVideo = {
        init: function () {
            this.video = document.getElementById('capacity-video');
            this.hasPlayed = false; // Флаг для відстеження відтворення

            if (!this.video) {
                console.warn('Capacity video element not found');
                return;
            }
            console.log('Capacity video element found:', this.video);

            this.setupVideo();
            // Показуємо glass блок одразу при ініціалізації
            this.showGlassEffect();
        },

        setupVideo: function () {
            // Налаштування для iOS Safari
            if (window.AppGlobals.isIOS) {
                this.video.setAttribute('playsinline', '');
                this.video.setAttribute('webkit-playsinline', '');
                console.log('iOS video attributes set for capacity video');
            }

            // Автозапуск відео коли у viewport
            if (typeof IntersectionObserver !== 'undefined') {
                console.log('Setting up IntersectionObserver for capacity video');
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            if (!this.hasPlayed) {
                                console.log('Capacity video is in viewport for first time');
                                this.playVideo();
                            } else {
                                // Якщо відео вже програвалося, встановлюємо останній кадр і показуємо glass
                                console.log('Capacity video returning to viewport, setting last frame');
                                this.setToLastFrame();
                                this.showGlassEffect();
                            }
                        }
                    });
                }, { threshold: 0.5 });

                observer.observe(this.video);
            }

            // Зупинка відео на останньому кадрі
            this.video.addEventListener('ended', () => {
                console.log('Capacity video ended, setting to last frame');
                this.video.currentTime = this.video.duration;
            });

            // Додаємо обробник для встановлення останнього кадру після завантаження метаданих
            this.video.addEventListener('loadedmetadata', () => {
                if (this.hasPlayed) {
                    console.log('Capacity video metadata loaded, setting to last frame');
                    this.setToLastFrame();
                }
            });
        },

        playVideo: function () {
            if (this.video.paused && !this.hasPlayed) {
                this.hasPlayed = true; // Встановлюємо флаг
                console.log('Attempting to play capacity video (first time only)');
                const playPromise = this.video.play();
                if (playPromise !== undefined) {
                    playPromise.then(() => {
                        // Показуємо glass блок одразу без паузи
                        this.showGlassEffect();
                    }).catch(error => {
                        console.warn('Capacity video autoplay prevented:', error);
                        // Все одно показуємо glass навіть якщо відео не запустилось
                        this.showGlassEffect();
                    });
                } else {
                    // Fallback для старих браузерів
                    this.showGlassEffect();
                }
            }
        },

        showGlassEffect: function () {
            const glassContainer = document.getElementById('capacity-glass');
            if (glassContainer) {
                glassContainer.classList.add('show');
                console.log('Capacity glass effect shown');
            }
        },

        setToLastFrame: function () {
            // Встановлюємо останній кадр
            if (this.video.duration && this.video.duration > 0) {
                this.video.currentTime = this.video.duration;
                console.log('Capacity video set to last frame');
            }
        }
    };

    // Ініціалізація відео модулів
    console.log('Initializing video modules...');
    window.HeroVideo.init();
    window.ScrollVideo.init();
    window.CapacityVideo.init();
}); 