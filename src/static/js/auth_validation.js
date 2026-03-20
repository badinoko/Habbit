document.addEventListener('DOMContentLoaded', function() {
    const authForms = document.querySelectorAll('.auth-form');

    authForms.forEach((form) => {
        const errorBox = document.querySelector('[data-auth-client-error]');
        if (!errorBox) {
            return;
        }

        function messageForField(field) {
            const validity = field.validity;

            if (validity.valueMissing) {
                return field.name === 'email' ? 'Введите email.' : 'Введите пароль.';
            }

            if (field.name === 'email' && validity.typeMismatch) {
                return 'Введите корректный email.';
            }

            if (field.name === 'password' && (validity.tooShort || validity.tooLong)) {
                return 'Пароль должен быть длиной от 8 до 256 символов.';
            }

            if (field.name === 'password' && validity.badInput) {
                return 'Проверьте корректность пароля.';
            }

            return field.validationMessage || 'Проверьте корректность введённых данных.';
        }

        function showError(message) {
            errorBox.hidden = false;
            errorBox.querySelector('[data-auth-client-error-text]').textContent = message;
        }

        function clearError() {
            errorBox.hidden = true;
            errorBox.querySelector('[data-auth-client-error-text]').textContent = '';
        }

        form.addEventListener(
            'invalid',
            function(event) {
                event.preventDefault();
                showError(messageForField(event.target));
            },
            true
        );

        form.addEventListener('submit', function(event) {
            clearError();

            if (!form.checkValidity()) {
                event.preventDefault();
                const invalidField = form.querySelector(':invalid');
                if (invalidField instanceof HTMLElement) {
                    invalidField.focus();
                    showError(messageForField(invalidField));
                }
            }
        });

        form.querySelectorAll('input').forEach((field) => {
            field.addEventListener('input', function() {
                if (form.checkValidity()) {
                    clearError();
                }
            });
        });
    });
});
