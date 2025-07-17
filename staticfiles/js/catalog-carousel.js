// Catalog Carousel Management - покращена версія
class CatalogCarousel {
    constructor(carouselElement) {
        this.carousel = carouselElement;
        this.container = carouselElement.querySelector('.carousel-container');
        this.track = carouselElement.querySelector('.carousel-track');
        this.prevBtn = carouselElement.querySelector('.carousel-prev');
        this.nextBtn = carouselElement.querySelector('.carousel-next');
        this.cards = carouselElement.querySelectorAll('.product-card');

        this.currentIndex = 0;
        this.cardWidth = 280;
        this.gap = 16;
        this.cardsToShow = this.calculateCardsToShow();
        this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);
        this.isMobile = window.innerWidth <= 768;

        this.init();
    }

    init() {
        // Для мобільних пристроїв використовуємо нативний скрол
        if (this.isMobile) {
            this.initMobileScroll();
        } else {
            this.initDesktopCarousel();
        }

        // Обробка зміни розміру вікна
        window.addEventListener('resize', () => {
            const wasMobile = this.isMobile;
            this.isMobile = window.innerWidth <= 768;

            if (wasMobile !== this.isMobile) {
                // Переключення між мобільним та десктопним режимами
                if (this.isMobile) {
                    this.initMobileScroll();
                } else {
                    this.initDesktopCarousel();
                }
            } else if (!this.isMobile) {
                // Оновлення параметрів для десктопу
                this.updateDesktopParams();
            }
        });
    }

    initMobileScroll() {
        // Скидаємо transform для мобільних
        this.track.style.transform = '';

        // Приховуємо кнопки навігації
        if (this.prevBtn) this.prevBtn.style.display = 'none';
        if (this.nextBtn) this.nextBtn.style.display = 'none';

        // Додаємо smooth scrolling для мобільних
        this.container.style.scrollBehavior = 'smooth';
    }

    initDesktopCarousel() {
        // Показуємо кнопки навігації
        if (this.prevBtn) this.prevBtn.style.display = 'flex';
        if (this.nextBtn) this.nextBtn.style.display = 'flex';

        // Скидаємо scroll для десктопу
        this.container.scrollLeft = 0;
        this.container.style.scrollBehavior = 'auto';

        this.updateDesktopParams();
        this.addEventListeners();
        this.updatePosition();
        this.updateButtons();
    }

    updateDesktopParams() {
        this.cardsToShow = this.calculateCardsToShow();
        this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);
        this.currentIndex = Math.min(this.currentIndex, this.maxIndex);
    }

    calculateCardsToShow() {
        if (this.isMobile) return 1;

        const containerWidth = this.container.offsetWidth;
        const cardTotalWidth = this.cardWidth + this.gap;
        return Math.floor(containerWidth / cardTotalWidth);
    }

    addEventListeners() {
        if (this.isMobile) return;

        // Видаляємо старі слухачі подій
        if (this.prevBtn) {
            this.prevBtn.removeEventListener('click', this.goToPrevBound);
            this.goToPrevBound = () => this.goToPrev();
            this.prevBtn.addEventListener('click', this.goToPrevBound);
        }

        if (this.nextBtn) {
            this.nextBtn.removeEventListener('click', this.goToNextBound);
            this.goToNextBound = () => this.goToNext();
            this.nextBtn.addEventListener('click', this.goToNextBound);
        }

        // Підтримка клавіатури
        this.carousel.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                this.goToPrev();
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                this.goToNext();
            }
        });

        // Додаємо можливість фокусування для клавіатури
        this.carousel.setAttribute('tabindex', '0');
    }

    goToPrev() {
        if (this.isMobile || this.currentIndex <= 0) return;

        this.currentIndex--;
        this.updatePosition();
        this.updateButtons();
    }

    goToNext() {
        if (this.isMobile || this.currentIndex >= this.maxIndex) return;

        this.currentIndex++;
        this.updatePosition();
        this.updateButtons();
    }

    updatePosition() {
        if (this.isMobile) return;

        const translateX = -this.currentIndex * (this.cardWidth + this.gap);
        this.track.style.transform = `translateX(${translateX}px)`;
    }

    updateButtons() {
        if (this.isMobile) return;

        if (this.prevBtn) {
            this.prevBtn.disabled = this.currentIndex === 0;
        }

        if (this.nextBtn) {
            this.nextBtn.disabled = this.currentIndex >= this.maxIndex;
        }
    }
}

// Ініціалізація каруселей при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    const carousels = document.querySelectorAll('.products-carousel');

    carousels.forEach(carousel => {
        // Додаємо невелику затримку для кращої ініціалізації
        setTimeout(() => {
            new CatalogCarousel(carousel);
        }, 100);
    });

    // Автоматичне застосування фільтрів при зміні
    const filterForm = document.getElementById('filters-form');
    if (filterForm) {
        const filterElements = filterForm.querySelectorAll('.filter-select, .price-input');

        filterElements.forEach(element => {
            element.addEventListener('change', () => {
                filterForm.submit();
            });
        });
    }

    // Покращення UX для touch пристроїв
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
    }
}); 