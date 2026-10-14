from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..kpis import machine_kpis, score_machines
from ..models import Machine
from ..schemas import MachineDetail, MachineKpi, TimePoint
from ..series import monthly

router = APIRouter(tags=["machines"])


@router.get("/api/machines", response_model=list[MachineKpi])
def list_machines(db: Session = Depends(get_db)):
    """Per-machine KPIs with rank flags, score and priority."""
    return score_machines(machine_kpis(db))


@router.get("/api/machines/{machine_id}", response_model=MachineDetail)
def machine_detail(machine_id: int, db: Session = Depends(get_db)):
    """One machine: KPI row + monthly series (cost, breakdowns, mtbf, mttr)."""
    machine = db.get(Machine, machine_id)
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")

    scored = score_machines(machine_kpis(db))
    detail_row = None
    for row in scored:
        if row["machine_id"] == machine_id:
            detail_row = row

    series = []
    for month_row in monthly(db, machine_id=machine_id):
        point = TimePoint(
            month=month_row["month"],
            cost=month_row["cost"],
            breakdowns=month_row["breakdowns"],
            mtbf=month_row["mtbf"],
            mttr=month_row["mttr"],
        )
        series.append(point)

    return MachineDetail(machine=detail_row, series=series)
