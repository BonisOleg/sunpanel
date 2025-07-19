// Catalog Carousel Management - Enhanced Touch Version
class CatalogCarousel {
    constructor(carouselElement) {
        this.carousel = carouselElement;
        this.track = carouselElement.querySelector('.carousel-track');
        this.prevBtn = carouselElement.querySelector('.carousel-prev');
        this.nextBtn = carouselElement.querySelector('.carousel-next');
        this.cards = carouselElement.querySelectorAll('.product-card');

        this.currentIndex = 0;
        this.cardWidth = this.calculateCardWidth();
        this.cardGap = this.calculateCardGap();
        this.cardsToShow = this.calculateCardsToShow();
        this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);

        // Прапорці для оптимізації
        this.isAnimating = false;
        this.resizeTimeout = null;
        this.isTouchDevice = this.detectTouchDevice();
        this.isMobile = window.innerWidth <= 768;

        // Touch/Swipe змінні
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchEndX = 0;
        this.touchEndY = 0;
        this.isPressed = false;
        this.startTime = 0;

        this.init();
    }

    init() {
        if (this.cards.length === 0) return;

        // Завжди додаємо touch підтримку
        this.setupTouchCarousel();
        this.setupResizeHandler();
    }

    detectTouchDevice() {
        return 'ontouchstart' in window ||
            navigator.maxTouchPoints > 0 ||
            navigator.msMaxTouchPoints > 0;
    }

    calculateCardWidth() {
        const viewportWidth = window.innerWidth;

        if (viewportWidth >= 1400) return 280;
        if (viewportWidth >= 1200) return 260;
        if (viewportWidth >= 992) return 240;
        if (viewportWidth >= 768) return 220;
        if (viewportWidth >= 576) return 180;
        return 160;
    }

    calculateCardGap() {
        const viewportWidth = window.innerWidth;

        if (viewportWidth >= 1400) return 20;
        if (viewportWidth >= 1200) return 18;
        if (viewportWidth >= 992) return 16;
        if (viewportWidth >= 768) return 14;
        if (viewportWidth >= 576) return 12;
        return 10;
    }

    calculateCardsToShow() {
        const container = this.carousel.querySelector('.carousel-container');
        if (!container) return 1;

        const containerWidth = container.offsetWidth;
        const totalCardWidth = this.cardWidth + this.cardGap;
        let cardsToShow = Math.floor(containerWidth / totalCardWidth);

        return Math.max(1, Math.min(cardsToShow, this.cards.length));
    }

    setupTouchCarousel() {
        // На мобільних приховуємо кнопки
        if (this.isMobile) {
            if (this.prevBtn) this.prevBtn.style.display = 'none';
            if (this.nextBtn) this.nextBtn.style.display = 'none';
        } else {
            this.updateButtons();
            this.addButtonListeners();
        }

        // Налаштовуємо контейнер для touch
        this.setupTouchContainer();

        // Додаємо touch listeners до carousel контейнера
        this.addTouchListeners();
    }

    setupTouchContainer() {
        if (this.isMobile) {
            // На мобільних використовуємо нативний скрол + touch events
            this.carousel.style.overflowX = 'auto';
            this.carousel.style.overflowY = 'hidden';
            this.carousel.style.scrollbarWidth = 'none';
            this.carousel.style.msOverflowStyle = 'none';
            this.carousel.style.webkitOverflowScrolling = 'touch';

            // Налаштовуємо track
            this.track.style.display = 'flex';
            this.track.style.gap = `${this.cardGap}px`;
            this.track.style.transform = 'none';
            this.track.style.transition = 'none';
        } else {
            // На desktop/планшетах використовуємо transform
            this.carousel.style.overflowX = 'hidden';
            this.updatePosition(false);
        }
    }

    addTouchListeners() {
        // Додаємо touch events до самого carousel контейнера
        const targetElement = this.isMobile ? this.carousel : this.track;

        // Touch events
        targetElement.addEventListener('touchstart', this.handleTouchStart.bind(this), {
            passive: false
        });
        targetElement.addEventListener('touchmove', this.handleTouchMove.bind(this), {
            passive: false
        });
        targetElement.addEventListener('touchend', this.handleTouchEnd.bind(this), {
            passive: true
        });

        // Mouse events для desktop
        if (!this.isMobile) {
            targetElement.addEventListener('mousedown', this.handleMouseDown.bind(this));
            targetElement.addEventListener('mousemove', this.handleMouseMove.bind(this));
            targetElement.addEventListener('mouseup', this.handleMouseUp.bind(this));
            targetElement.addEventListener('mouseleave', this.handleMouseUp.bind(this));

            // Запобігаємо вибору тексту
            targetElement.addEventListener('selectstart', (e) => e.preventDefault());
            targetElement.style.cursor = 'grab';
        }

        // Keyboard підтримка
        this.addKeyboardSupport();
    }

    handleTouchStart(e) {
        this.isPressed = true;
        this.startTime = Date.now();

        const touch = e.touches ? e.touches[0] : e;
        this.touchStartX = touch.clientX;
        this.touchStartY = touch.clientY;

        console.log('Touch start:', this.touchStartX, this.touchStartY);

        if (!this.isMobile) {
            this.carousel.style.cursor = 'grabbing';
        }
    }

    handleTouchMove(e) {
        if (!this.isPressed) return;

        const touch = e.touches ? e.touches[0] : e;
        const deltaX = Math.abs(touch.clientX - this.touchStartX);
        const deltaY = Math.abs(touch.clientY - this.touchStartY);

        // Якщо горизонтальний рух більший за вертикальний
        if (deltaX > deltaY && deltaX > 5) {
            e.preventDefault(); // Блокуємо скрол сторінки
            console.log('Horizontal swipe detected');
        }
    }

    handleTouchEnd(e) {
        if (!this.isPressed) return;

        const touch = e.changedTouches ? e.changedTouches[0] : e;
        this.touchEndX = touch.clientX;
        this.touchEndY = touch.clientY;

        this.isPressed = false;

        console.log('Touch end:', this.touchEndX, this.touchEndY);

        if (!this.isMobile) {
            this.carousel.style.cursor = 'grab';
        }

        this.handleSwipe();
    }

    handleMouseDown(e) {
        e.preventDefault();
        this.handleTouchStart(e);
    }

    handleMouseMove(e) {
        this.handleTouchMove(e);
    }

    handleMouseUp(e) {
        this.handleTouchEnd(e);
    }

    handleSwipe() {
        const deltaX = this.touchStartX - this.touchEndX;
        const deltaY = this.touchStartY - this.touchEndY;
        const deltaTime = Date.now() - this.startTime;
        const distance = Math.abs(deltaX);

        console.log('Swipe data:', { deltaX, deltaY, distance, deltaTime });

        // Мінімальні вимоги для свайпу
        const minDistance = 20; // Ще менше для кращої чутливості
        const maxTime = 1000;

        // Перевіряємо чи це горизонтальний свайп
        if (Math.abs(deltaY) > Math.abs(deltaX)) {
            console.log('Vertical swipe, ignoring');
            return;
        }

        if (distance > minDistance && deltaTime < maxTime) {
            console.log('Valid swipe detected');
            if (deltaX > 0) {
                // Свайп ліворуч - наступна картка
                console.log('Swiping to next');
                this.goToNext();
            } else {
                // Свайп праворуч - попередня картка
                console.log('Swiping to prev');
                this.goToPrev();
            }
        }
    }

    addButtonListeners() {
        // Кнопки навігації
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.goToPrev();
            });
        }

        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.goToNext();
            });
        }
    }

    setupResizeHandler() {
        const debouncedResize = this.debounce(() => {
            this.handleResize();
        }, 250);

        window.addEventListener('resize', debouncedResize);
    }

    handleResize() {
        const newIsMobile = window.innerWidth <= 768;
        const deviceTypeChanged = newIsMobile !== this.isMobile;

        const newCardWidth = this.calculateCardWidth();
        const newCardGap = this.calculateCardGap();
        const newCardsToShow = this.calculateCardsToShow();

        this.cardWidth = newCardWidth;
        this.cardGap = newCardGap;
        this.isMobile = newIsMobile;

        if (newCardsToShow !== this.cardsToShow || deviceTypeChanged) {
            this.cardsToShow = newCardsToShow;
            this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);
            this.currentIndex = Math.min(this.currentIndex, this.maxIndex);

            // Повторно ініціалізуємо
            this.setupTouchCarousel();
        }
    }

    addKeyboardSupport() {
        this.carousel.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                this.goToPrev();
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                this.goToNext();
            }
        });
    }

    goToPrev() {
        if (this.isAnimating || this.currentIndex === 0) return;

        console.log('Going to previous');
        this.currentIndex--;
        this.updatePosition();
        this.updateButtons();
    }

    goToNext() {
        if (this.isAnimating || this.currentIndex >= this.maxIndex) return;

        console.log('Going to next');
        this.currentIndex++;
        this.updatePosition();
        this.updateButtons();
    }

    updatePosition(animate = true) {
        if (!this.track || this.isMobile) return;

        if (animate) {
            this.isAnimating = true;
            this.track.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';

            setTimeout(() => {
                this.isAnimating = false;
            }, 300);
        } else {
            this.track.style.transition = 'none';
        }

        const translateX = -this.currentIndex * (this.cardWidth + this.cardGap);
        this.track.style.transform = `translateX(${translateX}px)`;

        console.log('Position updated:', translateX);
    }

    updateButtons() {
        if (this.prevBtn) {
            const isDisabled = this.currentIndex === 0;
            this.prevBtn.disabled = isDisabled;
            this.prevBtn.style.opacity = isDisabled ? '0.5' : '1';
            this.prevBtn.setAttribute('aria-disabled', isDisabled);
        }

        if (this.nextBtn) {
            const isDisabled = this.currentIndex >= this.maxIndex;
            this.nextBtn.disabled = isDisabled;
            this.nextBtn.style.opacity = isDisabled ? '0.5' : '1';
            this.nextBtn.setAttribute('aria-disabled', isDisabled);
        }
    }

    debounce(func, wait) {
        return (...args) => {
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
}

// Ініціалізація без підказок
document.addEventListener('DOMContentLoaded', () => {
    const carousels = document.querySelectorAll('.products-carousel');
    if (carousels.length > 0) {
        console.log(`Ініціалізуємо ${carousels.length} каруселей з touch підтримкою`);

        carousels.forEach((carousel, index) => {
            carousel.setAttribute('data-carousel-id', index);
            new CatalogCarousel(carousel);
        });
    }

    // Фільтри
    const filterForm = document.getElementById('filters-form');
    if (filterForm) {
        const filterElements = filterForm.querySelectorAll('.filter-select, .price-input');
        let filterTimeout = null;

        filterElements.forEach(element => {
            if (element.type === 'number') {
                element.addEventListener('input', () => {
                    clearTimeout(filterTimeout);
                    filterTimeout = setTimeout(() => {
                        filterForm.submit();
                    }, 500);
                });
            } else {
                element.addEventListener('change', () => {
                    filterForm.submit();
                });
            }
        });
    }
}); 