"""Главный модуль FastAPI приложения"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.bookings import router as bookings_router
from app.kafka.producer import kafka_producer
from app.db.database import engine
from app.models import Booking, Restaurant
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("Starting up API service...")
    try:
        kafka_producer.connect()
    except Exception as e:
        logger.warning(f"Kafka connection failed: {e}. Service will continue without Kafka.")

    yield

    # Shutdown
    logger.info("Shutting down API service...")
    kafka_producer.close()
    await engine.dispose()


app = FastAPI(
    title="Restaurant Booking System API",
    description="API для системы бронирования столиков в ресторанах",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(bookings_router)


@app.get("/", tags=["Health"])
async def root():
    """Проверка работоспособности API"""
    return {
        "status": "ok",
        "service": "Restaurant Booking System API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
