from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.models import Ordinateur, User
from app.config.database import get_session
from app.config.auth import get_current_active_user

router = APIRouter(prefix="/ordinateurs", tags=["ordinateurs"])

@router.get("")
def get_ordinateurs(session: Session = Depends(get_session)):
    statement = select(Ordinateur)
    ordinateurs = session.exec(statement).all()
    return ordinateurs

@router.get("/{ordinateur_id}")
def get_ordinateur(ordinateur_id: int, session: Session = Depends(get_session)):
    ordinateur = session.get(Ordinateur, ordinateur_id)
    if not ordinateur:
        raise HTTPException(status_code=404, detail="Ordinateur not found")
    return ordinateur

@router.post("")
def add_ordinateur(ordinateur: Ordinateur, session: Session = Depends(get_session)):
    session.add(ordinateur)
    session.commit()
    session.refresh(ordinateur)
    return {"message": "Ordinateur added successfully", "id": ordinateur.id}

@router.put("/{ordinateur_id}")
def edit_ordinateur(ordinateur_id: int, ordinateur_data: Ordinateur, session: Session = Depends(get_session)):
    ordinateur = session.get(Ordinateur, ordinateur_id)
    if not ordinateur:
        raise HTTPException(status_code=404, detail="Ordinateur not found")

    ordinateur_dict = ordinateur_data.model_dump(exclude_unset=True, exclude={'id'})
    for key, value in ordinateur_dict.items():
        setattr(ordinateur, key, value)

    session.add(ordinateur)
    session.commit()
    session.refresh(ordinateur)
    return {"message": "Ordinateur updated successfully", "ordinateur": ordinateur}

@router.delete("/{ordinateur_id}")
def delete_ordinateur(ordinateur_id: int, session: Session = Depends(get_session)):
    ordinateur = session.get(Ordinateur, ordinateur_id)
    if not ordinateur:
        raise HTTPException(status_code=404, detail="Ordinateur not found")

    session.delete(ordinateur)
    session.commit()
    return {"message": "Ordinateur deleted successfully"}

@router.get("/{ordinateur_id}/memory")
def get_memory(ordinateur_id: int, session: Session = Depends(get_session)):
    ordinateur = session.get(Ordinateur, ordinateur_id)
    if not ordinateur:
        raise HTTPException(status_code=404, detail="Ordinateur not found")

    total_memory = ordinateur.get_max_memory()
    free_memory = ordinateur.get_free_memory()
    return {"free_memory": free_memory, "total_memory": total_memory}

@router.get("/{ordinateur_id}/cpu_load")
def get_cpu_load(ordinateur_id: int, session: Session = Depends(get_session)):
    ordinateur = session.get(Ordinateur, ordinateur_id)
    if not ordinateur:
        raise HTTPException(status_code=404, detail="Ordinateur not found")

    cpu_load = ordinateur.get_cpu_load()
    return {"cpu_load": cpu_load}

@router.get("/{ordinateur_id}/os_release")
def get_os_release(ordinateur_id: int, session: Session = Depends(get_session)):
    ordinateur = session.get(Ordinateur, ordinateur_id)
    if not ordinateur:
        raise HTTPException(status_code=404, detail="Ordinateur not found")

    return ordinateur.get_os_release()
