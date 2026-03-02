let activeTasksCount = 0; // глобальная переменная для счётчика

// Базовые функции для взаимодействия
document.addEventListener('DOMContentLoaded', function() {
    // Считываем начальное значение активных задач
    const activeEl = document.getElementById('stat-active-tasks');
    if (activeEl) {
        activeTasksCount = parseInt(activeEl.textContent, 10) || 0;
    }

    initializeTaskStates(); // Инициализируем состояние выполненных задач
    initializeEventHandlers();
    addNotificationStyles();
});

function isTaskCompletedValue(completedAt) {
    return Boolean(completedAt && completedAt !== 'None' && completedAt !== '' && completedAt !== 'null');
}

// Функция для инициализации состояния выполненных задач при загрузке страницы
function initializeTaskStates() {
    const taskItems = document.querySelectorAll('.task-item');
    taskItems.forEach(taskItem => {
        const completedAt = taskItem.dataset.completed;
        const isCompleted = isTaskCompletedValue(completedAt);

        if (isCompleted) {
            // Задача выполнена – оставляем data-completed как есть
            const checkbox = taskItem.querySelector('.task-checkbox input[type="checkbox"]');
            if (checkbox) checkbox.checked = true;
            const taskTitle = taskItem.querySelector('.task-title');
            if (taskTitle) taskTitle.classList.add('completed');
        } else {
            // Задача активна – приводим data-completed к пустой строке
            taskItem.dataset.completed = '';
            const checkbox = taskItem.querySelector('.task-checkbox input[type="checkbox"]');
            if (checkbox) checkbox.checked = false;
            const taskTitle = taskItem.querySelector('.task-title');
            if (taskTitle) taskTitle.classList.remove('completed');
        }
    });
}

function initializeEventHandlers() {
    // Обработка чекбоксов задач
    const taskCheckboxes = document.querySelectorAll('.task-checkbox input[type="checkbox"]');
    taskCheckboxes.forEach(checkbox => {
        if (checkbox.dataset.boundToggle === '1') {
            return;
        }
        checkbox.dataset.boundToggle = '1';

        checkbox.addEventListener('change', function() {
            const taskItem = this.closest('.task-item');
            const taskId = this.dataset.taskId || taskItem.dataset.taskId;

            markTaskAsCompleted(taskId, this, taskItem);
        });
    });

    // Обработка кнопок привычек
    const habitButtons = document.querySelectorAll('.btn-habit-complete:not(.completed):not([disabled])');
    habitButtons.forEach(button => {
        if (button.dataset.boundHabitComplete === '1') {
            return;
        }
        button.dataset.boundHabitComplete = '1';

        button.addEventListener('click', function() {
            const habitId = this.dataset.habitId ||
                           this.id.replace('habit-', '') ||
                           this.closest('.habit-card')?.dataset.habitId;
            if (!habitId) {
                showNotification('Модуль привычек пока в разработке', 'info');
                return;
            }
            markHabitAsCompleted(habitId, this);
        });
    });

    // Редактирование и удаление
    initializeEditDeleteHandlers();
}


