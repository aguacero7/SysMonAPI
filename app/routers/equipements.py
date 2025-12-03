from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.models import Ordinateur, Router
from app.config.database import get_session

router = APIRouter(prefix="/equipements", tags=["equipements"])

@router.get("")
def get_equipements(session: Session = Depends(get_session)):
    ordinateurs = session.exec(select(Ordinateur)).all()
    routers = session.exec(select(Router)).all()
    return {"ordinateurs": ordinateurs, "routers": routers}

@router.get("/search")
def search_equipement_by_ip(ip: str, session: Session = Depends(get_session)):
    ordinateur = session.exec(select(Ordinateur).where(Ordinateur.ip == ip)).first()
    if ordinateur:
        return {"type": "ordinateur", "data": ordinateur}

    router = session.exec(select(Router).where(Router.ip == ip)).first()
    if router:
        return {"type": "router", "data": router}

    raise HTTPException(status_code=404, detail="Equipement not found")
