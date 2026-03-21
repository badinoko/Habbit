# PROMPT: Artifact Next Pass — Public Shell + Public Listings

> Цель: попросить artifact-assistant не "бережно адаптировать" старые Besedka surfaces, а перерисовать public shell и public listings более буквально по visual language артефактов, но с учётом реальных runtime-ограничений проекта.

---

## Что нужно перерисовать

1. Верхний public shell:
   - глобальный navbar;
   - sticky bar;
   - их совместную работу как единого visual stack.
2. Public listings:
   - `news`;
   - `gallery photos`;
   - `gallery albums`;
   - `growreports`.

---

## Что уже известно по текущему состоянию

1. Homepage уже попала в нужное artifact-направление и воспринимается prototype-like.
2. Gallery photos стали интереснее за счёт masonry и hover overlay.
3. News и GrowReports пока слишком похожи на прежние карточки Besedka; изменения считываются в основном как typography refresh.
4. Самый слабый участок сейчас — верхняя часть страниц: navbar и sticky bar визуально не совпадают с новым контентом под ними.
5. News desktop composition сейчас не принята:
   - большая featured-card слева не складывается по высоте с двумя карточками справа;
   - под featured появляются пустоты;
   - ряд ниже ломается вместо плотной artifact-like композиции.
6. List-view across modules тоже требует отдельного pass: особенно плохо воспринимается News list.

---

## Реальный Besedka navbar contract

Artifact-assistant должен рисовать navbar не как абстрактный лендинг-header, а как реальную верхнюю панель Besedka.

### Постоянные элементы navbar

Слева направо:
1. hamburger / sidebar trigger в левой части;
2. бренд Besedka;
3. центральная зона навигации;
4. notifications bell;
5. user area с dropdown пользователя.

### Три основных состояния navbar

#### 1. Public / homepage / основные разделы

Центральная зона показывает переключение между основными разделами сайта:
- Новости
- Гроурепорты
- Галерея
- Чат
- Магазин/другие frozen sections могут визуально существовать, но не должны ломать main navigation rhythm

#### 2. Admin state

Когда пользователь в админке, центральная зона не повторяет public sections, а показывает переключение между доступными admin surfaces.

Особенность:
- у owner есть dropdown переключения между админками;
- user dropdown, notifications и hamburger всё равно остаются частью верхней панели;
- navbar не должен превращаться в отдельный "чужой" продукт.

#### 3. Chat state

Когда пользователь в чате:
- центральная зона показывает переключение между чатами;
- минимум есть general chat;
- если у пользователя есть доступ, дополнительно есть VIP chat;
- user dropdown остаётся тем же;
- отсутствие VIP доступа не должно ломать geometry navbar.

---

## Реальный sticky bar contract

Sticky bar у Besedka — это не декоративная полоска и не hero-subnav.
Это вторая навигационная панель, которая:
- живёт почти на всех глубинах;
- всегда тянет назад;
- держит section-specific controls;
- является важной частью UX, а не временным workaround.

Нужно предложить visual redesign sticky bar так, чтобы:
1. он ощущался продолжением нового navbar;
2. не выглядел старым стеклянным слоем под новым artifact content;
3. оставался функционально плотным;
4. был применим на разных глубинах страниц, а не только в public listings.

Что важно помнить:
- кнопка назад там почти всегда есть;
- sticky bar нужен и в list, и в detail сценариях;
- он не должен быть удалён из концепта.

---

## Ограничения runtime, которые нельзя игнорировать

1. Нельзя выкинуть hamburger, notifications bell и user dropdown только потому, что их не было в исходных прототипах.
2. Нельзя ломать sticky bar contract.
3. Нельзя возвращать owner edit/delete на public preview cards.
4. Нельзя менять data contracts ради картинки.
5. Нельзя молча ломать `GrowEntry.images -> gallery.Photo`.

---

## Что хочется получить от artifact-assistant

Не CSS-советы и не "адаптацию по мотивам", а новый visual target:

1. public navbar, уже совместимый с реальным Besedka shell;
2. sticky bar, уже совместимый с реальным Besedka UX;
3. news listing, где featured / secondary / tertiary cards складываются без пустот и ощущаются artifact-native;
4. growreports listing, который действительно отличается по hierarchy и geometry от старой Besedka-card;
5. gallery listings, которые сохраняют удачные находки текущего pass, но лучше интегрируются с новым shell.

---

## Готовый текст для следующего artifact-assistant

```text
Нужно сделать не "бережную адаптацию", а новый artifact pass для public shell и public listings проекта Besedka.

У проекта уже есть реальный runtime shell, который нельзя игнорировать:
- слева в navbar всегда есть hamburger;
- справа всегда есть notifications bell и user dropdown;
- в центре navbar живёт navigation zone, но она бывает в 3 состояниях:
  1) public/home/main sections;
  2) admin mode с переключением между admin surfaces;
  3) chat mode с переключением между chat rooms (general, а для части пользователей ещё VIP).

Кроме navbar, в проекте есть sticky bar — это важная UX-панель почти на всех глубинах. Её нельзя убирать. Нужно визуально встроить её в новый shell, чтобы она выглядела продолжением navbar и нового artifact language, а не старым стеклянным слоем из прошлой версии.

Нужно перерисовать:
- public navbar;
- sticky bar;
- news listing;
- gallery photos listing;
- gallery albums listing;
- growreports listing.

Что уже известно по QA:
- homepage уже выглядит близко к prototype-state;
- gallery photos сейчас ощущаются лучше всего из public listings;
- news и growreports пока слишком похожи на старые Besedka cards;
- news desktop composition сейчас не принята: большая featured card слева не складывается по высоте с карточками справа, под ней образуются пустоты и ломается следующий ряд;
- list-view across modules тоже требует нового pass;
- визуально нужно уйти от ощущения "мы просто взяли старые карточки Besedka и слегка переодели их".

Нужен именно новый visual target, а не советы по CSS:
- более буквальный перенос visual language из артефактов;
- более плотная, packed/tetris-like композиция news listing без дыр;
- growreports listing с собственной hierarchy, а не с news-card silhouette;
- shell, который учитывает реальные Besedka constraints, но всё равно выглядит как единый redesign.

Не игнорируй runtime constraints:
- user dropdown, bell, hamburger должны остаться;
- sticky bar должен остаться;
- не предлагай ломать data contracts ради картинки.
```
