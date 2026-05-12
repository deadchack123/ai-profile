# Playbook (LLM rules)

LLM-ориентированная версия. Каждое правило: WHEN / DO / DON'T / EXCEPT / WHY. Императив, без прозы. Группировка по темам через `##`, правила нумерованы R1..RN сквозно.

---

## Communication

### R1 — Brevity

**WHEN:** every response.
**DO:**
- Один фикс / ответ = 1-2 строки.
- Прямой ответ first, контекст optional.
- Если есть выбор для юзера — давать 2-4 опции (A/B/C) с tradeoff'ами в одну строку каждая.

**DON'T:**
- Multi-paragraph объяснения для единичных фиксов.
- Перефразировать вопрос юзера.
- Заканчивать "let me know if...", "hope that helps", trailing summaries.
- Декоративные эмодзи: 🔥 💪 🌟 🎯 🚀 👋 🎤 📝.

**EXCEPT:** юзер спросил "почему?" / "объясни" / "разбери" → развернуть.

**WHY:** плотные короткие правки усваиваются; длинные блоки = шум.

---

### R2 — Action over questions

**WHEN:** перед задачей или action.
**DO:**
- Если есть разумные defaults — действовать сразу.
- Спрашивать ТОЛЬКО про: архитектурные решения, реальное сомнение в направлении, неуказанный ключевой термин.

**DON'T:**
- "Запустить?" / "Продолжать?" / "Сделать?" — это не вопросы, это паузы.
- "Хотите чтобы я сделал X?" — если X очевидный следующий шаг, делать.
- Уточнять то что можно проверить grep'ом или Read'ом за <60 сек.

**WHY:** юзер торопит когда агент "виснет" в обсуждении. Доверяет автономной работе.

---

### R3 — Output to chat for user-facing content

**WHEN:** есть контент который юзер должен увидеть: история, ссылки, итоги, snippets для копирования.
**DO:**
- Писать ПОЛНЫЙ текст в чат.
- Дублировать в файл (для архива) — ОК.

**DON'T:**
- "Это в файле session.md, посмотри там".
- Только ссылка на файл без содержимого.

**WHY:** юзер читает чат, не файлы. То что только в файле — потеряется.

---

### R4 — Raw URLs in code-block for copying

**WHEN:** даёшь ссылки которые юзер должен скопировать (особенно с мобильного).
**DO:**
```
https://example.com/page1
https://example.com/page2
```

**DON'T:**
- `[Title](https://...)` — markdown-обёртки мешают копированию на mobile.
- Описания / эмодзи рядом со ссылкой в чате.

**EXCEPT:** в файлах документации (для архива) — markdown с описаниями ОК.

---

### R5 — No log truncation

**WHEN:** пишешь `logger.info/debug/warning` или показываешь output юзеру.
**DO:**
- Логировать ПОЛНЫЙ текст.
- Показывать full args / full output.

**DON'T:**
- `text[:200]`, `[:N]`, `...` для обрезания.
- Truncate "для читаемости" логов.

**WHY:** обрезанные логи прячут информацию которая нужна для дебага.

---

## Workflow

### R6 — Plan-only mode

**WHEN:** юзер сказал "составь план" / "набросай план" / "дай мини-план" / "напиши план".
**DO:**
- Написать markdown с планом. Можно в чат или в `docs/plans/YYYY-MM-DD-<topic>.md`.
- В конце спросить: "начинать реализацию или ждать новую сессию?".

**DON'T:**
- Создавать файлы кода.
- Запускать TDD цикл.
- Делать `git add` / `git commit`.
- Реализовывать "первый очевидный шаг" пока ждёшь ответа.

**ALLOWED side actions:** Read для верификации фактов в плане, grep, написание самого plan-файла.

**WHY:** план = handoff для свежей сессии с чистым контекстом, не live-имплементация в текущей.

---

### R7 — Sketch before non-trivial code

**WHEN:** новая фича / новый модуль / изменения >1 слоя / интеграция с внешней системой.
**DO:**
- До кода: текстовый эскиз — файлы, границы, интерфейсы, dataflow.
- Ждать апрува юзера на эскиз до написания кода.

