# Припарация и Охрана

## Обавление в настоящее время

### Охрана данных с Render.com

1. **Dockerfile для составления**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

2. **выдвижение**
```bash
# Подтвердите, что Dockerfile и .dockerignore находятся в корне репозитория

# Регистрируются в Render
# 1. Нажмите кнопку "+" и выберите "Web Service"
# 2. Прикрепите GitHub гит репозитория
# 3. Выберите этот репозитория
# 4. Тип среды: Docker
# 5. Настройки повторятся вашему локальному .env файлу
```

### Охрана данных с Heroku

1. **Procfile**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. **requirements.txt** исполэзуется файл

3. **пю гит в Heroku**
```bash
# Проверите Heroku CLI
heroku login

# Настройка Heroku гит исключения
heroku create krylia-online

# Поставите переменные окружения
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALGORITHM=HS256
heroku config:set ACCESS_TOKEN_EXPIRE_MINUTES=30
heroku config:set DB_NAME=production.db

# Отправить в Heroku
git push heroku main
```

### Охрана данных с PythonAnywhere

1. **Зарегистрируются домена**
2. **Грузим простые файлы**
3. **Настраиваем ПА Web app**
4. **Одна их многие WSGI апликации**

## Ничего деплоймента в Linux/Ubuntu

### Настройка

```bash
# Обновить ас доступ

sudo apt-get update
sudo apt-get upgrade -y

# Установить Python и nginx
sudo apt-get install python3.11 python3-pip nginx supervisor -y

# Клонировать репозитория
cd /var/www
sudo git clone https://github.com/Andrew766938/ANGELINA_FINAl.git
cd ANGELINA_FINAl

# Настроить виртуальные окружения
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Настройка Supervisor

Составить `/etc/supervisor/conf.d/krylia-online.conf`:

```ini
[program:krylia-online]
directory=/var/www/ANGELINA_FINAl
command=/var/www/ANGELINA_FINAl/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/krylia-online/error.log
stdout_logfile=/var/log/krylia-online/out.log
```

```bash
sudo systemctl restart supervisor
```

### Настройка Nginx

Составить `/etc/nginx/sites-available/krylia-online`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/ANGELINA_FINAl/static/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/krylia-online /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### Установка SSL сертификата с Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Охрана данных доктора

### Docker Compose для локального запуска

`docker-compose.yml`:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=your-secret-key
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
      - DB_NAME=/app/db/test.db
    volumes:
      - ./db:/app/db
    command: python main.py
```

```bash
docker-compose up
```

## Оптимизация для ПО

### 1. Производственные базы данных
- Перестають SQLite на PostgreSQL в производстве
- Поставить библиотеки `asyncpg` или `psycopg2`

### 2. Кеширование
- Поддержите Redis для кеширования
- Включите ETag для статических ассетов

### 3. Индексирование
- Поддержите индексы базы данных для оптимизации запросов

### 4. Настройка CORS
- Ограничите CORS только источникам, которые вам нужны

## Мониторинг

### Логирование
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Метрики
- Ставите Prometheus и Grafana для мониторинга

## Безопасность

- Никогда не равлиц SECRET_KEY в репозитория
- Обновить депенденции на сторонних аппликаций
- Выключите DEBUG в производстве
- Обновите HTTPS с SSL сертификата
