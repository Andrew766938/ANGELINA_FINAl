# 👀 Гостевой режим - Инструкция по интеграции

## Шаг 1: Добавьте скрипт в HTML

В `templates/index.html`, перед закрывающим тегом `</head>` добавьте:

```html
<script src="/static/guest_mode.js"></script>
```

## Шаг 2: Добавьте кнопку "Войти как гость"

В `templates/index.html`, после кнопки `🔐 ВОЙТИ` добавьте:

```html
<button class="btn-auth" onclick="login()">🔐 ВОЙТИ</button>
<button class="btn-guest" onclick="loginAsGuest()">👀 ВОЙТИ КАК ГОСТЬ</button> <!-- НОВОЕ -->
<p class="auth-link">Нет аккаунта? <a onclick="switchAuthForm()">Зарегистрироваться</a></p>
```

## Шаг 3: Обновите функцию showApp()

В `<script>` секции, добавьте вызов `applyGuestRestrictions()` в конец функции `showApp()`:

```javascript
async function showApp() {
    document.getElementById('auth-modal').classList.add('hidden');
    document.getElementById('app').classList.remove('hidden');
    updateAccountTab();
    
    if (currentUser.role === 'admin') {
        document.getElementById('create-airport-section').style.display = 'block';
    } else {
        document.getElementById('create-airport-section').style.display = 'none';
    }
    
    await loadAllFlights();
    await loadAllAirports();
    await loadMyBookings();
    
    // 👀 ПРИМЕНЯЕМ ОГРАНИЧЕНИЯ ДЛЯ ГОСТЯ
    applyGuestRestrictions();
}
```

## Шаг 4: Обновите renderFlights()

В функции `renderFlights()`, измените кнопку бронирования:

```javascript
list.innerHTML = cachedFlights.map(f => {
    const bookBtn = isGuest() 
        ? '<p style="color: #a0aec0; font-size: 13px; margin-top: 10px;">👀 Гостевой режим - только просмотр</p>'
        : `<button class="btn-select" onclick="selectFlight(${f.id}, '${f.flight_number}', ${f.departure_airport_id}, ${f.arrival_airport_id}, ${f.price})"> 🎟️ ЗАБРОНИРОВАТЬ</button>`;
    
    return `
        <div class="card">
            <h3>${f.flight_number}</h3>
            <p><strong>🎫 ${f.airline}</strong></p>
            <p><strong>📍 Маршрут:</strong> ${f.departure_airport.city} (${f.departure_airport.code}) ➡️ ${f.arrival_airport.city} (${f.arrival_airport.code})</p>
            <p><strong>⏰ Вылет:</strong> ${new Date(f.departure_time).toLocaleString('ru-RU')}</p>
            <p><strong>💰 Цена:</strong> <span style="color: #48bb78; font-weight: 700;">₽${f.price}</span></p>
            <p><strong>💺 Места:</strong> ${f.available_seats}/${f.total_seats}</p>
            ${bookBtn}
        </div>
    `;
}).join('');
```

## Шаг 5: Обновите renderAirports()

В функции `renderAirports()`:

```javascript
list.innerHTML = cachedAirports.map(a => {
    let deleteBtn = '';
    // Только админы, не гости!
    if (currentUser && currentUser.role === 'admin' && !isGuest()) {
        deleteBtn = `<button class="btn-delete" onclick="deleteAirport(${a.id}, '${a.code}')" style="background: #f56565; color: white; margin-top: 10px; width: 100%;">🗑️ УДАЛИТЬ</button>`;
    }
    return `
        <div class="card">
            <h3>✈️ ${a.code}</h3>
            <p><strong>${a.name}</strong></p>
            <p><strong>🏢 Город:</strong> ${a.city}</p>
            <p><strong>🌍 Страна:</strong> ${a.country}</p>
            ${deleteBtn}
        </div>
    `;
}).join('');
```

## Шаг 6: Обновите renderBookings()

В функции `renderBookings()`:

```javascript
list.innerHTML = cachedBookings.map(b => {
    const flight = cachedFlights.find(f => f.id === b.flight_id);
    
    let deleteBtn = '';
    // Только админы, не гости!
    if (currentUser && currentUser.role === 'admin' && !isGuest()) {
        deleteBtn = `<button class="btn-delete" onclick="deleteBooking(${b.id}, '${b.booking_number || b.id}')" style="background: #f56565; color: white; margin-top: 10px; width: 100%;">🗑️ УДАЛИТЬ</button>`;
    }
    
    return `
        <div class="card-flip-container">
            <div class="card-flip">
                <div class="card-front">
                    <h3>🎫 №${b.booking_number || b.id}</h3>
                    <p><strong>👤 Пассажир:</strong> ${b.passenger_name}</p>
                    <p><strong>✈️ Рейс:</strong> ${flight?.flight_number || '-'} (${flight?.airline || '-'})</p>
                    <p><strong>🏢 Вылет из:</strong> ${flight?.departure_airport.name || '-'}, ${flight?.departure_airport.city || '-'}</p>
                    <p><strong>🏢 Прилёт в:</strong> ${flight?.arrival_airport.name || '-'}, ${flight?.arrival_airport.city || '-'}</p>
                    <p><strong>📧 Email:</strong> ${b.passenger_email}</p>
                    <p><strong>📱 Телефон:</strong> ${b.passenger_phone}</p>
                    <p><strong>💺 Мест:</strong> ${b.seats_count || 1}</p>
                    <p><strong>✅ Статус:</strong> <span style="color: #48bb78; font-weight: 700;">${b.status || 'pending'}</span></p>
                    ${deleteBtn}
                </div>
            </div>
        </div>
    `;
}).join('');
```

## Шаг 7: Обновите updateAccountTab()

В функции `updateAccountTab()`:

```javascript
function updateAccountTab() {
    if (!currentUser) return;
    document.getElementById('acc-name').textContent = currentUser.name;
    document.getElementById('acc-email').textContent = currentUser.email;
    
    let roleText = '👤 Пользователь';
    if (currentUser.role === 'admin') roleText = '👑 Администратор';
    if (currentUser.role === 'guest') roleText = '👀 Гость (только просмотр)';
    
    document.getElementById('acc-role').textContent = roleText;
    document.getElementById('acc-date').textContent = currentUser.loginTime;
}
```

## Результат

После применения всех изменений:

✅ Кнопка "👀 ВОЙТИ КАК ГОСТЬ" на экране входа
✅ Гость видит только рейсы и аэропорты
✅ Все кнопки бронирования/создания/удаления скрыты
✅ Вкладка "🎫 Билеты" скрыта для гостей
✅ В профиле показывается "👀 Гость (только просмотр)"
