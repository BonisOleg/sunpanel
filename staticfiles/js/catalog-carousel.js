// Проста карусель - на мобільних нативний скрол, на desktop - кнопки
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

        this.init();
    }

    init() {
        if (this.cards.length === 0) return;

        // На мобільних - нічого не робимо, тільки нативний скрол
        if (this.isMobile) {
            console.log('Mobile detected - using native scroll only');
            return;
        }

        // На desktop - налаштовуємо кнопки
        this.setupDesktop();
    }

    setupDesktop() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.goToPrev());
        }
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.goToNext());
        }

        this.updateButtons();

        // Resize handler
        window.addEventListener('resize', () => {
            const wasMobile = this.isMobile;
            this.isMobile = window.innerWidth <= 768;

            if (wasMobile !== this.isMobile && this.isMobile) {
                // Стали мобільними - перезавантажуємо сторінку для простоти
                location.reload();
            }
        });

        console.log('Desktop carousel setup complete');
    }

    goToPrev() {
        if (this.currentIndex === 0) return;
        this.currentIndex--;
        this.updatePosition();
        this.updateButtons();
    }

    goToNext() {
        const maxIndex = this.getMaxIndex();
        if (this.currentIndex >= maxIndex) return;
        this.currentIndex++;
        this.updatePosition();
        this.updateButtons();
    }

    getMaxIndex() {
        const containerWidth = this.container.offsetWidth;
        const cardWidth = 300; // Ширина картки + gap
        const cardsToShow = Math.floor(containerWidth / cardWidth);
        return Math.max(0, this.cards.length - cardsToShow);
    }

    updatePosition() {
        const cardWidth = 300;
        const translateX = -this.currentIndex * cardWidth;
        this.track.style.setProperty('--carousel-translate-x', `${translateX}px`);
    }

    updateButtons() {
        const maxIndex = this.getMaxIndex();

        if (this.prevBtn) {
            this.prevBtn.disabled = this.currentIndex === 0;
        }

        if (this.nextBtn) {
            this.nextBtn.disabled = this.currentIndex >= maxIndex;
        }
    }
}

// Ініціалізація
document.addEventListener('DOMContentLoaded', () => {
    const carousels = document.querySelectorAll('.products-carousel');

    carousels.forEach((carousel) => {
        new SimpleCatalogCarousel(carousel);
    });

    console.log(`Initialized ${carousels.length} carousels`);

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