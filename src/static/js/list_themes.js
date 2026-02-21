// Функция для редактирования темы (перенаправление на страницу редактирования)
function editTheme(themeName) {
    // Перенаправляем на страницу редактирования темы
    window.location.href = `/themes/${encodeURIComponent(themeName)}`;
}

// Функция для удаления темы
async function deleteTheme(themeId) {
    if (!confirm('Вы уверены, что хотите удалить эту тему? Все задачи с этой темой будут перемещены в "Без темы".')) {
        return;
    }

    try {
        const response = await fetch(`/themes/${themeId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });

        if (response.status === 204) {
            showNotification('Тема удалена', 'success');

            // Удаляем элемент из DOM
            const themeElement = document.querySelector(`[data-theme-id="${themeId}"]`);
            if (themeElement) {
                themeElement.remove();
            }

            // Обновляем список тем в сайдбаре если есть
            updateSidebarThemes(themeId);

            // Обновляем статистику если есть
            if (typeof updateStats === 'function') {
                updateStats();
            }

            // Перезагружаем страницу через 1 секунду
            setTimeout(() => {
                window.location.reload();
            }, 1000);

        } else {
            showNotification('Ошибка при удалении темы', 'error');
        }
    } catch (error) {
        console.error('Error deleting theme:', error);
        showNotification('Ошибка соединения с сервером', 'error');
    }
}

// Функция для обновления списка тем в сайдбаре после удаления
function updateSidebarThemes(deletedThemeId) {
    const sidebarTheme = document.querySelector(`.topic-item[data-topic-id="${deletedThemeId}"]`);
    if (sidebarTheme) {
        sidebarTheme.remove();
    }
}
