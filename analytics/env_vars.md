# Environment Variables

Ниже перечислены все необходимые переменные окружения и их краткое назначение:

- `SUPABASE_ENDPOINT` — базовый URL проекта Supabase
- `SUPABASE_KEY` — секретный ключ (anon или service-role) для доступа к API Supabase.

- `SENTRY_DSN` — URL-строка (Data Source Name) для отправки ошибок и событий в ваш проект Sentry.
- `SENTRY_ENV` —  название среды (например, production, staging, development), которое помечает, откуда пришли события **(по умолчанию 'production')**.
- `SENTRY_TRACES_SAMPLE_RATE` — доля (от 0 до 1) захваченных транзакций для APM; например, 0.1 значит 10% запросов **(по умолчанию 0.0)**.
- `SENTRY_DEBUG` — флаг (true/false) для включения подробного логирования самого SDK Sentry **(по умолчанию false)**.

- `LOG_LEVEL` — уровень логирования **(по умолчанию info)** Уровни: debug - показывает все логи входящих запросов и info - показывает общий вывод.
- `PORT` — номер TCP-порта, на котором приложение будет слушать входящие запросы **(по умолчанию 50053)**.

- `TELEGRAM_API_GRPC_URL`  — URL gRPC-эндоинта для подключения к Telegram API сервису.
- `AI_PROCESSOR_API_GRPC_URL` — URL gRPC-эндоинта для подключения к сервису обработки AI-запросов.