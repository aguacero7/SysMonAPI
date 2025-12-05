from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, func, desc
from app.models import SNMPMetric, Router
from app.config.database import get_session
from datetime import datetime, timedelta
from typing import Optional, List
import os

router = APIRouter(prefix="/monitoring", tags=["snmp-monitoring"])

# configure jinja2 templates
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/routers/{router_id}/metrics")
def get_router_metrics(
    router_id: int,
    limit: int = Query(default=100, le=1000),
    hours: Optional[int] = Query(default=None, description="nombre d'heures en arriere"),
    session: Session = Depends(get_session)
):
    """Recupere toutes les metriques snmp pour un routeur """

    router_check = session.get(Router, router_id)
    if not router_check:
        raise HTTPException(status_code=404, detail="router not found")

    statement = select(SNMPMetric).where(SNMPMetric.router_id == router_id)

    if hours:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        statement = statement.where(SNMPMetric.timestamp >= time_threshold)

    statement = statement.order_by(desc(SNMPMetric.timestamp)).limit(limit)
    metrics = session.exec(statement).all()

    return {
        "router_id": router_id,
        "count": len(metrics),
        "metrics": metrics
    }

@router.get("/routers/{router_id}/availability")
def get_router_availability(
    router_id: int,
    hours: int = Query(default=24, description="periode en heures pour calculer la dispo"),
    session: Session = Depends(get_session)
):
    """calcule les statistiques de disponibilite pour un routeur"""

    router_check = session.get(Router, router_id)
    if not router_check:
        raise HTTPException(status_code=404, detail="router not found")

    time_threshold = datetime.utcnow() - timedelta(hours=hours)

    # recupere toutes les metriques de la periode
    statement = select(SNMPMetric).where(
        SNMPMetric.router_id == router_id,
        SNMPMetric.timestamp >= time_threshold
    )
    metrics = session.exec(statement).all()

    if not metrics:
        return {
            "router_id": router_id,
            "period_hours": hours,
            "availability_percent": None,
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "average_response_time_ms": None
        }

    total_checks = len(metrics)
    successful_checks = sum(1 for m in metrics if m.is_reachable)
    failed_checks = total_checks - successful_checks

    availability_percent = (successful_checks / total_checks) * 100 if total_checks > 0 else 0

    # calcule le temps de reponse moyen pour les checks reussis
    response_times = [m.response_time for m in metrics if m.is_reachable and m.response_time is not None]
    avg_response_time = sum(response_times) / len(response_times) if response_times else None

    return {
        "router_id": router_id,
        "period_hours": hours,
        "availability_percent": round(availability_percent, 2),
        "total_checks": total_checks,
        "successful_checks": successful_checks,
        "failed_checks": failed_checks,
        "average_response_time_ms": round(avg_response_time, 2) if avg_response_time else None
    }

@router.get("/routers/{router_id}/bandwidth")
def get_router_bandwidth(
    router_id: int,
    hours: int = Query(default=24, description="periode en heures"),
    session: Session = Depends(get_session)
):
    """recupere les statistiques de bande passante pour un routeur"""

    # verifie que le routeur existe
    router_check = session.get(Router, router_id)
    if not router_check:
        raise HTTPException(status_code=404, detail="router not found")

    time_threshold = datetime.utcnow() - timedelta(hours=hours)

    # recupere les metriques de la periode
    statement = select(SNMPMetric).where(
        SNMPMetric.router_id == router_id,
        SNMPMetric.timestamp >= time_threshold,
        SNMPMetric.is_reachable == True
    ).order_by(SNMPMetric.timestamp)

    metrics = session.exec(statement).all()

    if len(metrics) < 2:
        return {
            "router_id": router_id,
            "period_hours": hours,
            "bandwidth_data": [],
            "message": "pas assez de donnees pour calculer la bande passante"
        }

    bandwidth_data = []

    # deltas entre les mesures successives
    for i in range(1, len(metrics)):
        prev_metric = metrics[i - 1]
        curr_metric = metrics[i]

        time_delta = (curr_metric.timestamp - prev_metric.timestamp).total_seconds()

        if time_delta > 0 and prev_metric.if_in_octets and curr_metric.if_in_octets:
            # octets par seconde
            in_delta = curr_metric.if_in_octets - prev_metric.if_in_octets
            out_delta = curr_metric.if_out_octets - prev_metric.if_out_octets if curr_metric.if_out_octets and prev_metric.if_out_octets else 0

            # gere le cas du rollover des compteurs 
            if in_delta < 0:
                in_delta += 2**32
            if out_delta < 0:
                out_delta += 2**32

            in_bps = (in_delta * 8) / time_delta  # bits par seconde
            out_bps = (out_delta * 8) / time_delta

            bandwidth_data.append({
                "timestamp": curr_metric.timestamp.isoformat(),
                "in_bps": int(in_bps),
                "out_bps": int(out_bps),
                "in_mbps": round(in_bps / 1_000_000, 2),
                "out_mbps": round(out_bps / 1_000_000, 2)
            })

    return {
        "router_id": router_id,
        "period_hours": hours,
        "data_points": len(bandwidth_data),
        "bandwidth_data": bandwidth_data
    }

