from fastapi import FastAPI
from app.api.users import router as users_router
from app.api.bills import router as bills_router
from app.api.expenses import router as expenses_router
from app.core.config import settings
import app.models

app = FastAPI(title=settings.app_name,
    description="A comprehensive expense splitting API",
    version="1.0.0")

app.include_router(users_router, prefix="/api/v1")
app.include_router(bills_router, prefix="/api/v1")
app.include_router(expenses_router, prefix="/api/v1")


@app.get("/")
def root():
    return "Hello Expense Splitter"