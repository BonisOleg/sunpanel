// Простий Catalog Carousel з Touch підтримкою
class SimpleCatalogCarousel {
    constructor(carouselElement) {
        this.carousel = carouselElement;
        this.track = carouselElement.querySelector('.carousel-track');
        this.container = carouselElement.querySelector('.carousel-container');
        this.prevBtn = carouselElement.querySelector('.carousel-prev');
        this.nextBtn = carouselElement.querySelector('.carousel-next');
        this.cards = carouselElement.querySelectorAll('.product-card');

        this.currentIndex = 0;
        this.isMobile = window.innerWidth <= 768;
        this.isAnimating = false;

        // Touch змінні
        this.startX = 0;
        this.currentX = 0;
        this.isDragging = false;
        this.startTime = 0;

        this.init();
    }

    init() {
        if (this.cards.length === 0) return;

        this.setupLayout();
        this.setupEventListeners();
        this.handleResize();
    }

    setupLayout() {
        if (this.isMobile) {
            // На мобільних: нативний скрол + центрування
            this.setupMobileLayout();
        } else {
            // На desktop: JavaScript керування
            this.setupDesktopLayout();
        }
    }

    setupMobileLayout() {
        // Приховуємо кнопки
        if (this.prevBtn) this.prevBtn.style.display = 'none';
        if (this.nextBtn) this.nextBtn.style.display = 'none';

        // Налаштовуємо smooth scroll
        this.container.style.overflowX = 'auto';
        this.container.style.scrollBehavior = 'smooth';
        this.container.style.webkitOverflowScrolling = 'touch';

        // Відключаємо transform
        this.track.style.transform = 'none';
        this.track.style.transition = 'none';

        // Центруємо картки
        this.centerCards();
    }

    setupDesktopLayout() {
        // Показуємо кнопки
        if (this.prevBtn) this.prevBtn.style.display = 'flex';
        if (this.nextBtn) this.nextBtn.style.display = 'flex';

        // Налаштовуємо overflow
        this.container.style.overflowX = 'hidden';

        // Активуємо transform
        this.track.style.transition = 'transform 0.3s ease';

        this.updateButtons();
        this.updatePosition(false);
    }

    centerCards() {
        if (!this.isMobile) return;

        // Центруємо картки використовуючи flexbox
        this.track.style.justifyContent = 'center';
        this.track.style.minWidth = 'calc(100% - 32px)';

        // Якщо товарів мало - центруємо їх
        if (this.cards.length <= 3) {
            this.track.style.justifyContent = 'center';
            this.track.style.gap = '20px';
        }
    }

    setupEventListeners() {
        // Кнопки навігації (тільки на desktop)
        if (!this.isMobile) {
            if (this.prevBtn) {
                this.prevBtn.addEventListener('click', () => this.goToPrev());
            }
            if (this.nextBtn) {
                this.nextBtn.addEventListener('click', () => this.goToNext());
            }
        }

        // Touch events для всіх пристроїв
        this.setupTouchEvents();

        // Resize handler
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
    }

    setupTouchEvents() {
        const element = this.isMobile ? this.container : this.track;

        // Touch events
        element.addEventListener('touchstart', (e) => this.handleTouchStart(e), { passive: false });
        element.addEventListener('touchmove', (e) => this.handleTouchMove(e), { passive: false });
        element.addEventListener('touchend', (e) => this.handleTouchEnd(e), { passive: true });

        // Mouse events для desktop
        if (!this.isMobile) {
            element.addEventListener('mousedown', (e) => this.handleMouseStart(e));
            element.addEventListener('mousemove', (e) => this.handleMouseMove(e));
            element.addEventListener('mouseup', (e) => this.handleMouseEnd(e));
            element.addEventListener('mouseleave', (e) => this.handleMouseEnd(e));

            // Cursor стилі
            element.style.cursor = 'grab';
            element.addEventListener('mousedown', () => {
                element.style.cursor = 'grabbing';
            });
            element.addEventListener('mouseup', () => {
                element.style.cursor = 'grab';
            });
        }
    }

    handleTouchStart(e) {
        this.isDragging = true;
        this.startTime = Date.now();

        const touch = e.touches ? e.touches[0] : e;
        this.startX = touch.clientX;
        this.currentX = touch.clientX;

        console.log('Touch start:', this.startX);
    }

