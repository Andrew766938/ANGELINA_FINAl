# API Примеры рядов

Все эксемплы должны быть эндпоинтами в `http://localhost:8000`

## Рейсы (Flights)

### 1. Получить все рейсы

```bash
curl -X GET http://localhost:8000/flights/
```

**Ответ:**
```json
[
  {
    "id": 1,
    "flight_number": "SU-123",
    "airline": "Aeroflot",
    "departure_airport": {
      "id": 1,
      "code": "MOW",
      "name": "Шереметьево",
      "city": "Москва",
      "country": "Россия"
    },
    "arrival_airport": {
      "id": 2,
      "code": "SPB",
      "name": "Пулково",
      "city": "Санкт-Петербург",
      "country": "Россия"
    },
    "departure_time": "2024-12-20T10:00:00",
    "arrival_time": "2024-12-20T12:00:00",
    "total_seats": 150,
    "available_seats": 120,
    "price": 5000
  }
]
```

### 2. Создать новый рейс

```bash
curl -X POST http://localhost:8000/flights/ \
  -H "Content-Type: application/json" \
  -d '{
    "flight_number": "SU-456",
    "airline": "Aeroflot",
    "departure_airport_id": 1,
    "arrival_airport_id": 2,
    "departure_time": "2024-12-20T14:00:00",
    "arrival_time": "2024-12-20T16:00:00",
    "total_seats": 200,
    "available_seats": 200,
    "price": 6500
  }'
```

### 3. Получить определенный рейс

```bash
curl -X GET http://localhost:8000/flights/1
```

### 4. Обновить рейс

```bash
curl -X PUT http://localhost:8000/flights/1 \
  -H "Content-Type: application/json" \
  -d '{
    "available_seats": 100,
    "price": 5500
  }'
```

### 5. Удалить рейс

```bash
curl -X DELETE http://localhost:8000/flights/1
```

## Аэропорты (Airports)

### 1. Получить все аэропорты

```bash
curl -X GET http://localhost:8000/flights/airports/
```

**Ответ:**
```json
[
  {
    "id": 1,
    "code": "MOW",
    "name": "Шереметьево",
    "city": "Москва",
    "country": "Россия"
  }
]
```

### 2. создать аэропорт

```bash
curl -X POST http://localhost:8000/flights/airports/ \
  -H "Content-Type: application/json" \
  -d '{
    "code": "VVO",
    "name": "Коко",
    "city": "Владивосток",
    "country": "Россия"
  }'
```

### 3. Получить определенный аэропорт

```bash
curl -X GET http://localhost:8000/flights/airports/1
```

## Бронирования (Bookings)

### 1. Получить все бронирования

```bash
curl -X GET http://localhost:8000/bookings/
```

**Ответ:**
```json
[
  {
    "id": 1,
    "booking_number": "BK12345678",
    "flight_id": 1,
    "passenger_name": "Иван Петров",
    "passenger_email": "ivan@example.com",
    "passenger_phone": "+7 (999) 123-45-67",
    "seats_count": 1,
    "total_price": 5000,
    "status": "PENDING",
    "booking_status": "PENDING",
    "flight": {
      "id": 1,
      "flight_number": "SU-123",
      "airline": "Aeroflot",
      "departure_airport": {
        "code": "MOW",
        "name": "Шереметьево"
      },
      "arrival_airport": {
        "code": "SPB",
        "name": "Пулково"
      },
      "departure_time": "2024-12-20T10:00:00",
      "arrival_time": "2024-12-20T12:00:00",
      "available_seats": 120,
      "price": 5000
    }
  }
]
```

### 2. Создать бронирование

```bash
curl -X POST http://localhost:8000/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": 1,
    "passenger_name": "Николай Сидоров",
    "passenger_email": "nikolay@example.com",
    "passenger_phone": "+7 (999) 987-65-43",
    "seats_count": 2
  }'
```

**Ответ:**
```json
{
  "id": 2,
  "booking_number": "BK98765432",
  "flight_id": 1,
  "user_id": 1,
  "passenger_name": "Николай Сидоров",
  "passenger_email": "nikolay@example.com",
  "passenger_phone": "+7 (999) 987-65-43",
  "seats_count": 2,
  "total_price": 10000,
  "status": "PENDING"
}
```

### 3. Подтвердить бронирование

```bash
curl -X POST http://localhost:8000/bookings/1/confirm \
  -H "Content-Type: application/json"
```

### 4. Онновить татус бронирования

```bash
curl -X PUT http://localhost:8000/bookings/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "CONFIRMED"
  }'
```

### 5. Отменить бронирование

```bash
curl -X DELETE http://localhost:8000/bookings/1
```

## Платежи (Payments)

### 1. Создать платеж

```bash
curl -X POST http://localhost:8000/bookings/1/payment \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method": "credit_card"
  }'
```

### 2. Подтвердить платеж

```bash
curl -X POST http://localhost:8000/bookings/payment/1/confirm \
  -H "Content-Type: application/json"
```

## Эфикасность HTTP Статус коды

- **200 OK** - Успешный ПОЛУЧЕНИЕ данных
- **201 Created** - ресурс выведен успешно
- **204 No Content** - Отмена/Удаление операции окончена
- **400 Bad Request** - Неверные данные
- **404 Not Found** - ресурс не найден
- **500 Internal Server Error** - Ошибка сервера
