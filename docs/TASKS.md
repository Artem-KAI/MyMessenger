# Розподіл роботи (lab-01-messenger)

## Backend: Артем
Гілки `backend/<фіча>`, папка `app/` (крім `app/static/`).
- [x] Моделі `User`, `Conversation`, `Message` (час у UTC): `app/models.py`
- [x] Валідація: `app/validation.py`
- [x] Атомарне збереження в JSON: `app/storage.py`
- [x] Сервіс: користувачі, розмови, повідомлення, історія: `app/services.py`
- [x] Групові чати (3+), пошук повідомлень
- [x] REST API поверх `MessengerService`: `app/api.py`, опис у `docs/API.md`
- [ ] WebSocket поверх `MessengerService` (живі оновлення)
- [x] Обробка помилок сховища (`StorageError`), тести

## Frontend / клієнт: напарник
Гілки `frontend/<фіча>`, папка `app/static/`.
- [x] Екран входу / створення користувача
- [x] Список розмов, вікно чату, відправка повідомлень
- [x] Показ часу в локальній зоні (зберігається в UTC)
- [x] Пошук, повідомлення про помилки валідації
- [ ] README: скріншоти, запис 15 с

## Контракт
Фронтенд працює з REST API з `docs/API.md`. Запуск: `uvicorn app.main:app --reload`, документація на `/docs`.
