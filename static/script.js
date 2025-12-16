// ============== CONFIGURATION ==============
const API_URL = 'http://localhost:8000';
let currentUser = null;
let selectedFlightId = null;
let allAirports = [];

// ============== AUTH FUNCTIONS ==============
function switchAuth() {
    document.getElementById('login-form').classList.toggle('active');
    document.getElementById('register-form').classList.toggle('active');
}

async function login() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    if (!email || !password) {
        showNotification('Заполните все поля', 'error');
        return;
    }
    
    currentUser = {
        id: Date.now(),
        email: email,
        name: email.split('@')[0],
        token: 'demo-token-' + Math.random()
    };
    
    localStorage.setItem('user', JSON.stringify(currentUser));
    showNotification('Добро пожаловать, ' + currentUser.name + '!', 'success');
    showMainApp();
}

async function register() {
    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    if (!name || !email || !password) {
        showNotification('Заполните все поля', 'error');
        return;
    }
    
    if (password.length < 6) {
        showNotification('Пароль должен быть минимум 6 символов', 'error');
        return;
    }
    
    currentUser = {
        id: Date.now(),
        email: email,
        name: name,
        token: 'demo-token-' + Math.random()
    };
    
    localStorage.setItem('user', JSON.stringify(currentUser));
    showNotification('Аккаунт создан! Добро пожаловать, ' + name + '!', 'success');
    showMainApp();
}

function demoLogin() {
    currentUser = {
        id: 1,
        email: 'demo@example.com',
        name: 'Демо пользователь',
        token: 'demo-token-demo'
    };
    
    localStorage.setItem('user', JSON.stringify(currentUser));
    showNotification('Вы вошли как демо пользователь', 'info');
    showMainApp();
}

function logout() {
    currentUser = null;
    localStorage.removeItem('user');
    document.getElementById('app-container').style.display = 'none';
    document.getElementById('auth-modal').style.display = 'flex';
    document.getElementById('auth-modal').classList.add('show-auth');
    showNotification('Вы вышли из аккаунта', 'info');
}

function showMainApp() {
    document.getElementById('auth-modal').style.display = 'none';
    document.getElementById('app-container').style.display = 'block';
    loadAirports();
    loadAllFlights();
}

// ============== AIRPORT FUNCTIONS ==============
async function loadAirports() {
    try {
        const response = await fetch(`${API_URL}/flights/airports/`);
        if (response.ok) {
            allAirports = await response.json();
            populateAirportSelects();
        }
    } catch (error) {
        console.error('Ошибка загрузки аэропортов:', error);
    }
}

function populateAirportSelects() {
    const fromSelect = document.getElementById('flight-from-airport');
    const toSelect = document.getElementById('flight-to-airport');
    
    fromSelect.innerHTML = '<option value="">Выберите аэропорт...</option>';
    toSelect.innerHTML = '<option value="">Выберите аэропорт...</option>';
    
    allAirports.forEach(airport => {
        const option1 = document.createElement('option');
        option1.value = airport.id;
        option1.textContent = `${airport.code} - ${airport.city}`;
        fromSelect.appendChild(option1);
        
        const option2 = document.createElement('option');
        option2.value = airport.id;
        option2.textContent = `${airport.code} - ${airport.city}`;
        toSelect.appendChild(option2);
    });
}

// ============== FLIGHT FUNCTIONS ==============
async function loadAllFlights() {
    try {
        const response = await fetch(`${API_URL}/flights/`);
        if (response.ok) {
            const flights = await response.json();
            displayManageFlights(flights);
        }
    } catch (error) {
        console.error('Ошибка загружки рейсов:', error);
    }
}

