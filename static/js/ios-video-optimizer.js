/**
 * iOS Safari Video Optimizer
 * Оптимізує відео для мобільних пристроїв, особливо iOS Safari
 */

(function () {
    'use strict';

    // Детекція мобільного пристрою та iOS Safari
    const isMobile = window.innerWidth <= 768 || /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

        // Функція для зміни джерела відео залежно від розміру екрана
    function optimizeVideoSource(video) {
        const videoId = video.id;
        const mobileSrc = video.getAttribute('data-mobile-src');
        const desktopSrc = video.getAttribute('data-desktop-src');
        
        // Встановлюємо правильне джерело
        if (isMobile && mobileSrc) {
            video.src = mobileSrc;
            // Оновлюємо source елемент теж
            const source = video.querySelector('source');
            if (source) {
                source.src = mobileSrc;
            }
            console.log(`Мобільне відео завантажено для ${videoId}: ${mobileSrc}`);
        } else if (!isMobile && desktopSrc) {
            video.src = desktopSrc;
            // Оновлюємо source елемент теж
            const source = video.querySelector('source');
            if (source) {
                source.src = desktopSrc;
            }
            console.log(`Десктопне відео завантажено для ${videoId}: ${desktopSrc}`);
        }

        // Спеціальні налаштування для iOS Safari
        if (isIOS && isSafari) {
            video.setAttribute('webkit-playsinline', 'true');
            video.setAttribute('playsinline', 'true');
            video.muted = true;
            video.autoplay = false; // iOS Safari не підтримує autoplay без взаємодії користувача

            // Додаємо обробник для ручного запуску
            video.addEventListener('canplay', function () {
                if (video.paused) {
                    video.play().catch(e => {
                        console.log(`Не вдалося автоматично запустити відео ${videoId}:`, e);
                    });
                }
            });
        }
    }

    // Функція для налаштування інтерсекшн обсервера
    function setupIntersectionObserver() {
        if ('IntersectionObserver' in window) {
            const videoObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    const video = entry.target;
                    if (entry.isIntersecting) {
                        // Відео в зоні видимості - завантажуємо і запускаємо
                        if (video.readyState < 2) { // HAVE_CURRENT_DATA
                            video.load();
                        }

                        video.play().catch(e => {
                            console.log(`Помилка відтворення відео ${video.id}:`, e);
                        });
                    } else {
                        // Відео поза зоною видимості - ставимо на паузу для економії ресурсів
                        if (!video.paused) {
                            video.pause();
                        }
                    }
                });
            }, {
                threshold: 0.25, // Запускати коли 25% відео видимо
                rootMargin: '50px 0px' // Додаткові 50px зверху і знизу
            });

            // Додаємо всі відео до спостереження
            document.querySelectorAll('video').forEach(video => {
                videoObserver.observe(video);
            });
        }
    }

    // Функція ініціалізації
    function initVideoOptimizer() {
        const videos = document.querySelectorAll('video');

        videos.forEach(video => {
            optimizeVideoSource(video);

            // Додаткові налаштування для всіх відео
            video.setAttribute('preload', isMobile ? 'metadata' : 'metadata');
            video.muted = true;
            video.setAttribute('playsinline', 'true');

            // iOS Safari специфічні налаштування
            if (isIOS) {
                video.setAttribute('webkit-playsinline', 'true');
                video.setAttribute('x-webkit-airplay', 'allow');
                video.controls = false;

                // Додаємо клас для CSS стилізації
                video.classList.add('ios-optimized');
            }

            // Обробники подій для кращої продуктивності
            video.addEventListener('loadstart', function () {
                console.log(`Почалося завантаження відео: ${video.id}`);
            });

            video.addEventListener('canplaythrough', function () {
                console.log(`Відео готове до відтворення: ${video.id}`);
            });

            video.addEventListener('error', function (e) {
                console.error(`Помилка завантаження відео ${video.id}:`, e);
            });
        });

        // Налаштовуємо intersection observer
        setupIntersectionObserver();
    }

    // Функція для обробки зміни орієнтації
    function handleOrientationChange() {
        setTimeout(() => {
            const videos = document.querySelectorAll('video');
            videos.forEach(optimizeVideoSource);
        }, 100); // Невелика затримка після зміни орієнтації
    }

    // Ініціалізація після завантаження DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVideoOptimizer);
    } else {
        initVideoOptimizer();
    }

    // Обробка зміни розміру вікна та орієнтації
    window.addEventListener('resize', handleOrientationChange);
    window.addEventListener('orientationchange', handleOrientationChange);

    // Логування для дебагу
    console.log('iOS Video Optimizer ініціалізовано:', {
        isMobile,
        isIOS,
        isSafari,
        screenWidth: window.innerWidth
    });

})(); 