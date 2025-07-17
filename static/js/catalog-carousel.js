// Catalog Carousel Management
class CatalogCarousel {
    constructor(carouselElement) {
        this.carousel = carouselElement;
        this.track = carouselElement.querySelector('.carousel-track');
        this.prevBtn = carouselElement.querySelector('.carousel-prev');
        this.nextBtn = carouselElement.querySelector('.carousel-next');
        this.cards = carouselElement.querySelectorAll('.product-card');

        this.currentIndex = 0;
        this.cardWidth = 280; // ширина картки + gap
        this.cardsToShow = this.calculateCardsToShow();
        this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);

        this.init();
    }

    init() {
        this.updateButtons();
        this.addEventListeners();

        // Обробка зміни розміру вікна
        window.addEventListener('resize', () => {
            this.cardsToShow = this.calculateCardsToShow();
            this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);
            this.currentIndex = Math.min(this.currentIndex, this.maxIndex);
            this.updatePosition();
            this.updateButtons();
        });
    }

    calculateCardsToShow() {
        const containerWidth = this.carousel.querySelector('.carousel-container').offsetWidth;
        const cardWidth = 280 + 16; // картка + gap
        return Math.floor(containerWidth / cardWidth);
    }

    addEventListeners() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.goToPrev());
        }

        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.goToNext());
        }

        // Підтримка свайпів на мобільних
        this.addTouchSupport();
    }

    addTouchSupport() {
        let startX = 0;
        let isDragging = false;

        this.track.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            isDragging = true;
        });

        this.track.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            e.preventDefault();
        });

        this.track.addEventListener('touchend', (e) => {
            if (!isDragging) return;

            const endX = e.changedTouches[0].clientX;
            const deltaX = startX - endX;

            if (Math.abs(deltaX) > 50) { // мінімальна відстань для свайпу
                if (deltaX > 0) {
                    this.goToNext();
                } else {
                    this.goToPrev();
                }
            }

            isDragging = false;
        });
    }

    goToPrev() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.updatePosition();
            this.updateButtons();
        }
    }

    goToNext() {
        if (this.currentIndex < this.maxIndex) {
            this.currentIndex++;
            this.updatePosition();
            this.updateButtons();
        }
    }

    updatePosition() {
        const translateX = -this.currentIndex * (this.cardWidth + 16);
        this.track.style.transform = `translateX(${translateX}px)`;
    }

    updateButtons() {
        if (this.prevBtn) {
            this.prevBtn.disabled = this.currentIndex === 0;
            this.prevBtn.style.opacity = this.currentIndex === 0 ? '0.5' : '1';
        }

        if (this.nextBtn) {
            this.nextBtn.disabled = this.currentIndex >= this.maxIndex;
            this.nextBtn.style.opacity = this.currentIndex >= this.maxIndex ? '0.5' : '1';
        }
    }
}

// Ініціалізація каруселей при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    const carousels = document.querySelectorAll('.products-carousel');

    carousels.forEach(carousel => {
        new CatalogCarousel(carousel);
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


}); 