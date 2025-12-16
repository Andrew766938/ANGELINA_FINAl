"""Init demo data with 16 airports, 16 flights, 16 bookings

Revision ID: 002
Revises: 001
Create Date: 2025-12-16 11:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Таблица airports
    op.execute("""
        INSERT INTO airports (code, name, city, country) VALUES
        ('MOW', 'Шереметьево', 'Москва', 'Россия'),
        ('SPB', 'Пулково', 'Санкт-Петербург', 'Россия'),
        ('KZN', 'Казань', 'Казань', 'Россия'),
        ('SVX', 'Кольцово', 'Екатеринбург', 'Россия'),
        ('YKA', 'Площадь Ленина', 'Якутск', 'Россия'),
        ('LED', 'Пулково-2', 'Санкт-Петербург', 'Россия'),
        ('NOV', 'Новосибирск', 'Новосибирск', 'Россия'),
        ('VVO', 'Новый Владивосток', 'Владивосток', 'Россия'),
        ('OVB', 'Обь', 'Обь', 'Россия'),
        ('UUS', 'Южносахалинск', 'Южносахалинск', 'Россия'),
        ('TOE', 'Толяти', 'Толяти', 'Россия'),
        ('PEE', 'Пермь', 'Пермь', 'Россия'),
        ('TJM', 'Тюмень', 'Тюмень', 'Россия'),
        ('IGT', 'Иркутск', 'Иркутск', 'Россия'),
        ('ULY', 'Улан-Удэ', 'Улан-Удэ', 'Россия'),
        ('CHI', 'Чита', 'Чита', 'Россия')
    """)
    
    # Таблица flights (16 рейсов)
    now = datetime.utcnow()
    op.execute(f"""
        INSERT INTO flights (flight_number, airline, departure_airport_id, arrival_airport_id, departure_time, arrival_time, price, total_seats, available_seats, created_at) VALUES
        ('SU-001', 'Аэрофлот', 1, 2, '{now + timedelta(hours=1)}', '{now + timedelta(hours=3)}', 5500, 180, 180, '{now}'),
        ('SU-002', 'Аэрофлот', 2, 1, '{now + timedelta(hours=2)}', '{now + timedelta(hours=4)}', 5500, 180, 145, '{now}'),
        ('U6-100', 'Уральские авиалинии', 1, 3, '{now + timedelta(hours=3)}', '{now + timedelta(hours=5)}', 4800, 150, 150, '{now}'),
        ('UT-50', 'Ют-Аэр', 3, 4, '{now + timedelta(hours=4)}', '{now + timedelta(hours=6)}', 6200, 160, 160, '{now}'),
        ('S7-500', 'S7 Авиалинии', 2, 4, '{now + timedelta(hours=5)}', '{now + timedelta(hours=7)}', 7200, 120, 120, '{now}'),
        ('SU-003', 'Аэрофлот', 1, 5, '{now + timedelta(hours=6)}', '{now + timedelta(hours=12)}', 8500, 200, 200, '{now}'),
        ('FV-201', 'Финир аэро', 4, 2, '{now + timedelta(hours=7)}', '{now + timedelta(hours=9)}', 6800, 140, 140, '{now}'),
        ('A4-400', 'A4', 1, 6, '{now + timedelta(hours=8)}', '{now + timedelta(hours=10)}', 5200, 190, 190, '{now}'),
        ('R2-102', 'Русские авиалинии', 2, 3, '{now + timedelta(hours=9)}', '{now + timedelta(hours=11)}', 5800, 170, 170, '{now}'),
        ('FP-55', 'Фламинго', 3, 1, '{now + timedelta(hours=10)}', '{now + timedelta(hours=12)}', 5400, 160, 160, '{now}'),
        ('N1-555', 'Новые века', 1, 7, '{now + timedelta(hours=11)}', '{now + timedelta(hours=15)}', 7800, 210, 210, '{now}'),
        ('V1-888', 'Высота', 2, 8, '{now + timedelta(hours=12)}', '{now + timedelta(hours=18)}', 8200, 140, 140, '{now}'),
        ('E3-200', 'Экспресс', 1, 4, '{now + timedelta(hours=13)}', '{now + timedelta(hours=15)}', 6500, 150, 150, '{now}'),
        ('G5-777', 'Галактика', 3, 2, '{now + timedelta(hours=14)}', '{now + timedelta(hours=16)}', 5700, 180, 180, '{now}'),
        ('T4-999', 'Тандем', 4, 3, '{now + timedelta(hours=15)}', '{now + timedelta(hours=17)}', 4200, 120, 120, '{now}'),
        ('L7-333', 'Луч', 1, 9, '{now + timedelta(hours=16)}', '{now + timedelta(hours=20)}', 9200, 200, 200, '{now}')
    """)
    
    # Таблица bookings (16 бронирований)
    op.execute(f"""
        INSERT INTO bookings (user_id, flight_id, passenger_name, passenger_email, passenger_phone, booking_number, status, created_at) VALUES
        (1, 1, 'Иван Петров', 'ivan@example.com', '+7 999 111-00-01', 'BK-001', 'ПОДТВЕРЖдЕНО', '{now}'),
        (1, 2, 'Мария Сидорова', 'maria@example.com', '+7 999 222-00-02', 'BK-002', 'ПОДТВЕРЖДЕНО', '{now}'),
        (1, 3, 'Алексей Иванов', 'alex@example.com', '+7 999 333-00-03', 'BK-003', 'ЗАВЕРШЕНО', '{now}'),
        (1, 4, 'Елена Смирнова', 'elena@example.com', '+7 999 444-00-04', 'BK-004', 'ОЖИДАНИЕ', '{now}'),
        (1, 5, 'Сергей Федоров', 'sergey@example.com', '+7 999 555-00-05', 'BK-005', 'ПОДТВЕРЖДЕНО', '{now}'),
        (1, 6, 'Ольга Новикова', 'olga@example.com', '+7 999 666-00-06', 'BK-006', 'ПОДТВЕРЖДЕНО', '{now}'),
        (1, 7, 'Виктор Козлов', 'victor@example.com', '+7 999 777-00-07', 'BK-007', 'ЗАВЕРШЕНО', '{now}'),
        (1, 8, 'Екатерина Волкова', 'kate@example.com', '+7 999 888-00-08', 'BK-008', 'ПОДТВЕРЖДЕНО', '{now}'),
        (1, 9, 'Максим Соколов', 'max@example.com', '+7 999 900-00-09', 'BK-009', 'ОЖИДАНИЕ', '{now}'),
        (1, 10, 'Наталья Степанова', 'nata@example.com', '+7 999 101-00-10', 'BK-010', 'ПОДТВЕРЖДЕНО', '{now}'),
        (1, 11, 'Павел Морозов', 'pavel@example.com', '+7 999 202-00-11', 'BK-011', 'ЗАВЕРШЕНО', '{now}'),
        (1, 12, 'Анна Буланова', 'anna@example.com', '+7 999 303-00-12', 'BK-012', 'ПОДТВЕРЖДЕНО', '{now}'),
        (1, 13, 'Дмитрий Петров', 'dmitry@example.com', '+7 999 404-00-13', 'BK-013', 'ОЖИДАНИЕ', '{now}'),
        (1, 14, 'Валентина Соловьева', 'val@example.com', '+7 999 505-00-14', 'BK-014', 'ПОДТВЕРЖДЕНО', '{now}'),
        (1, 15, 'Руслан Кузнецов', 'ruslan@example.com', '+7 999 606-00-15', 'BK-015', 'ЗАВЕРШЕНО', '{now}'),
        (1, 16, 'Людмила Волохова', 'lyuda@example.com', '+7 999 707-00-16', 'BK-016', 'ПОДТВЕРЖДЕНО', '{now}')
    """)


def downgrade() -> None:
    op.execute("DELETE FROM bookings")
    op.execute("DELETE FROM flights")
    op.execute("DELETE FROM airports")
