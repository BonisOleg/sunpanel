// Система зворотного зв'язку
class CallbackSystem {
    constructor() {
        this.modal = null;
        this.init();
    }

    init() {
        this.createCallButton();
        this.createModal();
        this.bindEvents();
    }

    createCallButton() {
        const button = document.createElement('button');
        button.className = 'call-button';
        button.id = 'call-button';
        button.setAttribute('aria-label', 'Зателефонувати мені');
        document.body.appendChild(button);
    }

    createModal() {
        const modalHTML = `
            <div class="callback-modal" id="callback-modal">
                <div class="callback-modal__content">
                    <button class="callback-modal__close" id="modal-close">&times;</button>
                    
                    <!-- Головне меню варіантів -->
                    <div class="callback-options-screen" id="options-screen">
                        <h2 class="callback-modal__title">Як з вами зв'язатися?</h2>
                        <div class="callback-options">
                            <div class="callback-option" data-action="contact">
                                <span class="callback-option__icon">💬</span>
                                <div class="callback-option__title">Написати нам</div>
                                <div class="callback-option__description">Отримайте нашу контактну інформацію</div>
                            </div>
                            <div class="callback-option" data-action="callback">
                                <span class="callback-option__icon">📞</span>
                                <div class="callback-option__title">Залишити заявку</div>
                                <div class="callback-option__description">Ми зателефонуємо вам протягом 15 хвилин</div>
                            </div>
                        </div>
                    </div>

                    <!-- Екран контактів -->
                    <div class="contact-info-screen" id="contact-screen" style="display: none;">
                        <button class="callback-form__back" id="back-to-options">
                            ← Назад
                        </button>
                        <h2 class="callback-modal__title">Наші контакти</h2>
                        <div class="contact-info">
                            <div class="contact-item">
                                <span class="contact-icon">📞</span>
                                <div class="contact-details">
                                    <strong>Телефони:</strong><br>
                                    <a href="tel:+380500344881">+38 (050) 034-48-81</a><br>
                                    <a href="tel:+380634952145">+38 (063) 495-21-45</a>
                                </div>
                            </div>
                            <div class="contact-item">
                                <span class="contact-icon">📧</span>
                                <div class="contact-details">
                                    <strong>Email:</strong><br>
                                    <a href="mailto:info@greensolartech.com">info@greensolartech.com</a>
                                </div>
                            </div>
                            <div class="contact-item">
                                <span class="contact-icon">📍</span>
                                <div class="contact-details">
                                    <strong>Адреса:</strong><br>
                                    Київська область, м. Київ, Україна
                                </div>
                            </div>
                            <div class="contact-item">
                                <span class="contact-icon">🕒</span>
                                <div class="contact-details">
                                    <strong>Режим роботи:</strong><br>
                                    Пн-Пт: 09:00-18:00<br>
                                    Сб: 10:00-16:00
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Форма зворотного зв'язку -->
                    <div class="callback-form" id="callback-form">
                        <button class="callback-form__back" id="back-to-options-form">
                            ← Назад
                        </button>
                        <h2 class="callback-modal__title">Залишити заявку</h2>
                        <form id="callback-form-element">
                            <div class="form-group">
                                <label for="callback-name">Ваше ім'я *</label>
                                <input type="text" id="callback-name" name="name" required>
                            </div>
                            <div class="form-group">
                                <label for="callback-phone">Номер телефону *</label>
                                <input type="tel" id="callback-phone" name="phone" required>
                            </div>
                            <div class="form-group">
                                <label for="callback-message">Повідомлення (необов'язково)</label>
                                <textarea id="callback-message" name="message" placeholder="Розкажіть про ваш проект або питання..."></textarea>
                            </div>
                            <button type="submit" class="callback-submit" id="callback-submit">
                                Відправити заявку
                            </button>
                        </form>
                    </div>

                    <!-- Повідомлення про успіх -->
                    <div class="success-message" id="success-message">
                        <div class="success-message__icon">✅</div>
                        <h2 class="success-message__title">Заявку відправлено!</h2>
                        <p class="success-message__text">
                            Дякуємо за звернення! Наш менеджер зв'яжеться з вами протягом 15 хвилин.
                        </p>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById('callback-modal');
    }

    bindEvents() {
        // Відкриття модального вікна
        document.getElementById('call-button').addEventListener('click', () => {
            this.openModal();
        });

        // Закриття модального вікна
        document.getElementById('modal-close').addEventListener('click', () => {
            this.closeModal();
        });

        // Закриття при кліку на фон
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });

        // Обробка вибору опцій
        document.querySelectorAll('.callback-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleOptionSelect(action);
            });
        });

        // Кнопки "Назад"
        document.getElementById('back-to-options').addEventListener('click', () => {
            this.showOptionsScreen();
        });

        document.getElementById('back-to-options-form').addEventListener('click', () => {
            this.showOptionsScreen();
        });

        // Обробка форми
        document.getElementById('callback-form-element').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmit(e.target);
        });

        // Закриття на Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.closeModal();
            }
        });

        // Форматування номера телефону
        document.getElementById('callback-phone').addEventListener('input', (e) => {
            this.formatPhoneNumber(e.target);
        });
    }

    openModal() {
        this.modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        this.showOptionsScreen();
    }

    closeModal() {
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
        // Ресет форми при закритті
        setTimeout(() => {
            this.resetModal();
        }, 300);
    }

    resetModal() {
        this.showOptionsScreen();
        document.getElementById('callback-form-element').reset();
        document.getElementById('callback-submit').disabled = false;
        document.getElementById('callback-submit').textContent = 'Відправити заявку';
    }

    showOptionsScreen() {
        document.getElementById('options-screen').style.display = 'block';
        document.getElementById('contact-screen').style.display = 'none';
        document.getElementById('callback-form').classList.remove('active');
        document.getElementById('success-message').classList.remove('active');
    }

    handleOptionSelect(action) {
        if (action === 'contact') {
            this.showContactInfo();
        } else if (action === 'callback') {
            this.showCallbackForm();
        }
    }

    showContactInfo() {
        document.getElementById('options-screen').style.display = 'none';
        document.getElementById('contact-screen').style.display = 'block';
    }

    showCallbackForm() {
        document.getElementById('options-screen').style.display = 'none';
        document.getElementById('callback-form').classList.add('active');
    }

    async handleFormSubmit(form) {
        const submitBtn = document.getElementById('callback-submit');
        const formData = new FormData(form);

        // Отримання CSRF токена
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            document.querySelector('meta[name="csrf-token"]')?.content;

        const data = {
            name: formData.get('name'),
            phone: formData.get('phone'),
            message: formData.get('message') || '',
            csrfmiddlewaretoken: csrfToken
        };

        // Валідація
        if (!data.name.trim()) {
            this.showError('Будь ласка, введіть ваше ім\'я');
            return;
        }

        if (!data.phone.trim()) {
            this.showError('Будь ласка, введіть номер телефону');
            return;
        }

        // Дисейбл кнопки
        submitBtn.disabled = true;
        submitBtn.textContent = 'Відправляємо...';

        try {
            const response = await fetch('/api/callback/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                this.showSuccessMessage();
            } else {
                throw new Error('Помилка сервера');
            }
        } catch (error) {
            console.error('Помилка при відправці:', error);
            this.showError('Помилка при відправці заявки. Спробуйте ще раз або зателефонуйте нам безпосередньо.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Відправити заявку';
        }
    }

    showSuccessMessage() {
        document.getElementById('callback-form').classList.remove('active');
        document.getElementById('success-message').classList.add('active');

        // Автозакриття через 5 секунд
        setTimeout(() => {
            this.closeModal();
        }, 5000);
    }

    showError(message) {
        // Створюємо тимчасове повідомлення про помилку
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = `
            background: #f44336;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            font-size: 14px;
            animation: slideIn 0.3s ease;
        `;
        errorDiv.textContent = message;

        const form = document.getElementById('callback-form-element');
        const existingError = form.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        form.insertBefore(errorDiv, form.firstChild);

        // Видаляємо повідомлення через 5 секунд
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    formatPhoneNumber(input) {
        let value = input.value.replace(/\D/g, '');

        // Додаємо +38 якщо немає
        if (value.length > 0 && !value.startsWith('38')) {
            if (value.startsWith('0')) {
                value = '38' + value;
            } else if (!value.startsWith('38')) {
                value = '38' + value;
            }
        }

        // Форматування
        if (value.length >= 2) {
            let formatted = '+' + value.substring(0, 2);
            if (value.length > 2) {
                formatted += ' (' + value.substring(2, 5);
                if (value.length > 5) {
                    formatted += ') ' + value.substring(5, 8);
                    if (value.length > 8) {
                        formatted += '-' + value.substring(8, 10);
                        if (value.length > 10) {
                            formatted += '-' + value.substring(10, 12);
                        }
                    }
                }
            }
            input.value = formatted;
        }
    }
}

// Додаткові стилі для контактної інформації
const contactStyles = `
.contact-info {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.contact-item {
    display: flex;
    align-items: flex-start;
    gap: 15px;
    padding: 15px;
    background: #f9f9f9;
    border-radius: 10px;
}

.contact-icon {
    font-size: 24px;
    flex-shrink: 0;
}

.contact-details {
    line-height: 1.5;
}

.contact-details a {
    color: #4CAF50;
    text-decoration: none;
}

.contact-details a:hover {
    text-decoration: underline;
}

.error-message {
    background: #f44336;
    color: white;
    padding: 10px 15px;
    border-radius: 5px;
    margin-bottom: 15px;
    font-size: 14px;
    animation: slideIn 0.3s ease;
}

@media (max-width: 768px) {
    .contact-item {
        gap: 12px;
        padding: 12px;
    }
    
    .contact-icon {
        font-size: 20px;
    }
}
`;

// Додаємо стилі до сторінки
const style = document.createElement('style');
style.textContent = contactStyles;
document.head.appendChild(style);

// Ініціалізуємо систему після завантаження DOM
document.addEventListener('DOMContentLoaded', () => {
    window.callbackSystem = new CallbackSystem();
}); 