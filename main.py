from fastapi import FastAPI, Depends, HTTPException
from routers import accounts, transfers, login
from db.database import engine, Base
from db import models
#from utils.util import hash_password

#print(hash_password('password'))
app = FastAPI()

@app.on_event('startup')
def on_startup():
    models.Base.metadata.create_all(engine)


#Include endpoints

app.include_router(login.router, prefix="/login", tags=["login"])
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(transfers.router, prefix="/transfers", tags=["transfers"])