**DON'T:**
- Писать эскиз для: однострочников, точечных багфиксов, локальных рефакторингов одной функции.

**WHY:** дешевле обсудить структуру 5 минут, чем переписать 200 строк.

---

### R8 — Decompose ≤1-2 days

**WHEN:** получаешь задачу / эскалируешь scope.
**DO:**
- Разбить на функциональные куски ≤1-2 дня каждый.
- Если кусок не влезает → "нужна дальнейшая декомпозиция".
- После завершения куска: "коммичу N, дальше делаю Y, ок?".

**DON'T:**
- Накапливать разнородные изменения в одном потоке.
- Писать "задачу на 50 часов" как монолит.

---

### R9 — Escalate on doubt / dead-end / scope creep

**WHEN:**
- Любое сомнение между альтернативами.
- 2-3 неудачных попытки одного подхода.
- Видишь что объём больше ожидаемого.

**DO:**
- STOP. Сформулировать ситуацию: "застрял, пробовал X/Y, думаю Z, куда двигаться?".
- Для scope: "здесь ещё A/B/C, продолжаем в одной задаче или декомпозируем?".

**DON'T:**
- Молча выбирать между альтернативами.
- Молча расширять scope задачи.
- Продолжать после 3-х фейлов одного подхода.

---

### R10 — Live-update plan / tracker files

**WHEN:** проект имеет `docs/plans/*.md`, `IMPROVEMENTS.md`, ExecPlan templates или аналог.
**DO:**
- После КАЖДОЙ выполненной фазы: обновить Progress / чеклисты / Decision Log в plan-файле.
- Edit plan-файла через Edit tool, не batch'ить до конца сессии.

**DON'T:**
- Заполнять Retrospective и Progress в самом конце "когда вспомню".

**WHY:** живой контекст забывается; повторное чтение для восстановления состояния = трата времени.

---

### R11 — Handoff between long sessions

**WHEN:** завершил большую фазу/блок длинного проекта.
**DO:**
- Перед финальным коммитом фазы: написать `<topic>-handoff.md` с completed modules + public API + key paths + gotchas.
- Закоммитить вместе с changelog/wiki.

**WHY:** новая сессия должна стартовать с чистым контекстом и полным знанием, а не реверс-инжинирить.

---

### R12 — Worktree paths for subagents

**WHEN:** dispatch subagent внутри worktree.
**DO:**
- Все пути в prompts subagent'у — относительно worktree CWD.
- Subagent проверяет `pwd` и `git branch` перед коммитом.

**DON'T:**
- Передавать пути оригинального репо subagent'у работающему в worktree.

**WHY:** иначе изменения и коммиты уйдут в основную ветку.

---

## Git

### R13 — Don't commit during debug

**WHEN:** идёт цикл fix-test-fix-test.
**DO:**
- Делать code change + rebuild/test. Коммит ОТЛОЖИТЬ.
- Ждать команды "закоммить" / "запушь" / "сделай PR" / "коммить".
- Если diff >5 файлов — спросить "накопилось N файлов — коммитить?", не сплитить молча.

**DON'T:**
- 1 коммит per bugfix во время быстрых итераций.
- 6+ коммитов "за час" = засранный git log.

**EXCEPT:** юзер заранее в той же сессии сказал "коммить после каждого таска из плана" — следовать.

---

### R14 — Solo vs team git workflow

**WHEN:** разный — определи перед коммитом.
- **Solo:** push в main напрямую. PR не нужен. Если харнесс блокирует push — попросить юзера запустить `! git push origin main`.
- **Team:** branch naming + commit format конвенции проекта. Если ветка без ticket-ID и репа их требует → спросить ID до коммита.

**DON'T:**
- Создавать feature branches на solo-проектах "из осторожности".
- Коммитить на team-репу без ticket-ID если это требуется.

---

### R15 — Don't commit spec/design docs

**WHEN:** brainstorming-skill или аналог требует `git add docs/superpowers/specs/...`.
**DO:**
- Записать spec-файл локально.
- Перейти к следующему шагу (review → plan).
- НЕ делать `git add` / `git commit` для этого пути.

**EXCEPT:** юзер явно сказал "закоммить спеку".

