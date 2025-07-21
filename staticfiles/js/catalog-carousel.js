// Каталог Карусель з чистим CSS підходом без інлайн стилів
class CatalogCarousel {
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

        // Touch змінні для desktop
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
            this.setupMobileLayout();
        } else {
            this.setupDesktopLayout();
        }
    }

    setupMobileLayout() {
        // Додаємо мобільні класи
        this.carousel.classList.add('mobile-mode');
        this.carousel.classList.remove('desktop-mode');

        if (this.container) {
            this.container.classList.add('mobile-mode');
            this.container.classList.remove('desktop-mode');
        }

        if (this.track) {
            this.track.classList.add('mobile-mode');
            this.track.classList.remove('desktop-mode');
        }

        // Додаємо мобільні класи до кнопок
        if (this.prevBtn) {
            this.prevBtn.classList.add('mobile-mode');
            this.prevBtn.classList.remove('desktop-mode');
        }

        if (this.nextBtn) {
            this.nextBtn.classList.add('mobile-mode');
            this.nextBtn.classList.remove('desktop-mode');
        }

        // Додаємо scroll snap до карток через CSS клас
        this.cards.forEach(card => {
            card.classList.add('mobile-snap');
        });

        console.log('Mobile layout setup complete with CSS classes');
    }

    setupDesktopLayout() {
        // Додаємо desktop класи
        this.carousel.classList.add('desktop-mode');
        this.carousel.classList.remove('mobile-mode');

        if (this.container) {
            this.container.classList.add('desktop-mode');
            this.container.classList.remove('mobile-mode');
        }

        if (this.track) {
            this.track.classList.add('desktop-mode');
            this.track.classList.remove('mobile-mode');
        }

        // Додаємо desktop класи до кнопок
        if (this.prevBtn) {
            this.prevBtn.classList.add('desktop-mode');
            this.prevBtn.classList.remove('mobile-mode');
        }

        if (this.nextBtn) {
            this.nextBtn.classList.add('desktop-mode');
            this.nextBtn.classList.remove('mobile-mode');
        }

        // Прибираємо мобільні класи з карток
        this.cards.forEach(card => {
            card.classList.remove('mobile-snap');
        });

        this.updateButtons();
        this.updatePosition(false);

        console.log('Desktop layout setup complete with CSS classes');
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

        // Touch events
        if (this.isMobile) {
            this.setupMobileTouchEvents();
        } else {
            this.setupDesktopTouchEvents();
        }

        // Resize handler
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
    }

    setupMobileTouchEvents() {
        // На мобільних використовуємо нативний скрол без додаткової логіки
        // Браузер сам керує тач-подіями для скролу

        this.container.addEventListener('scroll', () => {
            this.updateMobileScrollPosition();
        }, { passive: true });

        // Мінімальна логіка тач-подій для відслідковування
        this.container.addEventListener('touchstart', (e) => {
            this.startX = e.touches[0].clientX;
        }, { passive: true });

        console.log('Mobile touch events setup complete - using native scroll');
    }

    setupDesktopTouchEvents() {
        // Touch events для desktop
        this.track.addEventListener('touchstart', (e) => this.handleTouchStart(e), { passive: false });
        this.track.addEventListener('touchmove', (e) => this.handleTouchMove(e), { passive: false });
        this.track.addEventListener('touchend', (e) => this.handleTouchEnd(e), { passive: true });

        // Mouse events для desktop
        this.track.addEventListener('mousedown', (e) => this.handleMouseStart(e));
        this.track.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.track.addEventListener('mouseup', (e) => this.handleMouseEnd(e));
        this.track.addEventListener('mouseleave', (e) => this.handleMouseEnd(e));

        // Cursor через CSS клас
        this.track.classList.add('draggable-cursor');

        console.log('Desktop touch events setup complete');
    }

    updateMobileScrollPosition() {
        // Дебаунс для оптимізації
        if (this.scrollTimeout) {
            clearTimeout(this.scrollTimeout);
        }

        this.scrollTimeout = setTimeout(() => {
            console.log('Mobile scroll position updated');
        }, 100);
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

        // Запобігання скролу сторінки під час горизонтального свайпу
        if (deltaX > 10) {
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

        // Умови для свайпу (тільки на desktop)
        const minDistance = 50;
        const maxTime = 500;

        if (distance > minDistance && deltaTime < maxTime && !this.isMobile) {
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
        this.track.classList.add('grabbing-cursor');
    }

    handleMouseMove(e) {
        this.handleTouchMove(e);
    }

    handleMouseEnd(e) {
        this.handleTouchEnd(e);
        this.track.classList.remove('grabbing-cursor');
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
        const cardWidth = 280;
        const gap = 20;
        const cardsToShow = Math.floor(containerWidth / (cardWidth + gap));

        return Math.max(0, this.cards.length - cardsToShow);
    }

    updatePosition(animate = true) {
        if (this.isMobile) return;

        if (animate) {
            this.isAnimating = true;
            this.track.classList.add('animating');

            setTimeout(() => {
                this.isAnimating = false;
                this.track.classList.remove('animating');
            }, 300);
        }

        const cardWidth = 280;
        const gap = 20;
        const translateX = -this.currentIndex * (cardWidth + gap);

        // Використовуємо CSS custom property замість inline стилю
        this.track.style.setProperty('--carousel-translate-x', `${translateX}px`);
        console.log('Position updated:', translateX);
    }

    updateButtons() {
        if (this.isMobile) return;

        const maxIndex = this.getMaxIndex();

        if (this.prevBtn) {
            this.prevBtn.disabled = this.currentIndex === 0;
            if (this.currentIndex === 0) {
                this.prevBtn.classList.add('disabled');
            } else {
                this.prevBtn.classList.remove('disabled');
            }
        }

        if (this.nextBtn) {
            this.nextBtn.disabled = this.currentIndex >= maxIndex;
            if (this.currentIndex >= maxIndex) {
                this.nextBtn.classList.add('disabled');
            } else {
                this.nextBtn.classList.remove('disabled');
            }
        }
    }

    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;

        if (wasMobile !== this.isMobile) {
            // Змінився тип пристрою - повторна ініціалізація
            this.currentIndex = 0;
            this.setupLayout();
            console.log('Device type changed, reinitializing. New mobile status:', this.isMobile);
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
        console.log(`Ініціалізуємо ${carousels.length} чистих CSS каруселей`);

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