async function markTaskAsCompleted(taskId, checkbox, taskItem) {
    const checkedNow = checkbox.checked;
    const previousChecked = !checkedNow;

    try {
        showLoading(checkbox);

        // Выбираем endpoint в зависимости от того, становится ли задача выполненной или нет
        const endpoint = checkedNow ? `/tasks/${taskId}/complete` : `/tasks/${taskId}/incomplete`;

        const response = await fetch(endpoint, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });

        const data = await response.json();

        if (data.success) {
            // После успеха определяем новое состояние (по ответу сервера)
            // Сервер может вернуть completed_at или просто completed: true/false
            const isCompleted = data.completed || (data.completed_at && data.completed_at !== '');

            // Обновляем data-атрибут
            if (isCompleted) {
                taskItem.dataset.completed = data.completed_at || new Date().toISOString();
            } else {
                taskItem.dataset.completed = '';
            }

            // Визуальные изменения
            if (isCompleted) {
                taskItem.classList.add('completed');
                const taskTitle = taskItem.querySelector('.task-title');
                if (taskTitle) taskTitle.classList.add('completed');
                showNotification('Задача выполнена!', 'success');
                // Уменьшаем счётчик активных задач
                activeTasksCount = Math.max(0, activeTasksCount - 1);
            } else {
                taskItem.classList.remove('completed');
                const taskTitle = taskItem.querySelector('.task-title');
                if (taskTitle) taskTitle.classList.remove('completed');
                showNotification('Задача возвращена в активные', 'info');
                // Увеличиваем счётчик активных задач
                activeTasksCount += 1;
            }

            // Синхронизируем чекбокс (на случай, если сервер вернул иное)
            checkbox.checked = isCompleted;

            // Обновляем отображение статистики
            const activeEl = document.getElementById('stat-active-tasks');
            if (activeEl) activeEl.textContent = activeTasksCount;

        } else {
            // Ошибка сервера – откатываем чекбокс
            checkbox.checked = previousChecked;
            showNotification(data.error || 'Ошибка при обновлении задачи', 'error');
        }
    } catch (error) {
        console.error('Error toggling task:', error);
        checkbox.checked = previousChecked;
        showNotification('Ошибка соединения с сервером', 'error');
    } finally {
        hideLoading(checkbox);
    }
}

async function markHabitAsCompleted(habitId, button) {
    const habitCard = button.closest('.habit-card');
    if (!habitCard || !habitId) {
        showNotification('Модуль привычек пока в разработке', 'info');
        return;
    }

    const streakElement = habitCard.querySelector('.habit-streak');
    const currentStreak = streakElement ? parseInt(streakElement.textContent) || 0 : 0;

    // Сохраняем исходное состояние
    const originalText = button.innerHTML;
    const originalClass = button.className;
    const originalBgColor = button.style.backgroundColor;

    try {
        // Показываем загрузку
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обработка...';

        const response = await fetch(`/api/habits/${habitId}/complete`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });

        const data = await response.json();

        if (data.success) {
            // Визуальное подтверждение
            button.innerHTML = '<i class="fas fa-check"></i> Выполнено!';
            button.classList.add('completed');
            button.style.backgroundColor = '#27ae60';

            // Обновляем серию если есть элемент
            if (streakElement && data.new_streak) {
                streakElement.textContent = data.new_streak + ' дней';
            } else if (streakElement) {
                streakElement.textContent = (currentStreak + 1) + ' дней';
            }

            showNotification('Привычка отмечена как выполненная!', 'success');

            // Через секунду делаем кнопку неактивной
            setTimeout(() => {
                button.disabled = true;
                button.title = 'Уже выполнено сегодня';
            }, 1000);

        } else {
            // Возвращаем исходное состояние
            button.innerHTML = originalText;
            button.className = originalClass;
            button.style.backgroundColor = originalBgColor;
            button.disabled = false;

            showNotification(data.error || 'Ошибка при выполнении привычки', 'error');
        }
    } catch (error) {
        console.error('Error marking habit as completed:', error);

        // Возвращаем исходное состояние
        button.innerHTML = originalText;
        button.className = originalClass;
        button.style.backgroundColor = originalBgColor;
        button.disabled = false;

        showNotification('Ошибка соединения с сервером', 'error');
    }
}

