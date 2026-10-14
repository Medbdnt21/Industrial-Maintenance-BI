from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..kpis import alerts, machine_kpis
from ..schemas import MachineKpi

router = APIRouter(tags=["alerts"])


@router.get("/api/alerts", response_model=list[MachineKpi])
def list_alerts(db: Session = Depends(get_db)):
    """Machines with score >= 2 (worst quartile on 2+ KPIs), worst first."""
    return alerts(machine_kpis(db))
