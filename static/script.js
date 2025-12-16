// API Base URL
const API_BASE = 'http://localhost:8000';

// Global state
let currentUser = null;
let selectedFlight = null;
let airports = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAirports();
    checkAuth();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const bookingForm = document.getElementById('bookingForm');
    const addFlightForm = document.getElementById('addFlightForm');
    const addAirportForm = document.getElementById('addAirportForm');

    if (loginForm) loginForm.addEventListener('submit', handleLogin);
    if (registerForm) registerForm.addEventListener('submit', handleRegister);
    if (bookingForm) bookingForm.addEventListener('submit', handleBooking);
    if (addFlightForm) addFlightForm.addEventListener('submit', handleAddFlight);
    if (addAirportForm) addAirportForm.addEventListener('submit', handleAddAirport);
}

// AUTH FUNCTIONS
function openAuthModal() {
    if (currentUser) return;
    document.getElementById('authModal').classList.add('show');
}

function closeAuthModal() {
    document.getElementById('authModal').classList.remove('show');
}

function switchTab(tab) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    const tabEl = document.getElementById(tab + 'Tab');
    if (tabEl) tabEl.classList.add('active');
    if (event && event.target) event.target.classList.add('active');
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            currentUser = { email, id: data.user_id, role: data.role };
            closeAuthModal();
            updateUI();
            showNotification('Successfully logged in!', 'success');
            loadMyBookings();
        } else {
            showNotification(data.detail || 'Login error', 'error');
        }
    } catch (error) {
        showNotification('Connection error', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;

    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();
        if (response.ok) {
            showNotification('Registration successful! Now login', 'success');
            switchTab('login');
        } else {
            showNotification(data.detail || 'Registration error', 'error');
        }
    } catch (error) {
        showNotification('Connection error', 'error');
    }
}

function handleLogout() {
    localStorage.removeItem('token');
    currentUser = null;
    updateUI();
    showNotification('You logged out', 'success');
}

function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        currentUser = { token };
    }
    updateUI();
}