// Функция для удаления задачи (добавлена для кнопок удаления в tasks_list.html)
async function deleteTask(taskId) {
    if (!confirm('Вы уверены, что хотите удалить эту задачу?')) return;

    const taskItem = document.querySelector(`[data-task-id="${taskId}"]`);
    const wasActive = taskItem && (!taskItem.dataset.completed || taskItem.dataset.completed === '');

    try {
        if (taskItem) {
            taskItem.style.opacity = '0.5';
            taskItem.style.pointerEvents = 'none';
        }

        const response = await fetch(`/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });

        if (response.ok) { // или response.status === 200
            showNotification('Задача удалена', 'success');

            if (taskItem) {
                taskItem.remove();
                if (wasActive) {
                    activeTasksCount--;
                    const activeEl = document.getElementById('stat-active-tasks');
                    if (activeEl) activeEl.textContent = activeTasksCount;
                }
            }

        } else {
            showNotification('Ошибка при удалении задачи', 'error');
            if (taskItem) {
                taskItem.style.opacity = '';
                taskItem.style.pointerEvents = '';
            }
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showNotification('Ошибка соединения с сервером', 'error');
        if (taskItem) {
            taskItem.style.opacity = '';
            taskItem.style.pointerEvents = '';
        }
    }
}

// Вспомогательные функции
function showLoading(element) {
    const spinner = document.createElement('span');
    spinner.className = 'loading-spinner';
    spinner.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    if (element.parentElement) {
        element.parentElement.appendChild(spinner);
    }

    element.disabled = true;
}

function hideLoading(element) {
    const spinner = element.parentElement.querySelector('.loading-spinner');
    if (spinner) {
        spinner.remove();
    }

    element.disabled = false;
}

function showNotification(message, type = 'info') {
    // Проверяем, есть ли уже контейнер для уведомлений
    let container = document.querySelector('.notification-container');

    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
    }

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
        </div>
        <div class="notification-content">${message}</div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(notification);

    // Автоматическое удаление через 5 секунд
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

function getCsrfToken() {
    // Django CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        return csrfToken.value;
    }

    // Meta tag CSRF token
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        return metaToken.getAttribute('content');
    }

    // Flask WTForms CSRF token
    const flaskToken = document.querySelector('[name="csrf_token"]');
    if (flaskToken) {
        return flaskToken.value;
    }

    // Input hidden CSRF token
    const inputToken = document.querySelector('input[name="_csrf_token"]');
    if (inputToken) {
        return inputToken.value;
    }

    console.warn('CSRF token not found!');
    return '';
}

function initializeEditDeleteHandlers() {
    // Обработчики для кнопок удаления (редактирование остаётся на обычных ссылках)
    const deleteButtons = document.querySelectorAll('.btn-task-delete');
    deleteButtons.forEach(button => {
        if (button.dataset.boundDeleteTask === '1') {
            return;
        }
        button.dataset.boundDeleteTask = '1';

        // Удаляем старый обработчик onclick, если он есть
        button.removeAttribute('onclick');

        button.addEventListener('click', function() {
            const taskId = this.dataset.taskId || this.closest('.task-item').dataset.taskId;
            if (taskId) {
                deleteTask(taskId);
            }
        });
    });
}

function addNotificationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .notification-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 350px;
        }

        .notification {
            background: white;
            border-radius: 8px;
            padding: 15px 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 15px;
            animation: slideIn 0.3s ease-out;
            border-left: 4px solid;
        }

        .notification-success {
            border-left-color: #2ecc71;
        }

        .notification-error {
            border-left-color: #e74c3c;
        }

        .notification-warning {
            border-left-color: #f39c12;
        }

        .notification-info {
            border-left-color: #3498db;
        }

        .notification-icon {
            font-size: 1.2rem;
        }

        .notification-success .notification-icon {
            color: #2ecc71;
        }

        .notification-error .notification-icon {
            color: #e74c3c;
        }

        .notification-warning .notification-icon {
            color: #f39c12;
        }

        .notification-info .notification-icon {
            color: #3498db;
        }

        .notification-content {
            flex: 1;
            color: #333;
            font-size: 0.95rem;
        }

        .notification-close {
            background: none;
            border: none;
            color: #95a5a6;
            cursor: pointer;
            padding: 5px;
            font-size: 0.9rem;
        }

        .notification-close:hover {
            color: #e74c3c;
        }

        .loading-spinner {
            margin-left: 10px;
            color: #3498db;
        }

        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
}
