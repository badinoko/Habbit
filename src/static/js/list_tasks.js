// В самом начале файла объявим глобальные переменные для состояния
window.currentSort = 'created';
window.currentOrder = 'desc';

document.addEventListener('DOMContentLoaded', () => {
    const tasksList = document.querySelector('.tasks-list');
    const statusFilter = document.getElementById('status-filter');
    const sortSelect = document.getElementById('sort-tasks');
    const sortAscBtn = document.getElementById('sort-asc');
    const sortDescBtn = document.getElementById('sort-desc');

    // Сохраним ссылку на контейнер в глобальной переменной, если нужно
    window.tasksListContainer = tasksList;

    // Устанавливаем начальное активное состояние кнопок
    if (sortDescBtn) sortDescBtn.classList.add('active');
    if (sortAscBtn) sortAscBtn.classList.remove('active');

    // Функция получения всех элементов задач (используем глобальную ссылку на контейнер)
    function getAllTaskItems() {
        const container = window.tasksListContainer || document.querySelector('.tasks-list');
        return Array.from(container.querySelectorAll('.task-item'));
    }

    // Функция сравнения (без изменений)
    function compareTasks(a, b) {
        let valA, valB;

        switch (currentSort) {
            case 'name':
                valA = a.querySelector('.task-title').textContent.trim().toLowerCase();
                valB = b.querySelector('.task-title').textContent.trim().toLowerCase();
                return valA.localeCompare(valB);

            case 'priority':
                // Ищем элемент с классом task-priority и получаем значение из data-priority-value
                const priorityElementA = a.querySelector('.task-priority');
                const priorityElementB = b.querySelector('.task-priority');

                valA = priorityElementA ? parseInt(priorityElementA.dataset.priorityValue || '0', 10) : 0;
                valB = priorityElementB ? parseInt(priorityElementB.dataset.priorityValue || '0', 10) : 0;

                // Для сортировки по убыванию (высокий приоритет сверху)
                return valB - valA;   // 3(high) > 2(medium) > 1(low)

            case 'updated':
                valA = a.dataset.updated || '0000-00-00T00:00:00';
                valB = b.dataset.updated || '0000-00-00T00:00:00';
                return valA.localeCompare(valB);

            case 'created':
            default:
                valA = a.dataset.created || '0000-00-00T00:00:00';
                valB = b.dataset.created || '0000-00-00T00:00:00';
                return valA.localeCompare(valB);
        }
    }

    // Основная функция сортировки
    function sortTasks() {
        const tasks = getAllTaskItems();
        if (tasks.length === 0) return;

        tasks.sort((a, b) => {
            const comparison = compareTasks(a, b);
            return window.currentOrder === 'asc' ? comparison : -comparison;
        });

        const container = window.tasksListContainer || document.querySelector('.tasks-list');
        while (container.firstChild) container.removeChild(container.firstChild);
        tasks.forEach(task => container.appendChild(task));
    }

    // Функция фильтрации по статусу
    function applyStatusFilter() {
        const status = statusFilter ? statusFilter.value : 'active';
        const tasks = getAllTaskItems();
        if (tasks.length === 0) return;

        tasks.forEach(task => {
            const completedAt = task.dataset.completed;
            const isCompleted = completedAt && completedAt !== 'None' && completedAt !== '' && completedAt !== 'null';
            let shouldShow = true;
            if (status === 'active') shouldShow = !isCompleted;
            else if (status === 'completed') shouldShow = isCompleted;
            task.style.display = shouldShow ? '' : 'none';
        });
    }

    // Делаем функции глобальными
    window.sortTasks = sortTasks;
    window.applyStatusFilter = applyStatusFilter;

    // Обработчики изменения сортировки
    if (sortSelect) {
        sortSelect.addEventListener('change', () => {
            window.currentSort = sortSelect.value;
            sortTasks();
            applyStatusFilter(); // после сортировки фильтр применяется автоматически
        });
    }

    if (sortAscBtn) {
        sortAscBtn.addEventListener('click', () => {
            window.currentOrder = 'asc';
            sortAscBtn.classList.add('active');
            if (sortDescBtn) sortDescBtn.classList.remove('active');
            sortTasks();
            applyStatusFilter();
        });
    }

    if (sortDescBtn) {
        sortDescBtn.addEventListener('click', () => {
            window.currentOrder = 'desc';
            sortDescBtn.classList.add('active');
            if (sortAscBtn) sortAscBtn.classList.remove('active');
            sortTasks();
            applyStatusFilter();
        });
    }

    // Обработчик изменения фильтра статуса
    if (statusFilter) {
        statusFilter.addEventListener('change', () => {
            applyStatusFilter();
        });
    }

    // Первоначальное применение сортировки и фильтра
    sortTasks();
    applyStatusFilter();
});
