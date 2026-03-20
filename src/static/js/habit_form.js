document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.item-form');
    const scheduleTypeSelect = document.getElementById('schedule_type');
    const scheduleConfigInput = document.getElementById('schedule_config');
    const startsOnInput = document.getElementById('starts_on');
    const endsOnInput = document.getElementById('ends_on');
    const periodInfiniteCheckbox = document.getElementById('period-infinite');

    if (!form || !scheduleTypeSelect || !scheduleConfigInput) {
        return;
    }

    const scheduleBlocks = {
        daily: document.getElementById('schedule-config-daily'),
        weekly_days: document.getElementById('schedule-config-weekly-days'),
        monthly_day: document.getElementById('schedule-config-monthly-day'),
        yearly_date: document.getElementById('schedule-config-yearly-date'),
        interval_cycle: document.getElementById('schedule-config-interval-cycle')
    };

    function toggleScheduleBlocks() {
        const selectedType = scheduleTypeSelect.value;
        Object.entries(scheduleBlocks).forEach(([type, block]) => {
            if (!block) return;
            block.style.display = type === selectedType ? 'block' : 'none';
        });
    }

    function checkedValues(name) {
        return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`))
            .map((input) => input.value);
    }

    function asPositiveInt(id, label) {
        const input = document.getElementById(id);
        const value = Number.parseInt(input?.value || '', 10);
        if (!Number.isFinite(value) || value < 1) {
            throw new Error(`Поле "${label}" должно быть больше 0`);
        }
        return value;
    }

    function buildScheduleConfig() {
        const scheduleType = scheduleTypeSelect.value;
        if (scheduleType === 'daily') {
            return {};
        }

        if (scheduleType === 'weekly_days') {
            const days = checkedValues('weekly_days');
            if (days.length === 0) {
                throw new Error('Для расписания "По дням недели" выберите хотя бы один день');
            }
            return { days };
        }

        if (scheduleType === 'monthly_day') {
            const day = asPositiveInt('monthly_day', 'День месяца');
            if (day > 31) {
                throw new Error('День месяца должен быть в диапазоне 1..31');
            }
            return { day };
        }

        if (scheduleType === 'yearly_date') {
            const month = asPositiveInt('yearly_month', 'Месяц');
            const day = asPositiveInt('yearly_day', 'День');
            if (month > 12) {
                throw new Error('Месяц должен быть в диапазоне 1..12');
            }
            if (day > 31) {
                throw new Error('День должен быть в диапазоне 1..31');
            }
            return { month, day };
        }

        if (scheduleType === 'interval_cycle') {
            return {
                active_days: asPositiveInt('interval_active_days', 'Дней подряд (N)'),
                break_days: asPositiveInt('interval_break_days', 'Дней перерыва (K)')
            };
        }

        throw new Error('Некорректный тип расписания');
    }

    function showError(message) {
        if (typeof showFormError === 'function') {
            showFormError(message);
            return;
        }
        alert(message);
    }

    function togglePeriodFields() {
        if (!endsOnInput || !periodInfiniteCheckbox) {
            return;
        }
        endsOnInput.disabled = periodInfiniteCheckbox.checked;
        if (periodInfiniteCheckbox.checked) {
            endsOnInput.value = '';
        }
    }

    function normalizePeriod() {
        const startsOn = startsOnInput?.value || null;
        let endsOn = endsOnInput?.value || null;

        if (periodInfiniteCheckbox?.checked) {
            endsOn = null;
        } else if (endsOnInput && !endsOnInput.value) {
            throw new Error(
                'Укажите дату конца периода или включите "Бесконечный период"'
            );
        }

        if (startsOn && endsOn && endsOn < startsOn) {
            throw new Error('Дата конца периода не может быть раньше даты начала');
        }

        if (endsOnInput) {
            endsOnInput.disabled = false;
            endsOnInput.value = endsOn || '';
        }

        return { startsOn, endsOn };
    }


    scheduleTypeSelect.addEventListener('change', toggleScheduleBlocks);
    toggleScheduleBlocks();
    periodInfiniteCheckbox?.addEventListener('change', togglePeriodFields);
    togglePeriodFields();

    form.addEventListener('submit', (event) => {
        try {
            const scheduleConfig = buildScheduleConfig();
            normalizePeriod();
            scheduleConfigInput.value = JSON.stringify(scheduleConfig);
        } catch (error) {
            event.preventDefault();
            showError(error instanceof Error ? error.message : 'Ошибка валидации формы');
            return;
        }

        const method = (form.dataset.method || form.getAttribute('method') || 'post').toLowerCase();
        if (method === 'put') {
            return;
        }
    });
});
