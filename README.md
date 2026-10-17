# Messenger

Онлайн-месенджер (початкова основа): FastAPI + WebSocket.

## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Відкрийте http://127.0.0.1:8000 у кількох вкладках, щоб побачити спільний чат.

## Тести

```bash
pytest
```

## Структура

```
app/
  main.py        # FastAPI-застосунок і WebSocket-чат
  static/        # веб-клієнт
tests/           # pytest
```

## Плани

- Автентифікація користувачів
- Збереження повідомлень у БД
- Кімнати / приватні чати
