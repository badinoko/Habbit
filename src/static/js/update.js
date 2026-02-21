document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.item-form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            // Собираем данные формы
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            // Убеждаемся, что выбранный цвет включен в данные
            const selectedColor = document.querySelector('input[name="color"]:checked');
            if (!data.color && selectedColor) {
                data.color = selectedColor.value;
            }

            const method = form.dataset.method || form.getAttribute('method') || 'post';
            const action = form.getAttribute('action');

            if (method.toLowerCase() === 'put') {
                updateFormData(form, data, action);
            } else {
                form.submit();
            }
        });
    });
});

function updateFormData(form, data, url) {
    fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.text().then(text => {
                throw new Error(`HTTP error! status: ${response.status}, body: ${text}`);
            });
        }
    })
    .then(data => {
        console.log('Данные успешно обновлены:', data);
        showNotification('Изменения сохранены успешно!', 'success');
        const currentPath = window.location.pathname;

        if (currentPath.startsWith('/tasks')) {
            window.location.href = '/tasks';
        } else if (currentPath.startsWith('/themes')) {
            window.location.href = '/themes';
        } else {
            console.warn('Неизвестный путь для редиректа');
            // Можно добавить fallback редирект
            // window.location.href = '/';
        }
    })
    .catch(error => {
        console.error('Ошибка при обновлении:', error);
        showNotification('Ошибка при сохранении изменений', 'error');
    });
}

// Функция показа уведомлений
function showNotification(message, type = 'info') {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;

    // Добавляем в начало формы
    const form = document.querySelector('.item-form');
    form.parentNode.insertBefore(notification, form);

    // Удаляем через 3 секунды
    setTimeout(() => {
        notification.remove();
    }, 3000);
}