async function searchFlights() {
    const from = document.getElementById('search-from').value;
    const to = document.getElementById('search-to').value;
    const date = document.getElementById('search-date').value;
    
    if (!from || !to || !date) {
        showNotification('Заполните все поля поиска', 'error');
        return;
    }
    
    try {
        const fromAirport = allAirports.find(a => a.code.toUpperCase() === from.toUpperCase());
        const toAirport = allAirports.find(a => a.code.toUpperCase() === to.toUpperCase());
        
        if (!fromAirport || !toAirport) {
            showNotification('Аэропорт не найден. Используйте коды (например: MOW, SPB)', 'error');
            return;
        }
        
        const url = `${API_URL}/flights/?departure_airport_id=${fromAirport.id}&arrival_airport_id=${toAirport.id}&departure_date=${date}`;
        const response = await fetch(url);
        
        if (response.ok) {
            const flights = await response.json();
            displayFlights(flights);
        } else {
            showNotification('Ошибка при поиске рейсов', 'error');
        }
    } catch (error) {
        console.error('Ошибка поиска:', error);
        showNotification('Ошибка при поиске рейсов', 'error');
    }
}

function displayFlights(flights) {
    const container = document.getElementById('flights-list');
    
    if (flights.length === 0) {
        container.innerHTML = '<p class="empty-state">Рейсов не найдено</p>';
        return;
    }
    
    container.innerHTML = flights.map(flight => `
        <div class="flight-card">
            <div class="flight-header">
                <h3>${flight.flight_number}</h3>
                <span class="airline">${flight.airline}</span>
            </div>
            <div class="flight-info">
                <div class="route">
                    <strong>FROM</strong>
                    <span class="arrow">→</span>
                    <strong>TO</strong>
                </div>
                <div class="times">
                    <p>Вылет: ${new Date(flight.departure_time).toLocaleString('ru-RU')}</p>
                    <p>Прилет: ${new Date(flight.arrival_time).toLocaleString('ru-RU')}</p>
                </div>
                <div class="availability">
                    <p>Свободных мест: <strong>${flight.available_seats}/${flight.total_seats}</strong></p>
                    <p>Цена: <strong>${flight.price} руб.</strong></p>
                </div>
            </div>
            <button class="btn btn-primary" onclick="selectFlight(${flight.id})">Выбрать рейс</button>
        </div>
    `).join('');
}

function displayManageFlights(flights) {
    const container = document.getElementById('all-flights-list');
    
    if (flights.length === 0) {
        container.innerHTML = '<p class="empty-state">Нет рейсов в системе</p>';
        return;
    }
    
    container.innerHTML = flights.map(flight => `
        <div class="flight-card">
            <div class="flight-header">
                <h3>#${flight.id} - ${flight.flight_number}</h3>
                <span class="airline">${flight.airline}</span>
            </div>
            <div class="flight-info">
                <p>Вылет: ${new Date(flight.departure_time).toLocaleString('ru-RU')}</p>
                <p>Свободно: ${flight.available_seats}/${flight.total_seats} мест</p>
                <p>Цена: ${flight.price} руб.</p>
            </div>
            <button class="btn btn-danger" onclick="deleteFlight(${flight.id})">Удалить</button>
        </div>
    `).join('');
}

function selectFlight(flightId) {
    selectedFlightId = flightId;
    document.getElementById('booking-flight-id').value = flightId;
    document.getElementById('app-container').querySelector('[data-tab="bookings"]').click();
    showNotification('ID рейса установлен. Заполните данные пассажира и забронируйте', 'info');
}

