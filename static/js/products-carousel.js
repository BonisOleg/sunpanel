// Products Carousel - Unified Logic for All Devices
document.addEventListener('DOMContentLoaded', function () {
    const carousel = document.querySelector('.products__grid');

    if (!carousel) return;

    let isDown = false;
    let startX;
    let scrollLeft;

    // Mouse drag events
    carousel.addEventListener('mousedown', (e) => {
        isDown = true;
        carousel.classList.add('active');
        startX = e.pageX - carousel.offsetLeft;
        scrollLeft = carousel.scrollLeft;
        e.preventDefault();
    });

    carousel.addEventListener('mouseleave', () => {
        isDown = false;
        carousel.classList.remove('active');
    });

    carousel.addEventListener('mouseup', () => {
        isDown = false;
        carousel.classList.remove('active');
    });

    carousel.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - carousel.offsetLeft;
        const walk = (x - startX) * 1.5;
        carousel.scrollLeft = scrollLeft - walk;
    });

    // Touch drag events
    let touchStartX = 0;
    let touchScrollLeft = 0;

    carousel.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
        touchScrollLeft = carousel.scrollLeft;
    }, { passive: true });

    carousel.addEventListener('touchmove', (e) => {
        if (!touchStartX) return;
        const touchX = e.touches[0].clientX;
        const walk = (touchStartX - touchX) * 1.2;
        carousel.scrollLeft = touchScrollLeft + walk;
    }, { passive: true });

    carousel.addEventListener('touchend', () => {
        touchStartX = 0;
    });

    // Unified scale and opacity effect - same for all devices
    function updateCardsScale() {
        const cards = carousel.querySelectorAll('.product-card');
        const carouselRect = carousel.getBoundingClientRect();
        const carouselCenter = carouselRect.left + carouselRect.width / 2;

        // Check scroll position
        const scrollLeft = carousel.scrollLeft;
        const maxScrollLeft = carousel.scrollWidth - carousel.clientWidth;
        const isAtLeftEdge = scrollLeft <= 20;
        const isAtRightEdge = scrollLeft >= maxScrollLeft - 20;

        let activeCardIndex = -1;
        let minDistance = Infinity;

        // Find the card closest to center (for middle positions)
        cards.forEach((card, index) => {
            const cardRect = card.getBoundingClientRect();
            const cardCenter = cardRect.left + cardRect.width / 2;
            const distance = Math.abs(carouselCenter - cardCenter);

            if (distance < minDistance) {
                minDistance = distance;
                activeCardIndex = index;
            }
        });

        // Override active card for edge positions
        if (isAtLeftEdge) {
            activeCardIndex = 0; // First card when at left edge
        } else if (isAtRightEdge) {
            activeCardIndex = cards.length - 1; // Last card when at right edge
        }

        // Apply scaling to all cards
        cards.forEach((card, index) => {
            let scale, opacity, zIndex;

            if (index === activeCardIndex) {
                // Active card gets max scale
                scale = 1.1;
                opacity = 1.0;
                zIndex = 10;
            } else {
                // Calculate distance from active card for smooth transition
                const distanceFromActive = Math.abs(index - activeCardIndex);
                const normalizedDistance = Math.min(distanceFromActive / 2, 1);
                scale = 1.1 - (normalizedDistance * 0.3); // 1.1 to 0.8
                opacity = 1 - (normalizedDistance * 0.4); // 1.0 to 0.6
                zIndex = 1;
            }

            // Apply consistent transform for all devices
            card.style.transform = `scale(${Math.max(0.8, scale)})`;
            card.style.opacity = Math.max(0.6, opacity);
            card.style.zIndex = zIndex;
        });
    }

    // Update scale on scroll
    carousel.addEventListener('scroll', updateCardsScale);

    // Initial scale update
    setTimeout(updateCardsScale, 100);

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (!carousel.matches(':hover')) return;

        if (e.key === 'ArrowLeft') {
            carousel.scrollBy({ left: -320, behavior: 'smooth' });
            e.preventDefault();
        } else if (e.key === 'ArrowRight') {
            carousel.scrollBy({ left: 320, behavior: 'smooth' });
            e.preventDefault();
        }
    });
}); 