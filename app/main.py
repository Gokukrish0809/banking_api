from fastapi import FastAPI

from .database import Base, engine
from .routers import accounts, login, transfers


app = FastAPI(
    title="Entrix Banking API",
    description="Authenticate employees, create accounts, check balances, transfer funds, get transfer history",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(engine)

@app.get("/", summary="Landing point")
async def root():
    return {"message": "Welcome to Entrix Banking API"}


# Include endpoints

app.include_router(login.router, prefix="/login", tags=["login"])
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(transfers.router, prefix="/transfers", tags=["transfers"])
