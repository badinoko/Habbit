// Функция для редактирования темы (перенаправление на страницу редактирования)
function editTheme(themeId) {
    // Перенаправляем на страницу редактирования темы
    window.location.href = `/themes/${encodeURIComponent(themeId)}`;
}

// Функция для удаления темы
async function deleteTheme(themeId) {
    if (!confirm('Вы уверены, что хотите удалить эту тему? Все задачи с этой темой будут перемещены в "Без темы".')) {
        return;
    }

    try {
        const response = await fetch(`/themes/${encodeURIComponent(themeId)}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });

        if (response.status === 204) {
            showNotification('Тема удалена', 'success');

            // Удаляем элемент из DOM
            const themeElement = findThemeCardById(themeId);
            if (themeElement) {
                const themeName = themeElement.dataset.themeName;
                themeElement.remove();

                // Обновляем список тем в сайдбаре если есть (там фильтр по имени)
                if (themeName) {
                    updateSidebarThemes(themeName);
                }
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
function updateSidebarThemes(deletedThemeName) {
    const sidebarLinks = document.querySelectorAll('.theme-filter-link');
    sidebarLinks.forEach(link => {
        const themeParam = new URL(link.href, window.location.origin).searchParams.get('theme');
        if (themeParam === deletedThemeName) {
            const sidebarItem = link.closest('.topic-item');
            if (sidebarItem) {
                sidebarItem.remove();
            }
        }
    });
}

function findThemeCardById(themeId) {
    const cards = document.querySelectorAll('.theme-card[data-theme-id]');
    return Array.from(cards).find(card => card.dataset.themeId === themeId) || null;
}