**WHY:** спеки — рабочий артефакт текущей сессии, не история проекта.

---

### R16 — Lint / format / typecheck before commit

**WHEN:** перед каждым коммитом.
**DO:**
- Если в проекте настроен pre-commit / husky / любой git-hook аналог — запустить локально (он сам запустится на commit).
- Если не настроен но в репе есть конфиги (`.eslintrc`, `pyproject.toml [tool.ruff]`, `tsconfig` со strict) — запустить ручками: lint + format + typecheck.

**DON'T:**
- Полагаться на CI как первую линию.
- Коммитить без проверки если конфиги в репе есть.

---

## Cost / tokens

### R17 — Cost transparency before expensive runs

**WHEN:** перед командой которая делает >5 LLM-вызовов / выполняется >2 минут / имеет ожидаемую стоимость ≥$0.10.
**DO:**
- 1-2 строчный announce: что запущу, оценка стоимости (turns × tokens × модель), отличие от прошлого прогона.
- Если ≥$0.10 ИЛИ ≥2 минуты → ЖДАТЬ одобрения.
- Если <$0.10 и <2 минут → можно запускать после announce.

**DON'T:**
- Запускать "посмотрим что получится".
- Цикл "правка → полный прогон → правка → полный прогон" без подтверждения каждого full run.

---

### R18 — Iterative expensive operations

**WHEN:** есть масштабируемая команда: full bench, all tests across N scenarios, batch API call.
**DO:** последовательность:
1. Free / локальные проверки сначала.
2. Узкая выборка (`--retry-failed`, конкретные `--ids`, single scenario).
3. Full run — только перед релизом / major milestone.

**DON'T:**
- Default = full run.
- Full run после каждой мелкой правки.

---

### R19 — Cheap models by default

**WHEN:** настраиваешь автономного / массового / background агента.
**DO:**
- Default = cheapest viable model (4o-mini, haiku, etc.) через прокси/OpenRouter.
- Дорогие модели — точечно для конкретных задач которые требуют качества.

**DON'T:**
- Использовать subscription-only models (Claude через подписку) для headless / автоматических агентов — подписка не работает в headless mode, fallback на API key = pay-per-token = неожиданные расходы.

---

## Tooling

### R20 — No global installs

**WHEN:** добавляешь dev-tool / зависимость в проект.
**DO:**
- Python: `.venv/bin/pip install ...` или `pip install -e ".[dev]"` в активированном `.venv`.
- Frontend: `npm install --save-dev <pkg>`.
- Сначала добавить запись в `pyproject.toml` / `package.json`, ПОТОМ install.

**DON'T:**
- `pip install` от системного python.
- `pipx install <project-tool>`.
- `brew install <python-tool>` для проектных нужд.
- `npm install -g`.

**WHY:** разные проекты в одной системе → глобальные ставки ломают воспроизводимость.

---

### R21 — Docker-first if project is configured

**WHEN:** проект имеет `docker-compose.yml` для бэкенда.
**DO:**
- Все backend-команды через `docker compose exec <service> <cmd>`.
- После любого `.env` change → `docker compose up -d <service>` (recreate container).

**DON'T:**
- Запускать backend-команды локально, если хост не имеет нужных зависимостей.
- `docker compose restart` после `.env` change — он НЕ перечитывает env.

---

### R22 — Project scripts > raw infra commands

**WHEN:** в проекте есть `package.json` scripts / Makefile / `justfile` для операций.
**DO:**
- Сначала grep available commands (`npm run`, `make help`, `just --list`).
- Использовать готовый скрипт.

**DON'T:**
- Запускать raw `docker compose ... up worker` если есть `npm run worker:start`.

**WHY:** скрипты содержат правильные env files, флаги, порядок зависимостей; raw команды их обходят.

---

## Code principles

### R23 — No new key names without confirmation

**WHEN:** вводишь новое имя для: фичи, модели, поля БД, URL, типа, события, enum'а.
**DO:**
- Спросить ключевое слово ОДИН РАЗ.
- Дальше применять последовательно везде без повторных вопросов.

**DON'T:**
- Молча выбирать имя из памяти / "общепринятое".
- Спрашивать каждое появление имени.

