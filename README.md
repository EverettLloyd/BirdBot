# BirdBot

Асинхронный Telegram-бот для сбора заявок на пристройство птиц. Используется
`aiogram v3`, база данных PostgreSQL и SQLAlchemy.

## Требования
- Python 3.11+
- PostgreSQL сервер
- Переменные окружения:
  - `BOT_TOKEN` – токен Telegram бота
  - `DATABASE_URL` – строка подключения к PostgreSQL
  - `ADMIN_CHAT_ID` – чат для приёма заявок
  - `PUBLICATION_CHANNEL_ID` – канал для публикаций

## Установка
```bash
pip install -r requirements.txt
```

## Запуск
```bash
python -m bot
```

Бот поддерживает две формы: "Хочу приютить" и "Отдать птицу". После заполнения
заявка отправляется в админский чат, где её можно одобрить или отклонить.
