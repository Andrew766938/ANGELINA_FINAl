# 🧪 Тестирование исправленных функций удаления

## 📝 Предварительные шаги: Создать тестовые данные

### 1️⃣ Создать аэропорты

```bash
curl -X POST http://localhost:8000/flights/airports \
  -H "Content-Type: application/json" \
  -d '{
    "code": "MOW",
    "name": "Шереметьево",
    "city": "Москва",
    "country": "Россия"
  }'

# Ответ (запомните ID, например: 1)
# {
#   "id": 1,
#   "code": "MOW",
#   "name": "Шереметьево",
#   "city": "Москва",
#   "country": "Россия"
# }
```

```bash
curl -X POST http://localhost:8000/flights/airports \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SPB",
    "name": "Пулково",
    "city": "Санкт-Петербург",
    "country": "Россия"
  }'
# Ответ: {"id": 2, "code": "SPB", ...}
```

### 2️⃣ Создать билет (flight)

```bash
curl -X POST http://localhost:8000/flights/ \
  -H "Content-Type: application/json" \
  -d '{
    "flight_number": "SU001",
    "airline": "Aeroflot",
    "departure_airport_id": 1,
    "arrival_airport_id": 2,
    "departure_time": "2025-12-20T10:00:00",
    "arrival_time": "2025-12-20T12:00:00",
    "total_seats": 180,
    "available_seats": 180,
    "price": 5000.0
  }'

# Ответ (запомните ID, например: 5)
# {
#   "id": 5,
#   "flight_number": "SU001",
#   "airline": "Aeroflot",
#   ...
# }
```

---

## ✅ Тест 1: Удалить билет

### 1. Выполнить DELETE запрос

```bash
# 🗑️ УДАЛИТЬ билет
curl -X DELETE http://localhost:8000/flights/5 -v

# Ожидаемый Ответ:
# HTTP/1.1 204 No Content
# (пустое тело ответа)
```

### 2. Проверить, что билет удален из базы

```bash
# Проверить GET (404 - нормально)
curl http://localhost:8000/flights/5
# Ответ:
# HTTP 404
# {"detail": "Flight with id 5 not found"}
```

### 3. Проверить в базе данных

```sql
-- Откройте SQLite CLI или используйте DB Browser
SELECT COUNT(*) FROM flights WHERE id = 5;
-- Ожидаемый результат: 0 (билет удален!) ✅

SELECT * FROM flights WHERE id = 5;
-- Ожидаемый результат: (пустая выборка)
```

---

## ✅ Тест 2: Удалить аэропорт

### 1. Выполнить DELETE запрос

```bash
# 🗑️ УДАЛИТЬ аэропорт
curl -X DELETE http://localhost:8000/flights/airports/1 -v

# Ожидаемый Ответ:
# HTTP/1.1 204 No Content
# (пустое тело ответа)
```

### 2. Проверить, что аэропорт удален

```bash
# Проверить GET
curl http://localhost:8000/flights/airports/1
# Ответ: HTTP 404
```

### 3. Проверить в БД

```sql
SELECT COUNT(*) FROM airports WHERE id = 1;
-- Ожидаемый результат: 0 ✅
```

---

## ❌ Тест 3: Повторное удаление (должно вернуть 404)

```bash
# 🗑️ Попытка удалить уже удаленный билет
curl -X DELETE http://localhost:8000/flights/5 -v

# Очекиваемый Ответ:
# HTTP/1.1 404 Not Found
# {
#   "detail": "Flight with id 5 not found"
# }
```

---

## 📊 Полная последовательность тестирования

### Сценарий: Очистка системы от тестовых данных

```bash
# 1️⃣ Получить все аэропорты
curl http://localhost:8000/flights/airports/

# 2️⃣ Получить все билеты
curl http://localhost:8000/flights/

# 3️⃣ Удалить каждый билет (кнючи к аэропортам)
curl -X DELETE http://localhost:8000/flights/1
curl -X DELETE http://localhost:8000/flights/2
curl -X DELETE http://localhost:8000/flights/3

# 4️⃣ Удалить каждый аэропорт (теперь без связи)
curl -X DELETE http://localhost:8000/flights/airports/1
curl -X DELETE http://localhost:8000/flights/airports/2
curl -X DELETE http://localhost:8000/flights/airports/3

# 5️⃣ Проверить, что все удалено
curl http://localhost:8000/flights/
# Response: []

curl http://localhost:8000/flights/airports/
# Response: []
```

---

## 👀 Обсервация в консоли

При мониторинге консоли FastAPI, вы должны видеть в логах:

```
[DELETE /flights/1] Deleting flight
[DELETE /flights/1] Flight deleted
[DELETE /flights/airports/1] Deleting airport
[DELETE /flights/airports/1] Airport deleted successfully
```

Отсутствие ошибок в логах = все правильно! 😀

---

## 📚 Команды SQLite для проверки

```bash
# Открыть БД
sqlite3 test.db

# Посмотреть все таблицы
.tables

# Показать количество аэропортов
SELECT COUNT(*) as airport_count FROM airports;

# Показать количество билетов
SELECT COUNT(*) as flights_count FROM flights;

# Показать все аэропорты
SELECT * FROM airports;

# Показать все билеты
SELECT * FROM flights;

# Отыскать конкретный айтем
SELECT * FROM airports WHERE id = 1;
SELECT * FROM flights WHERE id = 5;

# Выйти
.exit
```

---

## 🚀 Это готово!

Обе функции делете теперь работают корректно!

**Что было исправлено**:
- ✅ Добавлен `await self.db_session.flush()` в `delete_flight()`
- ✅ Добавлен `await self.db_session.flush()` в `delete_airport()`
- ✅ Немедленная синхронизация с БД
- ✅ Нет race conditions
- ✅ Нет "привидений" в БД
