from fastapi import FastAPI
from locksy.db.connection import init_db
from locksy.api.routes import router

app = FastAPI(title="Locksy - Encrypted Evidence Locker")

@app.on_event("startup")
def startup():
    init_db("locksy.db")

app.include_router(router)

@app.get("/")
def read_root():
    return {"status": "ok", "app": "Locksy"}