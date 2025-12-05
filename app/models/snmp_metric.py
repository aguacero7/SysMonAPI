from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class SNMPMetric(SQLModel, table=True):
    """Modèle de métrique SNMP pour un routeur"""
    id: Optional[int] = Field(default=None, primary_key=True)
    router_id: int = Field(foreign_key="router.id", index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

    # metriques systeme
    system_uptime: Optional[int] = None  # en centiemes de seconde
    cpu_usage: Optional[float] = None  # pourcentage
    memory_total: Optional[int] = None  # en bytes
    memory_used: Optional[int] = None  # en bytes
    memory_free: Optional[int] = None  # en bytes

    # metriques reseau
    interface_name: Optional[str] = None
    if_in_octets: Optional[int] = None  # bytes entrants
    if_out_octets: Optional[int] = None  # bytes sortants
    if_in_errors: Optional[int] = None  # erreurs entrantes
    if_out_errors: Optional[int] = None  # erreurs sortantes
    if_oper_status: Optional[int] = None  # 1=up, 2=down

    # disponibilite
    is_reachable: bool = True
    response_time: Optional[float] = None  # temps de reponse en ms