function updateUI() {
    const authBtn = document.getElementById('authBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    if (currentUser) {
        if (authBtn) authBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'block';
    } else {
        if (authBtn) authBtn.style.display = 'block';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

// AIRPORTS
async function loadAirports() {
    try {
        const response = await fetch(`${API_BASE}/flights/airports`);
        if (response.ok) {
            airports = await response.json();
            populateAirportSelects();
        }
    } catch (error) {
        console.error('Error loading airports:', error);
    }
}

function populateAirportSelects() {
    const selects = ['departureAirport', 'arrivalAirport', 'adminDeparture', 'adminArrival'];
    
    selects.forEach(id => {
        const select = document.getElementById(id);
        if (select) {
            select.innerHTML = '<option value="">Select airport</option>';
            airports.forEach(airport => {
                const option = document.createElement('option');
                option.value = airport.id;
                option.textContent = `${airport.code} - ${airport.name}`;
                select.appendChild(option);
            });
        }
    });
}

// SEARCH FLIGHTS
async function searchFlights() {
    const departureId = document.getElementById('departureAirport').value;
    const arrivalId = document.getElementById('arrivalAirport').value;
    const date = document.getElementById('departureDate').value;

    if (!departureId || !arrivalId || !date) {
        showNotification('Fill all search fields', 'warning');
        return;
    }

    try {
        const params = new URLSearchParams({
            departure_airport_id: departureId,
            arrival_airport_id: arrivalId,
            departure_date: date
        });

        const response = await fetch(`${API_BASE}/flights/?${params}`);
        if (response.ok) {
            const flights = await response.json();
            displayFlights(flights);
            document.getElementById('searchResults').scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        showNotification('Search error', 'error');
    }
}

function displayFlights(flights) {
    const grid = document.getElementById('flightsGrid');
    
    if (flights.length === 0) {
        grid.innerHTML = '<p class="empty-state">No flights found</p>';
        return;
    }

    grid.innerHTML = flights.map(flight => `
        <div class="flight-card" onclick="openFlightDetails(${flight.id})">
            <div class="flight-header">
                <span class="flight-number">${flight.flight_number}</span>
                <span class="flight-price">$${flight.price}</span>
            </div>
            
            <div class="flight-route">
                <span class="airport-code">${flight.departure_airport.code}</span>
                <span class="arrow">→</span>
                <span class="airport-code">${flight.arrival_airport.code}</span>
            </div>

            <div class="flight-details-line">
                <span>${flight.departure_airport.city}</span>
                <span>${flight.arrival_airport.city}</span>
            </div>

            <div class="flight-details-line">
                <span>${formatTime(flight.departure_time)}</span>
                <span>${formatTime(flight.arrival_time)}</span>
            </div>

            <div class="available-seats ${flight.available_seats < 5 ? 'low' : ''}">
                ✓ Available: ${flight.available_seats}
            </div>
        </div>
    `).join('');
}

async function openFlightDetails(flightId) {
    if (!currentUser) {
        showNotification('Please login first', 'warning');
        openAuthModal();
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/flights/${flightId}`);
        if (response.ok) {
            selectedFlight = await response.json();
            displayFlightModal();
            document.getElementById('flightModal').classList.add('show');
        }
    } catch (error) {
        showNotification('Error loading flight details', 'error');
    }
}

function displayFlightModal() {
    const flight = selectedFlight;
    const details = document.getElementById('flightDetails');
    
    details.innerHTML = `
        <div class="flight-detail-row">
            <span>Flight:</span>
            <strong>${flight.flight_number}</strong>
        </div>
        <div class="flight-detail-row">
            <span>Airline:</span>
            <strong>${flight.airline}</strong>
        </div>
        <div class="flight-detail-row">
            <span>From:</span>
            <strong>${flight.departure_airport.code} - ${flight.departure_airport.name}</strong>
        </div>
        <div class="flight-detail-row">
            <span>To:</span>
            <strong>${flight.arrival_airport.code} - ${flight.arrival_airport.name}</strong>
        </div>
        <div class="flight-detail-row">
            <span>Departure:</span>
            <strong>${formatFullTime(flight.departure_time)}</strong>
        </div>
        <div class="flight-detail-row">
            <span>Arrival:</span>
            <strong>${formatFullTime(flight.arrival_time)}</strong>
        </div>
        <div class="flight-detail-row">
            <span>Price:</span>
            <strong>$${flight.price}</strong>
        </div>
        <div class="flight-detail-row">
            <span>Available seats:</span>
            <strong>${flight.available_seats}/${flight.total_seats}</strong>
        </div>
    `;
}

function closeFlightModal() {
    document.getElementById('flightModal').classList.remove('show');
}

// BOOKING
async function handleBooking(e) {
    e.preventDefault();
    
    if (!currentUser) {
        showNotification('Must login first', 'error');
        return;
    }

    const bookingData = {
        flight_id: selectedFlight.id,
        passenger_name: document.getElementById('passengerName').value,
        passenger_email: document.getElementById('passengerEmail').value,
        passenger_phone: document.getElementById('passengerPhone').value,
        seats_count: parseInt(document.getElementById('seatsCount').value)
    };

    try {
        const response = await fetch(`${API_BASE}/bookings/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(bookingData)
        });

        if (response.ok) {
            const booking = await response.json();
            showNotification(`Booking successful! Number: ${booking.booking_number}`, 'success');
            closeFlightModal();
            document.getElementById('bookingForm').reset();
            loadMyBookings();
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Booking error', 'error');
        }
    } catch (error) {
        showNotification('Connection error', 'error');
    }
}

// MY BOOKINGS
async function loadMyBookings() {
    if (!currentUser) {
        document.getElementById('bookingsList').innerHTML = 
            '<p class="empty-state">Please login to view your bookings</p>';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/bookings/me`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            const bookings = await response.json();
            displayBookings(bookings);
        }
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

function displayBookings(bookings) {
    const list = document.getElementById('bookingsList');
    
    if (bookings.length === 0) {
        list.innerHTML = '<p class="empty-state">No bookings yet</p>';
        return;
    }

    list.innerHTML = bookings.map(booking => `
        <div class="booking-card">
            <span class="booking-status status-${booking.status}">${booking.status.toUpperCase()}</span>
            
            <div class="booking-info">
                <label>Booking Number:</label>
                <div>${booking.booking_number}</div>
            </div>
            
            <div class="booking-info">
                <label>Passenger:</label>
                <div>${booking.passenger_name}</div>
            </div>
            
            <div class="booking-info">
                <label>Seats:</label>
                <div>${booking.seats_count}</div>
            </div>
            
            <div class="booking-info">
                <label>Total:</label>
                <div style="font-size: 1.2em; color: var(--primary-blue); font-weight: 700;">$${booking.total_price}</div>
            </div>

            <div class="booking-actions">
                ${booking.status === 'pending' ? `
                    <button class="btn-confirm" onclick="confirmBooking(${booking.id})">Confirm</button>
                    <button class="btn-cancel" onclick="cancelBooking(${booking.id})">Cancel</button>
                ` : ''}
                ${booking.status === 'confirmed' ? `
                    <button class="btn-cancel" onclick="cancelBooking(${booking.id})">Cancel</button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

async function confirmBooking(bookingId) {
    try {
        const response = await fetch(`${API_BASE}/bookings/${bookingId}/confirm`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            showNotification('Booking confirmed!', 'success');
            loadMyBookings();
        }
    } catch (error) {
        showNotification('Confirmation error', 'error');
    }
}

async function cancelBooking(bookingId) {
    if (!confirm('Cancel booking?')) return;

    try {
        const response = await fetch(`${API_BASE}/bookings/${bookingId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            showNotification('Booking cancelled', 'success');
            loadMyBookings();
        }
    } catch (error) {
        showNotification('Cancellation error', 'error');
    }
}

// ADMIN PANEL
function openAdminModal() {
    if (!currentUser || currentUser.role !== 'admin') {
        showNotification('No admin access', 'error');
        return;
    }
    document.getElementById('adminModal').classList.add('show');
}

function closeAdminModal() {
    document.getElementById('adminModal').classList.remove('show');
}

function switchAdminTab(tab) {
    document.querySelectorAll('.admin-tab').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.admin-tabs .tab-btn').forEach(el => el.classList.remove('active'));
    const tabEl = document.getElementById('admin' + tab.charAt(0).toUpperCase() + tab.slice(1));
    if (tabEl) tabEl.classList.add('active');
    if (event && event.target) event.target.classList.add('active');
}

async function handleAddFlight(e) {
    e.preventDefault();

    const flightData = {
        flight_number: document.getElementById('flightNumber').value,
        airline: document.getElementById('airline').value,
        departure_airport_id: parseInt(document.getElementById('adminDeparture').value),
        arrival_airport_id: parseInt(document.getElementById('adminArrival').value),
        departure_time: document.getElementById('departureTime').value,
        arrival_time: document.getElementById('arrivalTime').value,
        total_seats: parseInt(document.getElementById('totalSeats').value),
        available_seats: parseInt(document.getElementById('availableSeats').value),
        price: parseFloat(document.getElementById('price').value)
    };

    try {
        const response = await fetch(`${API_BASE}/flights/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(flightData)
        });

        if (response.ok) {
            showNotification('Flight added successfully!', 'success');
            document.getElementById('addFlightForm').reset();
        }
    } catch (error) {
        showNotification('Error adding flight', 'error');
    }
}

async function handleAddAirport(e) {
    e.preventDefault();

    const airportData = {
        code: document.getElementById('airportCode').value.toUpperCase(),
        name: document.getElementById('airportName').value,
        city: document.getElementById('airportCity').value,
        country: document.getElementById('airportCountry').value
    };

    try {
        const response = await fetch(`${API_BASE}/flights/airports`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(airportData)
        });

        if (response.ok) {
            showNotification('Airport added successfully!', 'success');
            document.getElementById('addAirportForm').reset();
            loadAirports();
        }
    } catch (error) {
        showNotification('Error adding airport', 'error');
    }
}

// UTILITIES
function formatTime(datetime) {
    const date = new Date(datetime);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function formatFullTime(datetime) {
    const date = new Date(datetime);
    return date.toLocaleString('en-US');
}

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification show ${type}`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Close modal on outside click
window.onclick = function(event) {
    const authModal = document.getElementById('authModal');
    const flightModal = document.getElementById('flightModal');
    const adminModal = document.getElementById('adminModal');

    if (event.target === authModal) {
        closeAuthModal();
    }
    if (event.target === flightModal) {
        closeFlightModal();
    }
    if (event.target === adminModal) {
        closeAdminModal();
    }
};
