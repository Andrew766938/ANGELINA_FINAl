/**
 * Гостевой режим - только просмотр
 */

function loginAsGuest() {
    currentUser = {
        name: 'Гость',
        email: 'guest@view.only',
        role: 'guest',
        loginTime: new Date().toLocaleString('ru-RU')
    };
    showApp();
    notify('👀 Вход в гостевом режиме (только просмотр)', 'success');
}

function isGuest() {
    return currentUser && currentUser.role === 'guest';
}

function applyGuestRestrictions() {
    if (!isGuest()) return;
    
    // Скрыть все кнопки действий для гостя
    const actionButtons = document.querySelectorAll('.btn-select, .btn-delete, .btn-primary');
    actionButtons.forEach(btn => {
        btn.style.display = 'none';
    });
    
    // Скрыть формы бронирования и создания
    const forms = document.querySelectorAll('#booking-form-section, #create-airport-section');
    forms.forEach(form => {
        form.style.display = 'none';
    });
    
    // Скрыть вкладку "Билеты" для гостя (нет своих билетов)
    const bookingsTab = document.querySelectorAll('.nav-btn')[2];
    if (bookingsTab) {
        bookingsTab.style.display = 'none';
    }
}
