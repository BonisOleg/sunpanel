/**
 * iOS Safari Video Optimizer
 * Оптимізує відео для мобільних пристроїв, особливо iOS Safari
 */

(function () {
    'use strict';

    // Функція для точної детекції мобільного пристрою
    function isMobileDevice() {
        // Перевіряємо ширину екрана спочатку (головний критерій)
        if (window.innerWidth <= 768) {
            console.log('Мобільний пристрій детектовано за шириною екрана:', window.innerWidth);
            return true;
        }

        // Перевіряємо Chrome DevTools емуляцію
        if (window.navigator.webdriver || window.chrome?.runtime?.onConnect) {
            console.log('Chrome DevTools емуляція детектована');
            if (window.innerWidth <= 768) {
                return true;
            }
        }

        // Перевіряємо touch support (характерно для мобільних)
        if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
            console.log('Touch підтримка детектована');
            if (window.innerWidth <= 768) {
                return true;
            }
        }

        // Перевіряємо user agent
        const userAgent = navigator.userAgent || navigator.vendor || window.opera;
        const mobileRegex = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile|mobile|phone/i;

        if (mobileRegex.test(userAgent)) {
            console.log('Мобільний пристрій детектовано за User Agent:', userAgent);
            return true;
        }

        console.log('Десктопний пристрій детектовано');
        return false;
    }

    // Детекція iOS
    function isIOSDevice() {
        const userAgent = navigator.userAgent || navigator.vendor || window.opera;
        return /iPad|iPhone|iPod/.test(userAgent) && !window.MSStream;
    }

    // Детекція Safari
    function isSafariBrowser() {
        const userAgent = navigator.userAgent || navigator.vendor || window.opera;
        return /Safari/.test(userAgent) && /Apple Computer/.test(navigator.vendor);
    }

    // Поточні стани
    let isMobile = isMobileDevice();
    let isIOS = isIOSDevice();
    let isSafari = isSafariBrowser();

    console.log('Device Detection:', { isMobile, isIOS, isSafari, width: window.innerWidth });

    // Функція для зміни джерела відео
    function setVideoSource(video) {
        const videoId = video.id || 'unknown';
        const mobileSrc = video.getAttribute('data-mobile-src');
        const desktopSrc = video.getAttribute('data-desktop-src');

        console.log(`Налаштування відео ${videoId}:`, {
            isMobile,
            screenWidth: window.innerWidth,
            mobileSrc,
            desktopSrc,
            currentSrc: video.src
        });

        let targetSrc = null;

        if (isMobile && mobileSrc) {
            targetSrc = mobileSrc;
            console.log(`✅ Встановлюю мобільне відео для ${videoId}: ${mobileSrc}`);
        } else if (!isMobile && desktopSrc) {
            targetSrc = desktopSrc;
            console.log(`✅ Встановлюю десктопне відео для ${videoId}: ${desktopSrc}`);
        } else if (desktopSrc) {
            // Fallback на десктопне відео
            targetSrc = desktopSrc;
            console.log(`⚠️ Fallback на десктопне відео для ${videoId}: ${desktopSrc}`);
        }

        if (targetSrc) {
            const currentSrc = video.src || video.querySelector('source')?.src;

            if (currentSrc !== targetSrc) {
                console.log(`🔄 Змінюю джерело відео ${videoId} з "${currentSrc}" на "${targetSrc}"`);

                // Зупиняємо поточне відео
                video.pause();

                // Змінюємо джерело
                video.src = targetSrc;

                // Оновлюємо source елемент
                const source = video.querySelector('source');
                if (source) {
                    source.src = targetSrc;
                }

                // Перезавантажуємо відео
                video.load();

                console.log(`✅ Відео ${videoId} успішно оновлено`);
            } else {
                console.log(`ℹ️ Відео ${videoId} вже має правильне джерело`);
            }
        } else {
            console.error(`❌ Не знайдено підходящого джерела для відео ${videoId}`);
        }
    }

    // Функція для налаштування відео для iOS Safari
    function setupVideoForIOS(video) {
        // Видаляємо всі контроли
        video.removeAttribute('controls');
        video.controls = false;

        // Налаштування для iOS Safari
        video.setAttribute('playsinline', 'true');
        video.setAttribute('webkit-playsinline', 'true');
        video.setAttribute('x-webkit-airplay', 'allow');
        video.muted = true;
        video.autoplay = false;

        // Додаємо клас для CSS стилізації
        video.classList.add('ios-optimized');

        // Обробники для iOS Safari
        video.addEventListener('loadedmetadata', function () {
            if (video.paused) {
                video.play().catch(error => {
                    console.log(`iOS Safari: не вдалося запустити відео ${video.id}:`, error.message);
                });
            }
        });
    }

    // Функція для зміни джерела зображень
    function setImageSource(img) {
        const mobileSrc = img.getAttribute('data-mobile-src');
        const desktopSrc = img.getAttribute('data-desktop-src');

        console.log(`Налаштування зображення:`, {
            isMobile,
            screenWidth: window.innerWidth,
            mobileSrc,
            desktopSrc,
            currentSrc: img.src
        });

        let targetSrc = null;

        if (isMobile && mobileSrc) {
            targetSrc = mobileSrc;
            console.log(`✅ Встановлюю мобільне зображення: ${mobileSrc}`);
        } else if (!isMobile && desktopSrc) {
            targetSrc = desktopSrc;
            console.log(`✅ Встановлюю десктопне зображення: ${desktopSrc}`);
        } else if (desktopSrc) {
            targetSrc = desktopSrc;
            console.log(`⚠️ Fallback на десктопне зображення: ${desktopSrc}`);
        }

        if (targetSrc && img.src !== targetSrc) {
            console.log(`🔄 Змінюю зображення з "${img.src}" на "${targetSrc}"`);
            img.src = targetSrc;
            console.log(`✅ Зображення успішно оновлено`);
        } else if (targetSrc) {
            console.log(`ℹ️ Зображення вже має правильне джерело`);
        }
    }

    // Функція для налаштування всіх відео
    function setupVideo(video) {
        // Встановлюємо правильне джерело
        setVideoSource(video);

        // Загальні налаштування
        video.muted = true;
        video.setAttribute('playsinline', 'true');
        video.removeAttribute('controls');
        video.controls = false;

        // Спеціальні налаштування для iOS
        if (isIOS) {
            setupVideoForIOS(video);
        }

        // Налаштування preload для мобільних
        if (isMobile) {
            if (video.id === 'production-video') {
                video.setAttribute('preload', 'none');
            } else {
                video.setAttribute('preload', 'metadata');
            }
        }

        // Обробники подій
        video.addEventListener('loadstart', function () {
            console.log(`Завантаження відео: ${video.id}`);
        });

        video.addEventListener('canplaythrough', function () {
            console.log(`Відео готове: ${video.id}`);
        });

        video.addEventListener('error', function (e) {
            console.error(`Помилка відео ${video.id}:`, e);
        });
    }

    // Intersection Observer для відео
    function setupVideoObserver() {
        if (!('IntersectionObserver' in window)) {
            return;
        }

        const videoObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const video = entry.target;

                if (entry.isIntersecting) {
                    // Відео в зоні видимості
                    if (video.readyState < 2) {
                        video.load();
                    }

                    if (video.paused) {
                        video.play().catch(error => {
                            console.log(`Не вдалося запустити відео ${video.id}:`, error.message);
                        });
                    }
                } else {
                    // Відео поза зоною видимості - економимо ресурси
                    if (!video.paused && !isIOS) {
                        // На iOS краще не ставити на паузу через особливості Safari
                        video.pause();
                    }
                }
            });
        }, {
            threshold: 0.25,
            rootMargin: '50px 0px'
        });

        // Додаємо всі відео до спостереження
        document.querySelectorAll('video').forEach(video => {
            videoObserver.observe(video);
        });
    }

    // Функція для обробки зміни розміру вікна
    function handleResize() {
        // Оновлюємо статус мобільного пристрою
        const wasMobile = isMobile;
        isMobile = isMobileDevice();

        // Якщо статус змінився, оновлюємо відео та зображення
        if (wasMobile !== isMobile) {
            console.log('Статус пристрою змінився:', { was: wasMobile, now: isMobile });

            document.querySelectorAll('video').forEach(video => {
                setVideoSource(video);
            });

            document.querySelectorAll('img[data-mobile-src]').forEach(img => {
                setImageSource(img);
            });
        }
    }

    // Дебаунс для resize
    let resizeTimeout;
    function debouncedResize() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleResize, 250);
    }

    // Ініціалізація
    function initVideoOptimizer() {
        console.log('🚀 Ініціалізація Video Optimizer...');
        console.log('📱 Стан детекції:', {
            isMobile,
            isIOS,
            isSafari,
            screenWidth: window.innerWidth,
            userAgent: navigator.userAgent
        });

        const videos = document.querySelectorAll('video');
        console.log(`📹 Знайдено ${videos.length} відео елементів`);

        if (videos.length === 0) {
            console.warn('⚠️ Відео елементи не знайдені!');
            return;
        }

        videos.forEach((video, index) => {
            console.log(`🎬 Налаштування відео ${index + 1}:`, video.id || 'без ID');
            setupVideo(video);
        });

        // Налаштовуємо зображення
        const images = document.querySelectorAll('img[data-mobile-src]');
        console.log(`🖼️ Знайдено ${images.length} зображень з мобільними версіями`);

        images.forEach((img, index) => {
            console.log(`🎨 Налаштування зображення ${index + 1}`);
            setImageSource(img);
        });

        // Налаштовуємо observer
        setupVideoObserver();

        console.log('✅ Video Optimizer ініціалізовано успішно');

        // Додаткова перевірка через 1 секунду
        setTimeout(() => {
            console.log('🔍 Перевірка стану відео через 1 секунду...');
            videos.forEach(video => {
                console.log(`📊 Відео ${video.id}:`, {
                    src: video.src,
                    readyState: video.readyState,
                    paused: video.paused
                });
            });
        }, 1000);
    }

    // Примусове переключення на мобільні відео та зображення якщо ширина <= 768px
    function forceMobileSwitch() {
        if (window.innerWidth <= 768) {
            console.log('🎯 Примусове переключення на мобільні медіа для вузького екрана');

            // Переключаємо відео
            const videos = document.querySelectorAll('video[data-mobile-src]');
            videos.forEach(video => {
                const mobileSrc = video.getAttribute('data-mobile-src');
                if (mobileSrc && video.src !== mobileSrc) {
                    console.log(`🔄 Примусово змінюю відео ${video.id} на мобільну версію: ${mobileSrc}`);
                    video.pause();
                    video.src = mobileSrc;
                    const source = video.querySelector('source');
                    if (source) {
                        source.src = mobileSrc;
                    }
                    video.load();
                }
            });

            // Переключаємо зображення
            const images = document.querySelectorAll('img[data-mobile-src]');
            images.forEach(img => {
                const mobileSrc = img.getAttribute('data-mobile-src');
                if (mobileSrc && img.src !== mobileSrc) {
                    console.log(`🔄 Примусово змінюю зображення на мобільну версію: ${mobileSrc}`);
                    img.src = mobileSrc;
                }
            });
        }
    }

    // Запуск після завантаження DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initVideoOptimizer();
            forceMobileSwitch();
        });
    } else {
        initVideoOptimizer();
        forceMobileSwitch();
    }

    // Додатково запускаємо через 500мс для надійності
    setTimeout(() => {
        forceMobileSwitch();

        // Оновлюємо детекцію
        isMobile = isMobileDevice();
        console.log('🔄 Повторна детекція:', { isMobile, width: window.innerWidth });

        document.querySelectorAll('video').forEach(setVideoSource);
        document.querySelectorAll('img[data-mobile-src]').forEach(setImageSource);
    }, 500);

    // Обробка зміни розміру вікна та орієнтації
    window.addEventListener('resize', debouncedResize);
    window.addEventListener('orientationchange', function () {
        setTimeout(debouncedResize, 100);
    });

})(); 