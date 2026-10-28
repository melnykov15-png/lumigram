# Changelog

## Unreleased

### Сборка
- Сборка в GitHub Actions на раннере `xcode-27` (Xcode 27.1) с кэшем Bazel, который сохраняется даже при неудачной или прерванной сборке.
- База: Swiftgram `e3a3922` (Telegram 13.1.1).
- Одноразовая поддельная подпись для сборки; итоговый `.ipa` переподписывается Sideloadly.

### Совместимость с бесплатным Apple ID
- Отключены app extensions (Share, Widget, Notification Service/Content, Siri Intents, Broadcast Upload).
- Из entitlements убраны push, CarPlay, iCloud, Siri, Sign in with Apple, Apple Pay, communication notifications.
- Если App Group недоступен после переподписи, данные хранятся в папке `Application Support/AppGroupFallback` вместо ошибки «Error 2» при запуске.

### Оформление
- Название Lumigram, bundle id `io.lumigram.<логин GitHub>` (можно задать переменной `BUNDLE_ID`).
- Новая иконка.