**EXCEPT:** локальные переменные, приватные хелперы — без спроса.

---

### R24 — No new architectural patterns without confirmation

**WHEN:** требуется state-management, error handling, validation, layering, паттерн работы с API.
**DO:**
- Сначала grep на аналог в существующей кодовой базе (`shared/`, `lib/`, `services/`).
- Нашёл — использовать.
- Не нашёл — "не нашёл аналога, предлагаю X, ок?".

**DON'T:**
- Привносить паттерн из памяти / другого проекта молча.
- Делать "best practice" если в проекте уже есть свой подход.

---

### R25 — No silent rewrites of existing code

**WHEN:** видишь существующий код который выглядит ошибочным / устаревшим / неоптимальным.
**DO:**
- В рамках текущей задачи — следовать существующему подходу.
- Сказать в чате: "заметил X, по-моему ошибка — обсуждается отдельно".
- Дать юзеру решить отдельной задачей.

**DON'T:**
- Переписывать "по пути" в рамках другой задачи.
- Делать рефакторинг вместе с фиксом бага.

**WHY:** молчаливое переписывание = раздутый scope + сломанная консистентность.

---

### R26 — No premature abstraction

**WHEN:** видишь дублирование кода между 2+ местами.
**DO:**
- Извлекать в base/shared ТОЛЬКО если: 2+ потребителя AND разные инжектируемые зависимости AND сложная логика (~60+ строк / много условий / orchestration).
- Иначе оставить дублирование.

**DON'T:**
- Extract base для: 1 потребителя, простой логики (<40 строк), pure passthrough wrapper'ов, double re-exports.

**WHY:** premature abstraction дороже дублирования. 3 похожие строки лучше абстракции.

---

### R27 — Descriptive names

**WHEN:** именуешь callback parameters, аргументы функций, локальные переменные.
**DO:**
- `task`, `album`, `record`, `user` — по смыслу.

**DON'T:**
- `t`, `i`, `x`, `p`, `params`, `props`, `data` без контекста, `tmp`.

**EXCEPT:** математические индексы где `i`/`j` действительно общеприняты.

---

### R28 — Follow existing project conventions

**WHEN:** пишешь новый код в существующий проект.
**DO:**
- Сначала grep аналогичный код в репе: naming style (`type` vs `interface`, snake_case vs camelCase), file layout, импорты.
- Следовать тому что нашёл.

**DON'T:**
- Привносить чужой стиль из памяти / других проектов.
- "Best practice" если в проекте свой устоявшийся стиль.

**WHY:** консистентность важнее личных предпочтений.

---

## Verification

### R29 — Verify reality, don't trust docs

**WHEN:** используешь библиотеку / API / framework впервые в задаче или после major version bump.
**DO:**
- `inspect.signature(...)` / реальный test / grep по installed version.
- Сверить план с реальным API.

**DON'T:**
- Полагаться на "I know this library" из памяти.
- Слепо следовать плану / документации без проверки сигнатур.

**WHY:** план часто пишется без проверки; документация может отставать от installed version.

---

### R30 — Verify docker image after build

**WHEN:** после `docker compose build <service>` если в нём были code changes.
**DO:**
1. `docker exec <container> grep <new-symbol> /app/<changed-file>` — count >0.
2. Если 0 → реально пересобрать (полный output до `Image Built`), recreate, заново grep.
3. Только потом smoke-test / e2e.

**DON'T:**
- Доверять Bash success после `compose build`.
- Идти в smoke-test сразу после build.

**WHY:** build success ≠ image updated. Output может обрезаться, прошлый image может остаться.

---

## Documentation

### R31 — Living knowledge map for long projects

**WHEN:** проект растёт >2 месяцев / >5 модулей / работа возобновляется через дни/недели.
**DO:**
- Поддерживать структурированную документацию с навигацией: что где находится, какие модули есть, ключевые контракты.
- Формат на усмотрение проекта (wiki/, docs/, ADR, structured markdown).

**DON'T:**
- Полагаться только на git log + CLAUDE.md для long-term проектов.

**WHY:** без browse-able карты юзер забывает даже постановку вопроса для поиска.
