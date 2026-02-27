window.addEventListener('pageshow', function(event) {
    initializeFormHandlers();
});

function initializeFormHandlers() {
    // Обработка выбора типа цели для привычек
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(btn => {
        btn.disabled = false;
        btn.classList.remove('btn-loading');
    });

    const goalTypeSelect = document.getElementById('goal_type');
    const goalValueContainer = document.getElementById('goal-value-container');

    if (goalTypeSelect && goalValueContainer) {
        goalTypeSelect.addEventListener('change', function() {
            if (this.value === 'completion') {
                goalValueContainer.style.display = 'none';
            } else {
                goalValueContainer.style.display = 'block';

                // Обновляем placeholder в зависимости от типа цели
                const goalValueInput = document.getElementById('goal_value');
                if (this.value === 'duration') {
                    goalValueInput.placeholder = 'Например: 30 (минут)';
                } else if (this.value === 'quantity') {
                    goalValueInput.placeholder = 'Например: 5 (раз)';
                }
            }
        });
    }

    // Валидация формы при отправке
    const forms = document.querySelectorAll('.item-form');
    forms.forEach(form => {
        // PUT-формы обрабатываются в update.js, чтобы избежать двойного submit flow
        const method = (form.dataset.method || form.getAttribute('method') || 'post').toLowerCase();
        if (method === 'put') {
            return;
        }

        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showFormError('Пожалуйста, заполните все обязательные поля правильно.');
            } else {
                // Показываем loading состояние
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.classList.add('btn-loading');
                    submitBtn.disabled = true;
                }
            }
        });
    });

    // Валидация полей при изменении
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });

        input.addEventListener('input', function() {
            // Убираем ошибку при вводе
            const errorElement = this.parentNode.querySelector('.field-error');
            if (errorElement && this.value.trim()) {
                errorElement.remove();
                this.classList.remove('error');
            }
        });
    });

    // Инициализация подсказок
    initializeFieldHints();
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });

    // Специфичная валидация для привычек (дни недели)
    const scheduleCheckboxes = form.querySelectorAll('input[name="schedule"]:checked');
    if (scheduleCheckboxes.length === 0 && form.action.includes('/new/habit')) {
        const daysSelector = form.querySelector('.days-selector');
        showFieldError(daysSelector, 'Выберите хотя бы один день');
        isValid = false;
    }

    return isValid;
}

function validateField(field) {
    const errorElement = field.parentNode.querySelector('.field-error');

    // Убираем предыдущую ошибку
    if (errorElement) {
        errorElement.remove();
    }

    field.classList.remove('error');

    // Проверка обязательных полей
    if (field.hasAttribute('required') && !field.value.trim()) {
        showFieldError(field, 'Заполните все обязательные поля');
        return false;
    }

    // Проверка email
    if (field.type === 'email' && field.value && !isValidEmail(field.value)) {
        showFieldError(field, 'Введите корректный email');
        return false;
    }

    // Проверка числовых полей
    if (field.type === 'number') {
        const min = field.getAttribute('min');
        const max = field.getAttribute('max');

        if (min && field.value && parseInt(field.value) < parseInt(min)) {
            showFieldError(field, `Значение должно быть не меньше ${min}`);
            return false;
        }

        if (max && field.value && parseInt(field.value) > parseInt(max)) {
            showFieldError(field, `Значение должно быть не больше ${max}`);
            return false;
        }
    }

    return true;
}

function showFieldError(field, message) {
    field.classList.add('error');

    const errorElement = document.createElement('div');
    errorElement.className = 'field-error';
    errorElement.textContent = message;

    field.parentNode.appendChild(errorElement);
}

function showFormError(message) {
    // Удаляем предыдущие ошибки
    const existingErrors = document.querySelectorAll('.form-error');
    existingErrors.forEach(error => error.remove());

    const errorElement = document.createElement('div');
    errorElement.className = 'form-error';
    errorElement.textContent = message;

    const form = document.querySelector('.item-form');
    form.insertBefore(errorElement, form.firstChild);

    // Прокрутка к ошибке
    errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function initializeFieldHints() {
    // Добавляем подсказки для полей
    const fieldsWithHints = {
        'target': 'Сколько раз в день вы планируете выполнять эту привычку?',
        'frequency': 'Как часто вы будете отслеживать выполнение привычки?',
        'priority': 'Высокий приоритет для срочных и важных задач',
        'due_date': 'Установите реалистичный срок выполнения'
    };

    for (const [fieldId, hint] of Object.entries(fieldsWithHints)) {
        const field = document.getElementById(fieldId);
        if (field) {
            addFieldHint(field, hint);
        }
    }
}

function addFieldHint(field, hint) {
    const hintElement = document.createElement('div');
    hintElement.className = 'field-hint';
    hintElement.textContent = hint;

    field.parentNode.appendChild(hintElement);

    // Показываем/скрываем подсказку при фокусе
    field.addEventListener('focus', function() {
        hintElement.style.display = 'block';
    });

    field.addEventListener('blur', function() {
        hintElement.style.display = 'none';
    });

    hintElement.style.display = 'none';
}
