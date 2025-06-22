// Arkuda Pellet - Допоміжні функції
// Мінімальний набір для роботи сайту

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // Простіші анімації для карток
    window.CardAnimations = {
        init: function () {
            const cards = document.querySelectorAll(
                '.capacity__stat-card, .advantages__stat-card, .advantages__type-card'
            );

            if (cards.length === 0) return;

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate');
                    }
                });
            }, { threshold: 0.1 });

            cards.forEach(card => observer.observe(card));
        }
    };

    // Мінімальна система для optimization
    window.Performance = {
        init: function () {
            // Перевіряємо prefers-reduced-motion
            if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                document.documentElement.style.setProperty('--transition-normal', '0.01ms');
                document.documentElement.style.setProperty('--transition-fast', '0.01ms');
                document.documentElement.style.setProperty('--transition-slow', '0.01ms');
            }
        }
    };

    // Ініціалізація
    window.CardAnimations.init();
    window.Performance.init();
}); 