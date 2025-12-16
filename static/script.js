const API_BASE_URL = 'http://localhost:8000';
let selectedFlightForBooking = null;
let allAirports = [];

// Нотификация
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Навигация по вкладкам
function initializeTabs() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');
            
            // Отключим все табы
            tabContents.forEach(tab => tab.classList.remove('active'));
            navBtns.forEach(b => b.classList.remove('active'));
            
            // Включаем выбранный таб
            document.getElementById(tabName).classList.add('active');
            btn.classList.add('active');
            
            if (tabName === 'manage') {
                loadAllFlights();
                loadAirportsForSelect();
            }
        });
    });
}

// Причализация
function initializeEventListeners() {
    // Поиск рейсов
    document.getElementById('search-btn').addEventListener('click', searchFlights);
    
    // Отображение всех рейсов
    document.getElementById('search-from').addEventListener('input', (e) => {
        if (e.target.value.length > 0) {
            searchAirports(e.target.value, 'from');
        }
    });
    
    document.getElementById('search-to').addEventListener('input', (e) => {
        if (e.target.value.length > 0) {
            searchAirports(e.target.value, 'to');
        }
    });
    
    // Выбор аэропорта
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('airport-item')) {
            const code = e.target.getAttribute('data-code');
            const field = e.target.getAttribute('data-field');
            
            if (field === 'from') {
                document.getElementById('search-from').value = code;
                document.getElementById('from-airports').classList.remove('show');
            } else if (field === 'to') {
                document.getElementById('search-to').value = code;
                document.getElementById('to-airports').classList.remove('show');
            }
        }
    });
    
    // Создание бронирования
    document.getElementById('create-booking-btn').addEventListener('click', createBooking);
    
    // Добавление аэропорта
    document.getElementById('add-airport-btn').addEventListener('click', addAirport);
    
    // Добавление рейса
    document.getElementById('add-flight-btn').addEventListener('click', addFlight);
    
    // Модальное окно
    const modal = document.getElementById('flight-modal');
    const closeBtn = modal.querySelector('.close');
    
    closeBtn.addEventListener('click', () => {
        modal.classList.remove('show');
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
        }
    });
}

// Поиск аэропортов
async function searchAirports(query, field) {
    try {
        const response = await fetch(`${API_BASE_URL}/flights/airports`);
        const airports = await response.json();
        
        const filtered = airports.filter(a => 
            a.code.toUpperCase().includes(query.toUpperCase()) ||
            a.name.toUpperCase().includes(query.toUpperCase())
        );
        
        const container = document.getElementById(`${field}-airports`);
        container.innerHTML = '';
        
        filtered.forEach(airport => {
            const item = document.createElement('div');
            item.className = 'airport-item';
            item.setAttribute('data-code', airport.code);
            item.setAttribute('data-field', field);
            item.innerHTML = `
                <div class="airport-item-code">${airport.code}</div>
                <div class="airport-item-name">${airport.name}, ${airport.city}</div>
            `;
            container.appendChild(item);
        });
        
        if (filtered.length > 0) {
            container.classList.add('show');
        } else {
            container.classList.remove('show');
        }
    } catch (error) {
        console.error('Error searching airports:', error);
    }
}

