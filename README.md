# Lumigram

Неофициальный клиент Telegram для iPhone на основе [Swiftgram](https://github.com/Swiftgram/Telegram-iOS) (GPL‑2.0). Собирается бесплатно в GitHub Actions, ставится через Sideloadly с бесплатным Apple ID.

Lumigram не связан с Telegram и Swiftgram. Используется собственный api_id.

## Как это устроено

Репозиторий не хранит копию Swiftgram. Сборка:

1. скачивает Swiftgram на зафиксированном коммите (`mod/UPSTREAM_COMMIT`);
2. накладывает мод: `mod/apply_mod.py` (точечные правки) и `mod/overlay/` (новые файлы);
3. собирает неподписанный `.ipa` на macOS‑раннере (`.github/workflows/build.yml`) с кэшем Bazel.

Чтобы обновить базу Swiftgram, достаточно поменять коммит в `mod/UPSTREAM_COMMIT`.

## Документы

- [docs/SETUP.md](docs/SETUP.md) — что сделать один раз: GitHub, api_id, секреты.
- [docs/INSTALL.md](docs/INSTALL.md) — установка на iPhone через Sideloadly и переподпись раз в 7 дней.
- [docs/PLAN.md](docs/PLAN.md) — план проекта и список задач.
- [CHANGELOG.md](CHANGELOG.md) — список изменений.
