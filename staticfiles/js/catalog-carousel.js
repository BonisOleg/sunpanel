// Catalog Carousel Management - Optimized Version
class CatalogCarousel {
    constructor(carouselElement) {
        this.carousel = carouselElement;
        this.track = carouselElement.querySelector('.carousel-track');
        this.prevBtn = carouselElement.querySelector('.carousel-prev');
        this.nextBtn = carouselElement.querySelector('.carousel-next');
        this.cards = carouselElement.querySelectorAll('.product-card');

        this.currentIndex = 0;
        this.cardWidth = 280;
        this.cardGap = 16;
        this.cardsToShow = this.calculateCardsToShow();
        this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);

        // Прапорці для оптимізації
        this.isAnimating = false;
        this.resizeTimeout = null;

        this.init();
    }

    init() {
        if (this.cards.length === 0) return;

        this.updateButtons();
        this.addEventListeners();
        this.setupResizeHandler();
    }

    calculateCardsToShow() {
        const container = this.carousel.querySelector('.carousel-container');
        if (!container) return 1;

        const containerWidth = container.offsetWidth;
        const totalCardWidth = this.cardWidth + this.cardGap;
        return Math.max(1, Math.floor(containerWidth / totalCardWidth));
    }

    addEventListeners() {
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

        // Підтримка свайпів
        this.addTouchSupport();

        // Підтримка клавіатури
        this.addKeyboardSupport();
    }

    setupResizeHandler() {
        // Debounced resize handler для performance
        const debouncedResize = this.debounce(() => {
            this.handleResize();
        }, 250);

        window.addEventListener('resize', debouncedResize);
    }

    handleResize() {
        const newCardsToShow = this.calculateCardsToShow();
        if (newCardsToShow !== this.cardsToShow) {
            this.cardsToShow = newCardsToShow;
            this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);
            this.currentIndex = Math.min(this.currentIndex, this.maxIndex);
            this.updatePosition(false); // без анімації
            this.updateButtons();
        }
    }

    addTouchSupport() {
        let startX = 0;
        let startY = 0;
        let isDragging = false;
        let startTime = 0;

        const handleTouchStart = (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            startTime = Date.now();
            isDragging = true;
        };

        const handleTouchMove = (e) => {
            if (!isDragging) return;

            const deltaX = Math.abs(e.touches[0].clientX - startX);
            const deltaY = Math.abs(e.touches[0].clientY - startY);

            // Якщо горизонтальний рух більший за вертикальний - блокуємо скрол
            if (deltaX > deltaY && deltaX > 10) {
                e.preventDefault();
            }
        };

        const handleTouchEnd = (e) => {
            if (!isDragging) return;

            const endX = e.changedTouches[0].clientX;
            const deltaX = startX - endX;
            const deltaTime = Date.now() - startTime;

            isDragging = false;

            // Мінімальні вимоги для свайпу
            if (Math.abs(deltaX) > 50 && deltaTime < 500) {
                if (deltaX > 0) {
                    this.goToNext();
                } else {
                    this.goToPrev();
                }
            }
        };

        this.track.addEventListener('touchstart', handleTouchStart, { passive: true });
        this.track.addEventListener('touchmove', handleTouchMove, { passive: false });
        this.track.addEventListener('touchend', handleTouchEnd, { passive: true });
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

        this.currentIndex--;
        this.updatePosition();
        this.updateButtons();
    }

    goToNext() {
        if (this.isAnimating || this.currentIndex >= this.maxIndex) return;

        this.currentIndex++;
        this.updatePosition();
        this.updateButtons();
    }

    updatePosition(animate = true) {
        if (!this.track) return;

        if (animate) {
            this.isAnimating = true;
            // Відключаємо прапорець після завершення анімації
            setTimeout(() => {
                this.isAnimating = false;
            }, 300);
        }

        const translateX = -this.currentIndex * (this.cardWidth + this.cardGap);
        this.track.style.transform = `translateX(${translateX}px)`;
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

    // Utility function для debounce
    debounce(func, wait) {
        return (...args) => {
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
}

// Optimized initialization
document.addEventListener('DOMContentLoaded', () => {
    // Ініціалізація каруселей
    const carousels = document.querySelectorAll('.products-carousel');
    if (carousels.length > 0) {
        carousels.forEach(carousel => {
            new CatalogCarousel(carousel);
        });
    }

    // Оптимізована робота з фільтрами
    const filterForm = document.getElementById('filters-form');
    if (filterForm) {
        const filterElements = filterForm.querySelectorAll('.filter-select, .price-input');

        // Debounce для input полів
        let filterTimeout = null;

        filterElements.forEach(element => {
            if (element.type === 'number') {
                // Для числових полів використовуємо debounce
                element.addEventListener('input', () => {
                    clearTimeout(filterTimeout);
                    filterTimeout = setTimeout(() => {
                        filterForm.submit();
                    }, 500);
                });
            } else {
                // Для select відразу
                element.addEventListener('change', () => {
                    filterForm.submit();
                });
            }
        });
    }
}); 