// Поиск рейсов
async function searchFlights() {
    const fromCode = document.getElementById('search-from').value;
    const toCode = document.getElementById('search-to').value;
    const date = document.getElementById('search-date').value;
    
    if (!fromCode || !toCode) {
        showNotification('Пожалуйста, выберите аэропорты', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/flights/`);
        const flights = await response.json();
        
        // Фильтруем рейсы
        let filtered = flights.filter(f => 
            f.departure_airport.code === fromCode.toUpperCase() &&
            f.arrival_airport.code === toCode.toUpperCase()
        );
        
        if (date) {
            const selectedDate = new Date(date).toDateString();
            filtered = filtered.filter(f => {
                const departureDate = new Date(f.departure_time).toDateString();
                return departureDate === selectedDate;
            });
        }
        
        displayFlights(filtered, 'flights-list');
        
        if (filtered.length === 0) {
            showNotification('Не найдено рейсов по вашим критериям', 'info');
        } else {
            showNotification(`Найдено ${filtered.length} рейсов`, 'success');
        }
    } catch (error) {
        console.error('Error searching flights:', error);
        showNotification('Ошибка поиска рейсов', 'error');
    }
}

// Отображение рейсов
function displayFlights(flights, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (flights.length === 0) {
        container.innerHTML = '<p class="empty-state">Нет авайлыных рейсов</p>';
        return;
    }
    
    flights.forEach(flight => {
        const departureTime = new Date(flight.departure_time);
        const arrivalTime = new Date(flight.arrival_time);
        const duration = Math.round((arrivalTime - departureTime) / (1000 * 60));
        
        const card = document.createElement('div');
        card.className = 'flight-card';
        card.innerHTML = `
            <h4>${flight.flight_number} - ${flight.airline}</h4>
            <div class="flight-route">
                <span class="flight-airport">${flight.departure_airport.code}</span>
                ✈️
                <span class="flight-airport">${flight.arrival_airport.code}</span>
            </div>
            <div class="flight-info">
                <div class="flight-info-item">
                    <span class="flight-info-label">Вылет</span>
                    <span class="flight-info-value">${departureTime.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'})}</span>
                </div>
                <div class="flight-info-item">
                    <span class="flight-info-label">Прилет</span>
                    <span class="flight-info-value">${arrivalTime.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'})}</span>
                </div>
            </div>
            <div class="flight-details">
                <div class="detail-item">
                    <div class="detail-label">Но полету</div>
                    <div class="detail-value">${Math.floor(duration / 60)}h ${duration % 60}m</div>
                </div>
                <div class="detail-item">
                    <span class="seats-badge">Мест: ${flight.available_seats}</span>
                </div>
            </div>
            <div class="price-badge">₽ ${flight.price.toLocaleString('ru-RU')}</div>
        `;
        
        card.addEventListener('click', () => showFlightModal(flight));
        container.appendChild(card);
    });
}

// Модаль деталей рейса
function showFlightModal(flight) {
    selectedFlightForBooking = flight;
    const modal = document.getElementById('flight-modal');
    const details = document.getElementById('modal-flight-details');
    
    const departureTime = new Date(flight.departure_time);
    const arrivalTime = new Date(flight.arrival_time);
    
    details.innerHTML = `
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <p><strong>Номер рейса:</strong> ${flight.flight_number}</p>
            <p><strong>Авиакомпания:</strong> ${flight.airline}</p>
            <p><strong>Маршрут:</strong> ${flight.departure_airport.code} → ${flight.arrival_airport.code}</p>
            <p><strong>Вылет:</strong> ${departureTime.toLocaleString('ru-RU')}</p>
            <p><strong>Прилет:</strong> ${arrivalTime.toLocaleString('ru-RU')}</p>
            <p><strong>Доступно мест:</strong> ${flight.available_seats}/${flight.total_seats}</p>
            <p style="color: #f5576c; font-size: 18px; font-weight: bold;">Цена: ₽ ${flight.price.toLocaleString('ru-RU')}</p>
        </div>
    `;
    
    document.getElementById('modal-book-btn').onclick = () => {
        modal.classList.remove('show');
        document.querySelector('[data-tab="bookings"]').click();
    };
    
    modal.classList.add('show');
}

// Нагружение всех рейсов для управления
async function loadAllFlights() {
    try {
        const response = await fetch(`${API_BASE_URL}/flights/`);
        const flights = await response.json();
        displayFlights(flights, 'all-flights-list');
    } catch (error) {
        console.error('Error loading flights:', error);
    }
}

// Нагружение аэропортов для селектов
async function loadAirportsForSelect() {
    try {
        const response = await fetch(`${API_BASE_URL}/flights/airports`);
        allAirports = await response.json();
        
        const fromSelect = document.getElementById('flight-from-airport');
        const toSelect = document.getElementById('flight-to-airport');
        
        allAirports.forEach(airport => {
            const option1 = document.createElement('option');
            option1.value = airport.id;
            option1.textContent = `${airport.code} - ${airport.name}`;
            fromSelect.appendChild(option1);
            
            const option2 = document.createElement('option');
            option2.value = airport.id;
            option2.textContent = `${airport.code} - ${airport.name}`;
            toSelect.appendChild(option2);
        });
    } catch (error) {
        console.error('Error loading airports:', error);
    }
}

// Добавление аэропорта
async function addAirport() {
    const code = document.getElementById('airport-code').value;
    const name = document.getElementById('airport-name').value;
    const city = document.getElementById('airport-city').value;
    const country = document.getElementById('airport-country').value;
    
    if (!code || !name || !city || !country) {
        showNotification('Пожалуйста, заполните все поля', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/flights/airports`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code,
                name,
                city,
                country
            })
        });
        
        if (response.ok) {
            showNotification('Аэропорт добавлен успешно!', 'success');
            document.getElementById('airport-code').value = '';
            document.getElementById('airport-name').value = '';
            document.getElementById('airport-city').value = '';
            document.getElementById('airport-country').value = '';
            loadAirportsForSelect();
        } else {
            const error = await response.json();
            showNotification(сerror.detail || 'Ошибка при добавлении аэропорта', 'error');
        }
    } catch (error) {
        console.error('Error adding airport:', error);
        showNotification('Ошибка при добавлении аэропорта', 'error');
    }
}