    handleTouchMove(e) {
        if (!this.isDragging) return;

        const touch = e.touches ? e.touches[0] : e;
        this.currentX = touch.clientX;

        const deltaX = Math.abs(this.currentX - this.startX);
        const deltaY = Math.abs(touch.clientY - (e.touches?.[0]?.clientY || 0));

        // Якщо горизонтальний рух більший - блокуємо вертикальний скрол
        if (deltaX > deltaY && deltaX > 10) {
            e.preventDefault();
        }
    }

    handleTouchEnd(e) {
        if (!this.isDragging) return;

        this.isDragging = false;

        const touch = e.changedTouches ? e.changedTouches[0] : e;
        const endX = touch.clientX;
        const deltaX = this.startX - endX;
        const deltaTime = Date.now() - this.startTime;
        const distance = Math.abs(deltaX);

        console.log('Touch end - deltaX:', deltaX, 'distance:', distance, 'time:', deltaTime);

        // Умови для свайпу
        const minDistance = 30;
        const maxTime = 500;

        if (distance > minDistance && deltaTime < maxTime && !this.isMobile) {
            // Тільки на desktop реагуємо на свайпи переключенням
            if (deltaX > 0) {
                this.goToNext();
            } else {
                this.goToPrev();
            }
        }
    }

    handleMouseStart(e) {
        e.preventDefault();
        this.handleTouchStart(e);
    }

    handleMouseMove(e) {
        this.handleTouchMove(e);
    }

    handleMouseEnd(e) {
        this.handleTouchEnd(e);
    }

    goToPrev() {
        if (this.isAnimating || this.currentIndex === 0 || this.isMobile) return;

        this.currentIndex--;
        this.updatePosition();
        this.updateButtons();
        console.log('Go to prev, index:', this.currentIndex);
    }

    goToNext() {
        if (this.isAnimating || this.isMobile) return;

        const maxIndex = this.getMaxIndex();
        if (this.currentIndex >= maxIndex) return;

        this.currentIndex++;
        this.updatePosition();
        this.updateButtons();
        console.log('Go to next, index:', this.currentIndex);
    }

    getMaxIndex() {
        if (this.isMobile) return 0;

        const containerWidth = this.container.offsetWidth;
        const cardWidth = 280; // Базова ширина картки
        const gap = 20;
        const cardsToShow = Math.floor(containerWidth / (cardWidth + gap));

        return Math.max(0, this.cards.length - cardsToShow);
    }

    updatePosition(animate = true) {
        if (this.isMobile) return;

        if (animate) {
            this.isAnimating = true;
            this.track.style.transition = 'transform 0.3s ease';

            setTimeout(() => {
                this.isAnimating = false;
            }, 300);
        } else {
            this.track.style.transition = 'none';
        }

        const cardWidth = 280;
        const gap = 20;
        const translateX = -this.currentIndex * (cardWidth + gap);

        this.track.style.transform = `translateX(${translateX}px)`;
        console.log('Position updated:', translateX);
    }

    updateButtons() {
        if (this.isMobile) return;

        const maxIndex = this.getMaxIndex();

        if (this.prevBtn) {
            this.prevBtn.disabled = this.currentIndex === 0;
            this.prevBtn.style.opacity = this.currentIndex === 0 ? '0.3' : '1';
        }

        if (this.nextBtn) {
            this.nextBtn.disabled = this.currentIndex >= maxIndex;
            this.nextBtn.style.opacity = this.currentIndex >= maxIndex ? '0.3' : '1';
        }
    }

    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;

        if (wasMobile !== this.isMobile) {
            // Змінився тип пристрою - повторна ініціалізація
            this.currentIndex = 0;
            this.setupLayout();
            console.log('Device type changed, reinitializing');
        } else if (!this.isMobile) {
            // Тільки оновлюємо позицію на desktop
            this.currentIndex = Math.min(this.currentIndex, this.getMaxIndex());
            this.updatePosition(false);
            this.updateButtons();
        }
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Ініціалізація при завантаженні
document.addEventListener('DOMContentLoaded', () => {
    const carousels = document.querySelectorAll('.products-carousel');

    if (carousels.length > 0) {
        console.log(`Ініціалізуємо ${carousels.length} простих каруселей`);

        carousels.forEach((carousel, index) => {
            carousel.setAttribute('data-carousel-id', index);
            new SimpleCatalogCarousel(carousel);
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