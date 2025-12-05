from fastapi import FastAPI
from app.config.database import init_db
from app.routers import ordinateurs, routers, equipements, snmp_monitoring, auth
from app.services.snmp_monitor import snmp_monitor
from contextlib import asynccontextmanager


# remplace le app.onevent("startup") et app.onevent("shutdown") pour l'asynchrone
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await snmp_monitor.start()
    yield
    await snmp_monitor.stop()

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(ordinateurs.router)
app.include_router(routers.router)
app.include_router(equipements.router)
app.include_router(snmp_monitoring.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de surveillance des routeurs et ordinateurs."}