async function addFlight() {
    const number = document.getElementById('flight-number').value;
    const airline = document.getElementById('flight-airline').value;
    const fromId = document.getElementById('flight-from-airport').value;
    const toId = document.getElementById('flight-to-airport').value;
    const departure = document.getElementById('flight-departure').value;
    const arrival = document.getElementById('flight-arrival').value;
    const seats = document.getElementById('flight-seats').value;
    const price = document.getElementById('flight-price').value;
    
    if (!number || !airline || !fromId || !toId || !departure || !arrival || !seats || !price) {
        showNotification('Заполните все поля', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/flights/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                flight_number: number,
                airline: airline,
                departure_airport_id: parseInt(fromId),
                arrival_airport_id: parseInt(toId),
                departure_time: new Date(departure).toISOString(),
                arrival_time: new Date(arrival).toISOString(),
                total_seats: parseInt(seats),
                available_seats: parseInt(seats),
                price: parseFloat(price)
            })
        });
        
        if (response.ok) {
            showNotification('Рейс успешно добавлен!', 'success');
            document.getElementById('flight-number').value = '';
            document.getElementById('flight-airline').value = '';
            document.getElementById('flight-seats').value = '';
            document.getElementById('flight-price').value = '';
            loadAllFlights();
        } else {
            showNotification('Ошибка при добавлении рейса', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка при добавлении рейса', 'error');
    }
}

async function deleteFlight(flightId) {
    if (!confirm('Вы уверены?')) return;
    
    try {
        const response = await fetch(`${API_URL}/flights/${flightId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Рейс удален', 'success');
            loadAllFlights();
        }
    } catch (error) {
        showNotification('Ошибка при удалении', 'error');
    }
}

// ============== BOOKING FUNCTIONS ==============
async function createBooking() {
    const flightId = document.getElementById('booking-flight-id').value;
    const name = document.getElementById('booking-name').value;
    const email = document.getElementById('booking-email').value;
    const phone = document.getElementById('booking-phone').value;
    
    if (!flightId || !name || !email || !phone) {
        showNotification('Заполните все поля', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/bookings/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                flight_id: parseInt(flightId),
                passenger_name: name,
                passenger_email: email,
                passenger_phone: phone,
                status: 'CONFIRMED'
            })
        });
        
        if (response.ok) {
            const booking = await response.json();
            showNotification(`Бронирование успешно! Номер: ${booking.booking_number}`, 'success');
            document.getElementById('booking-flight-id').value = '';
            document.getElementById('booking-name').value = '';
            document.getElementById('booking-email').value = '';
            document.getElementById('booking-phone').value = '';
        } else {
            showNotification('Ошибка при бронировании', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка при бронировании', 'error');
    }
}

// ============== AIRPORT MANAGEMENT ==============
async function addAirport() {
    const code = document.getElementById('airport-code').value.toUpperCase();
    const name = document.getElementById('airport-name').value;
    const city = document.getElementById('airport-city').value;
    const country = document.getElementById('airport-country').value;
    
    if (!code || !name || !city || !country) {
        showNotification('Заполните все поля', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/flights/airports`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, name, city, country })
        });
        
        if (response.ok) {
            showNotification('Аэропорт добавлен!', 'success');
            document.getElementById('airport-code').value = '';
            document.getElementById('airport-name').value = '';
            document.getElementById('airport-city').value = '';
            document.getElementById('airport-country').value = '';
            loadAirports();
        } else {
            showNotification('Ошибка при добавлении аэропорта', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка при добавлении аэропорта', 'error');
    }
}

// ============== UTILITY FUNCTIONS ==============
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification show-${type}`;
    
    setTimeout(() => {
        notification.className = 'notification';
    }, 4000);
}

// ============== TAB NAVIGATION ==============
document.addEventListener('DOMContentLoaded', function() {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        showMainApp();
    }
    
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            
            this.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        });
    });
    
    document.getElementById('login-btn').addEventListener('click', login);
    document.getElementById('register-btn').addEventListener('click', register);
    document.getElementById('demo-btn').addEventListener('click', demoLogin);
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    document.getElementById('search-btn').addEventListener('click', searchFlights);
    document.getElementById('create-booking-btn').addEventListener('click', createBooking);
    document.getElementById('add-flight-btn').addEventListener('click', addFlight);
    document.getElementById('add-airport-btn').addEventListener('click', addAirport);
    
    document.getElementById('login-email').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') login();
    });
    document.getElementById('login-password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') login();
    });
});
