import json
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from app.models import Router
from app.config.database import get_session
from typing import Optional

router = APIRouter(prefix="/routers", tags=["routers"])

@router.get("")
def get_routers(session: Session = Depends(get_session)):
    statement = select(Router)
    routers = session.exec(statement).all()
    return routers

@router.get("/{router_id}/query_ntp")
def query_ntp(router_id: int, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    return router.query_ntp()

@router.get("/{router_id}")
def get_router(router_id: int, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    return router

@router.post("")
def add_router(router: Router, session: Session = Depends(get_session)):
    session.add(router)
    session.commit()
    session.refresh(router)
    return {"message": "Router added successfully", "id": router.id}

@router.put("/{router_id}")
def edit_router(router_id: int, router_data: Router, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")

    router_dict = router_data.model_dump(exclude_unset=True, exclude={'id'})
    for key, value in router_dict.items():
        setattr(router, key, value)

    session.add(router)
    session.commit()
    session.refresh(router)
    return {"message": "Router updated successfully", "router": router}

@router.delete("/{router_id}")
def delete_router(router_id: int, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")

    session.delete(router)
    session.commit()
    return {"message": "Router deleted successfully"}

@router.get("/{router_id}/routing_table")
def get_routing_table(router_id: int, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    return {"success": True, "routing_table": json.loads(router.get_routing_table())}

@router.get("/{router_id}/bgp_summary")
def get_bgp_summary(router_id: int, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    bgp_sum = json.loads(router.get_bgp_summary())
    return {"success": True, "bgp_summary": bgp_sum}

@router.get("/{router_id}/ospf_neighbors")
def get_ospf_neighbors(router_id: int, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    ospf_neigh = json.loads(router.get_ospf_neighbors())
    return {"success": True, "ospf_neighbors": ospf_neigh}

@router.get("/{router_id}/interfaces")
def get_interfaces(router_id: int, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    interfaces = json.loads(router.get_interfaces_status())
    return {"success": True, "interfaces": interfaces}