@router.get("/routers/{router_id}/errors")
def get_router_errors(
    router_id: int,
    hours: int = Query(default=24, description="periode en heures"),
    session: Session = Depends(get_session)
):
    """recupere les statistiques d'erreurs pour un routeur"""

    # verifie que le routeur existe
    router_check = session.get(Router, router_id)
    if not router_check:
        raise HTTPException(status_code=404, detail="router not found")

    time_threshold = datetime.utcnow() - timedelta(hours=hours)

    statement = select(SNMPMetric).where(
        SNMPMetric.router_id == router_id,
        SNMPMetric.timestamp >= time_threshold,
        SNMPMetric.is_reachable == True
    ).order_by(SNMPMetric.timestamp)

    metrics = session.exec(statement).all()

    if not metrics:
        return {
            "router_id": router_id,
            "period_hours": hours,
            "error_data": [],
            "message": "aucune donnee disponible"
        }

    error_data = []

    for metric in metrics:
        if metric.if_in_errors is not None or metric.if_out_errors is not None:
            error_data.append({
                "timestamp": metric.timestamp.isoformat(),
                "in_errors": metric.if_in_errors,
                "out_errors": metric.if_out_errors,
                "oper_status": metric.if_oper_status,
                "status_text": "up" if metric.if_oper_status == 1 else "down" if metric.if_oper_status == 2 else "unknown"
            })

    return {
        "router_id": router_id,
        "period_hours": hours,
        "data_points": len(error_data),
        "error_data": error_data
    }

@router.get("/overview")
def get_monitoring_overview(session: Session = Depends(get_session)):
    """apercu global du monitoring de tous les routeurs"""

    # recupere tous les routeurs
    routers_statement = select(Router)
    all_routers = session.exec(routers_statement).all()

    if not all_routers:
        return {
            "total_routers": 0,
            "routers": []
        }

    overview = []

    for router in all_routers:
        # recupere la derniere metrique
        latest_metric_statement = select(SNMPMetric).where(
            SNMPMetric.router_id == router.id
        ).order_by(desc(SNMPMetric.timestamp)).limit(1)

        latest_metric = session.exec(latest_metric_statement).first()

        # calcule la dispo sur les dernieres 24h
        time_threshold = datetime.utcnow() - timedelta(hours=24)
        metrics_24h = session.exec(
            select(SNMPMetric).where(
                SNMPMetric.router_id == router.id,
                SNMPMetric.timestamp >= time_threshold
            )
        ).all()

        if metrics_24h:
            successful = sum(1 for m in metrics_24h if m.is_reachable)
            availability = (successful / len(metrics_24h)) * 100
        else:
            availability = None

        overview.append({
            "router_id": router.id,
            "router_ip": router.ip,
            "router_hostname": router.hostname,
            "last_check": latest_metric.timestamp.isoformat() if latest_metric else None,
            "is_reachable": latest_metric.is_reachable if latest_metric else None,
            "response_time_ms": latest_metric.response_time if latest_metric else None,
            "availability_24h_percent": round(availability, 2) if availability is not None else None,
            "uptime_seconds": latest_metric.system_uptime / 100 if latest_metric and latest_metric.system_uptime else None
        })

    return {
        "total_routers": len(all_routers),
        "routers": overview
    }

@router.get("/dashboard", response_class=HTMLResponse)
def show_dashboard(request: Request, session: Session = Depends(get_session)):
    """affiche le dashboard html avec toutes les metriques"""

    # recupere tous les routeurs
    routers_statement = select(Router)
    all_routers = session.exec(routers_statement).all()

    if not all_routers:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "overview": {"total_routers": 0, "routers": []},
            "routers_up": 0,
            "routers_down": 0,
            "avg_availability": 0
        })

    overview = []
    routers_up = 0
    routers_down = 0
    total_availability = 0
    count_with_availability = 0

    for router in all_routers:
        # recupere la derniere metrique
        latest_metric_statement = select(SNMPMetric).where(
            SNMPMetric.router_id == router.id
        ).order_by(desc(SNMPMetric.timestamp)).limit(1)

        latest_metric = session.exec(latest_metric_statement).first()

        # calcule la dispo sur les dernieres 24h
        time_threshold = datetime.utcnow() - timedelta(hours=24)
        metrics_24h = session.exec(
            select(SNMPMetric).where(
                SNMPMetric.router_id == router.id,
                SNMPMetric.timestamp >= time_threshold
            )
        ).all()

        if metrics_24h:
            successful = sum(1 for m in metrics_24h if m.is_reachable)
            availability = (successful / len(metrics_24h)) * 100
            total_availability += availability
            count_with_availability += 1
        else:
            availability = None

        # compte les routeurs up/down
        if latest_metric and latest_metric.is_reachable:
            routers_up += 1
        elif latest_metric and not latest_metric.is_reachable:
            routers_down += 1

        overview.append({
            "router_id": router.id,
            "router_ip": router.ip,
            "router_hostname": router.hostname,
            "last_check": latest_metric.timestamp.isoformat() if latest_metric else None,
            "is_reachable": latest_metric.is_reachable if latest_metric else None,
            "response_time_ms": latest_metric.response_time if latest_metric else None,
            "availability_24h_percent": round(availability, 2) if availability is not None else None,
            "uptime_seconds": latest_metric.system_uptime / 100 if latest_metric and latest_metric.system_uptime else None
        })

    # calcule la disponibilite moyenne
    avg_availability = round(total_availability / count_with_availability, 2) if count_with_availability > 0 else 0

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "overview": {
            "total_routers": len(all_routers),
            "routers": overview
        },
        "routers_up": routers_up,
        "routers_down": routers_down,
        "avg_availability": avg_availability
    })
