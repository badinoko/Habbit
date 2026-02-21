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

// Функция для инициализации состояния выполненных задач при загрузке страницы
function initializeTaskStates() {
    const taskItems = document.querySelectorAll('.task-item');
    taskItems.forEach(taskItem => {
        const completedAt = taskItem.dataset.completed;
        const isCompleted = completedAt && completedAt !== 'None' && completedAt !== '' && completedAt !== 'null';

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
        checkbox.addEventListener('change', function() {
            const taskItem = this.closest('.task-item');
            const taskId = this.dataset.taskId || taskItem.dataset.taskId;

            markTaskAsCompleted(taskId, this, taskItem);
        });
    });

    // Обработка кнопок привычек
    const habitButtons = document.querySelectorAll('.btn-habit-complete:not(.completed)');
    habitButtons.forEach(button => {
        button.addEventListener('click', function() {
            const habitId = this.dataset.habitId ||
                           this.id.replace('habit-', '') ||
                           this.closest('.habit-card').dataset.habitId;
            markHabitAsCompleted(habitId, this);
        });
    });

    // Выбор темы
    const topicItems = document.querySelectorAll('.topic-item');
    topicItems.forEach(item => {
        item.addEventListener('click', function() {
            const topicId = this.dataset.topicId;
            filterByTopic(topicId, this);
        });
    });

    // Фильтрация задач
    const topicFilter = document.getElementById('topic-filter');
    if (topicFilter) {
        topicFilter.addEventListener('change', function() {
            filterTasksByTopic(this.value);
        });
    }

    // Редактирование и удаление
    initializeEditDeleteHandlers();
}


async function markTaskAsCompleted(taskId, checkbox, taskItem) {
    const wasChecked = checkbox.checked; // состояние до запроса

    try {
        showLoading(checkbox);

        // Выбираем endpoint в зависимости от того, становится ли задача выполненной или нет
        const endpoint = wasChecked ? `/tasks/${taskId}/complete` : `/tasks/${taskId}/incomplete`;

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
                activeTasksCount--;
            } else {
                taskItem.classList.remove('completed');
                const taskTitle = taskItem.querySelector('.task-title');
                if (taskTitle) taskTitle.classList.remove('completed');
                showNotification('Задача возвращена в активные', 'info');
                // Увеличиваем счётчик активных задач
                activeTasksCount++;
            }

            // Синхронизируем чекбокс (на случай, если сервер вернул иное)
            checkbox.checked = isCompleted;

            // Обновляем отображение статистики
            const activeEl = document.getElementById('stat-active-tasks');
            if (activeEl) activeEl.textContent = activeTasksCount;

            // Если есть другие обновления статистики (например, для привычек), можно вызвать
            if (typeof updateStats === 'function') updateStats();
        } else {
            // Ошибка сервера – откатываем чекбокс
            checkbox.checked = wasChecked;
            showNotification(data.error || 'Ошибка при обновлении задачи', 'error');
        }
    } catch (error) {
        console.error('Error toggling task:', error);
        checkbox.checked = wasChecked;
        showNotification('Ошибка соединения с сервером', 'error');
    } finally {
        hideLoading(checkbox);
    }
}

async function markHabitAsCompleted(habitId, button) {
    const habitCard = button.closest('.habit-card');
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

            if (typeof updateStats === 'function') {
                setTimeout(updateStats, 500);
            }
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

            // Обновляем статистику если есть
            if (typeof updateStats === 'function') updateStats();
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

function filterByTopic(topicId, clickedElement) {
    // Сбрасываем активное состояние у всех тем
    document.querySelectorAll('.topic-item').forEach(item => {
        item.classList.remove('active');
    });

    // Устанавливаем активное состояние выбранной теме
    clickedElement.classList.add('active');

    // Обновляем URL
    const url = new URL(window.location);
    if (topicId && topicId !== 'all') {
        url.searchParams.set('theme', topicId);
    } else {
        url.searchParams.delete('theme');
    }
    window.history.pushState({}, '', url);

    // Загружаем задачи через AJAX (если нужно)
    loadTasksByTheme(topicId);
}

async function loadTasksByTheme(themeId) {
    const container = document.getElementById('tasks-list-container');
    if (!container) return;

    container.innerHTML = '<div class="loading">Загрузка...</div>';

    const url = themeId && themeId !== 'all' ? `/tasks/?theme=${themeId}` : '/tasks/';
    try {
        const response = await fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!response.ok) throw new Error('Network error');
        const html = await response.text();
        container.innerHTML = html;

        // Переинициализируем состояние чекбоксов и обработчики из main.js
        initializeTaskStates();
        initializeEventHandlers();

        // Восстанавливаем сортировку и фильтрацию
        if (window.sortTasks) window.sortTasks();
        if (window.applyStatusFilter) window.applyStatusFilter();

    } catch (error) {
        console.error('Error loading tasks:', error);
        container.innerHTML = '<div class="error">Ошибка загрузки задач</div>';
    }
}

function filterTasksByTopic(topicId) {
    const tasks = document.querySelectorAll('.task-item');
    tasks.forEach(task => {
        if (topicId === 'all' || task.dataset.topicId === topicId) {
            task.style.display = 'flex';
        } else {
            task.style.display = 'none';
        }
    });
}


function initializeEditDeleteHandlers() {
    // Обработчики для кнопок редактирования
    const editButtons = document.querySelectorAll('.btn-task-edit, .btn-habit-edit');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const id = this.dataset.taskId || this.dataset.habitId;
            const type = this.classList.contains('btn-task-edit') ? 'task' : 'habit';
            editItem(type, id);
        });
    });

    // Обработчики для кнопок удаления (теперь используется глобальная функция deleteTask)
    const deleteButtons = document.querySelectorAll('.btn-task-delete');
    deleteButtons.forEach(button => {
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

function updateStats() {
}

window.addEventListener('popstate', () => {
    const params = new URLSearchParams(window.location.search);
    const themeId = params.get('theme');
    // Находим элемент темы, соответствующий themeId, и делаем его активным
    document.querySelectorAll('.topic-item').forEach(item => {
        const id = item.dataset.topicId;
        if (id === themeId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    loadTasksByTheme(themeId);
});

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

        /* Обновленные стили для чекбокса */
        .task-checkbox {
            position: relative;
            width: 20px;
            height: 20px;
            flex-shrink: 0;
        }

        .task-checkbox input[type="checkbox"] {
            width: 20px;
            height: 20px;
            border: 2px solid #95a5a6;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s ease;
            appearance: none;
            -webkit-appearance: none;
            position: relative;
            margin: 0;
        }

        .task-checkbox input[type="checkbox"]:checked {
            background-color: #2ecc71;
            border-color: #2ecc71;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='white' d='M10.28 2.28L4.5 8.06 1.72 5.28a.75.75 0 00-1.06 1.06l3.25 3.25a.75.75 0 001.06 0l6.25-6.25a.75.75 0 00-1.06-1.06z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: center;
            background-size: 12px;
        }

        /* Стили для выполненных задач */
        .task-item.completed {
            opacity: 0.7;
        }

        .task-item.completed .task-title {
            text-decoration: line-through;
            color: #95a5a6;
        }
    `;
    document.head.appendChild(style);
}