// Добавление рейса
async function addFlight() {
    const flightNumber = document.getElementById('flight-number').value;
    const airline = document.getElementById('flight-airline').value;
    const fromAirport = document.getElementById('flight-from-airport').value;
    const toAirport = document.getElementById('flight-to-airport').value;
    const departure = document.getElementById('flight-departure').value;
    const arrival = document.getElementById('flight-arrival').value;
    const seats = document.getElementById('flight-seats').value;
    const price = document.getElementById('flight-price').value;
    
    if (!flightNumber || !airline || !fromAirport || !toAirport || !departure || !arrival || !seats || !price) {
        showNotification('Пожалуйста, заполните все поля', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/flights/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                flight_number: flightNumber,
                airline,
                departure_airport_id: parseInt(fromAirport),
                arrival_airport_id: parseInt(toAirport),
                departure_time: new Date(departure).toISOString(),
                arrival_time: new Date(arrival).toISOString(),
                total_seats: parseInt(seats),
                available_seats: parseInt(seats),
                price: parseFloat(price)
            })
        });
        
        if (response.ok) {
            showNotification('Рейс добавлен успешно!', 'success');
            document.getElementById('flight-number').value = '';
            document.getElementById('flight-airline').value = '';
            document.getElementById('flight-from-airport').value = '';
            document.getElementById('flight-to-airport').value = '';
            document.getElementById('flight-departure').value = '';
            document.getElementById('flight-arrival').value = '';
            document.getElementById('flight-seats').value = '';
            document.getElementById('flight-price').value = '';
            loadAllFlights();
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Ошибка при добавлении рейса', 'error');
        }
    } catch (error) {
        console.error('Error adding flight:', error);
        showNotification('Ошибка при добавлении рейса', 'error');
    }
}

// Создание бронирования
async function createBooking() {
    const flightId = document.getElementById('booking-flight-id').value;
    const passengerName = document.getElementById('booking-name').value;
    const passengerEmail = document.getElementById('booking-email').value;
    const passengerPhone = document.getElementById('booking-phone').value;
    
    if (!flightId || !passengerName || !passengerEmail || !passengerPhone) {
        showNotification('Пожалуйста, заполните все поля', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/bookings/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                flight_id: parseInt(flightId),
                passenger_name: passengerName,
                passenger_email: passengerEmail,
                passenger_phone: passengerPhone
            })
        });
        
        if (response.ok) {
            showNotification('Бронирование сохранено успешно!', 'success');
            document.getElementById('booking-flight-id').value = '';
            document.getElementById('booking-name').value = '';
            document.getElementById('booking-email').value = '';
            document.getElementById('booking-phone').value = '';
            loadMyBookings();
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Ошибка при сохранении бронирования', 'error');
        }
    } catch (error) {
        console.error('Error creating booking:', error);
        showNotification('Ошибка при сохранении бронирования', 'error');
    }
}

// Нагружение моих бронирований
async function loadMyBookings() {
    try {
        const response = await fetch(`${API_BASE_URL}/bookings/`);
        const bookings = await response.json();
        
        const container = document.getElementById('my-bookings-list');
        container.innerHTML = '';
        
        if (bookings.length === 0) {
            container.innerHTML = '<p class="empty-state">У вас нет бронирований</p>';
            return;
        }
        
        bookings.forEach(booking => {
            const card = document.createElement('div');
            card.className = 'booking-card';
            card.innerHTML = `
                <h4>ID: ${booking.id}</h4>
                <p><strong>Пассажир:</strong> ${booking.passenger_name}</p>
                <p><strong>Email:</strong> ${booking.passenger_email}</p>
                <p><strong>Телефон:</strong> ${booking.passenger_phone}</p>
                <p><strong>Рейс:</strong> ${booking.flight.flight_number}</p>
                <p><strong>Статус:</strong> <span class="status-badge status-${booking.booking_status.toLowerCase()}">${booking.booking_status}</span></p>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

// Нициализация при загружке страницы
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeEventListeners();
});
