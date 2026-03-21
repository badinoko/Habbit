# Mobile Adaptation - Startup Prompt

> **Версия:** Session #11 (после Session #10 2026-02-21)
> **Приоритет:** КРИТИЧЕСКИЙ - унификация кнопок

---

## ⚠️ КРИТИЧЕСКАЯ ПРОБЛЕМА: ХАОС РАЗМЕРОВ КНОПОК

**Цитата пользователя:**
> "Хрен поймешь, почему у нас такие разные уникальные кнопки, блядь. Шесть, сука, размеров или пять, блядь. В пизду это все."

**Текущее состояние sticky bar (Gallery):**
- View toggle: ОГРОМНЫЕ (больше аватара пользователя)
- Drawer кнопка: огромная рамка, минимальный значок внутри
- Search кнопка: квадратная, другой размер
- Кнопка плюсика: самая маленькая, значок смещён влево
- Switcher Фото/Альбомы: прямоугольный, разная ширина при переключении

---

## РЕГРЕССИЯ: Drawer смещает контент (#MOBILE-113)

**Новое поведение (хуже чем раньше!):**
- Sticky bar смещается ВПРАВО при открытии drawer
- Контент ниже смещается ВЛЕВО
- Раньше sticky bar не двигался

**Нужно изучить:** Документ про модальные окна и компенсацию scrollbar.

---

## ОБЯЗАТЕЛЬНО ПРОЧИТАТЬ ПЕРЕД НАЧАЛОМ

```
@docs/mobile/overview.md      - Dashboard с задачами
@docs/mobile/feedback.md      - Дословный фидбэк (Session #10 в конце)
@docs/mobile/progress.md      - Хронология работы
```

---

## ПРИОРИТЕТЫ (Session #11)

### ПРИОРИТЕТ 1: Унификация размеров кнопок

**Цель:** Все кнопки в sticky bar должны быть ОДИНАКОВОГО размера.

**Задачи:**
1. #MOBILE-121 - Унификация всех кнопок
2. #MOBILE-122 - Уменьшить view toggle
3. #MOBILE-123 - Увеличить кнопку плюсика, центрировать значок
4. #MOBILE-124 - Уменьшить рамку drawer кнопки

**Подход:**
- Определить ОДИН размер для всех кнопок (44px? 40px? 48px?)
- Применить ко ВСЕМ кнопкам в sticky bar
- Протестировать на desktop и mobile

### ПРИОРИТЕТ 2: Drawer смещение

**Задача:** #MOBILE-113 - найти причину и исправить

**Что проверить:**
- Компенсация scrollbar в CSS
- `drawer-open` класс на body
- Padding-right при открытии drawer

### ПРИОРИТЕТ 3: Прочие исправления

1. #MOBILE-116 - Вернуть кнопку "Прочитать все"
2. #MOBILE-117 - Убрать "Тип контента" из drawer
3. #MOBILE-118 - Убрать кнопку "Все" (= "Новые")
4. #MOBILE-119 - Фиксированная ширина switcher
5. #MOBILE-120 - Увеличить крестик сброса

### ПРИОРИТЕТ 4: Theme switcher в dropdown

**Задача:** #MOBILE-115 - исправить смещение иконки

**Проблемы:**
- Desktop: иконка не в линии с другими иконками
- Mobile: надпись "Сменить тему" прижата к правому краю

**Файлы:**
- `static/css/user_dropdown_unified.css`
- `templates/includes/partials/unified_user_dropdown.html`

---

## Чеклист перед началом работы

```
[ ] Прочитал overview.md - понял текущий статус задач
[ ] Прочитал feedback.md (Session #10) - понял проблемы
[ ] Изучил gallery_redesign.css - понял текущие стили кнопок
[ ] Определил единый размер для всех кнопок
[ ] Готов начать унификацию
```

---

## ЗАПРЕТЫ

1. **НЕ ТРОГАТЬ navbar** - там всё хрупко
2. **НЕ добавлять новые элементы** без согласования
3. **НЕ делать скриншоты** без проверки самому в Playwright
4. **НЕ МЕНЯТЬ СТАТУСЫ** без подтверждения пользователя

---

## Ключевые файлы

**Sticky bar:**
- `static/css/gallery_redesign.css` - основные стили
- `static/css/news_redesign.css` - референс
- `static/css/growreports_redesign.css` - аналог

**Templates:**
- `templates/gallery/gallery_list.html`
- `templates/gallery/my_albums.html`

**Dropdown:**
- `static/css/user_dropdown_unified.css`
- `templates/includes/partials/unified_user_dropdown.html`

---

## ТЕСТИРОВАНИЕ

**Обязательные ширины:** 320px, 412px, 768px, 1920px
**Playwright URL:** `http://host.docker.internal:8001/`

```javascript
mcp__MCP_DOCKER__browser_navigate("http://host.docker.internal:8001/gallery/")
mcp__MCP_DOCKER__browser_resize({ width: 412, height: 915 })
mcp__MCP_DOCKER__browser_snapshot()
```
