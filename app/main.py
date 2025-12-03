from fastapi import FastAPI
from app.config.database import init_db
from app.routers import ordinateurs, routers, equipements

app = FastAPI()

app.include_router(ordinateurs.router)
app.include_router(routers.router)
app.include_router(equipements.router)

@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API FastAPI"}
