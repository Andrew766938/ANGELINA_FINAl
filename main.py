import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.api.sample import router as sample_router
from app.api.auth import router as auth_router
from app.api.roles import router as role_router
from app.api.flights import router as flights_router
from app.api.bookings import router as bookings_router

app = FastAPI(
    title="Крылья онлайн - Система бронирования авиа билетов",
    description="API для системы бронирования авиа билетов",
    version="1.0.0"
)

# ============== CORS CONFIGURATION ==============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники для разработки
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все HTTP методы
    allow_headers=["*"],  # Разрешить все заголовки
)

# Подключаем все роутеры
app.include_router(sample_router)
app.include_router(auth_router)
app.include_router(role_router)
app.include_router(flights_router)
app.include_router(bookings_router)

# Монтируем статические файлы
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Маршрут для главной страницы
@app.get("/")
async def read_root():
    index_path = Path(__file__).parent / "templates" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Крылья онлайн - Добро пожаловать!"}

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
