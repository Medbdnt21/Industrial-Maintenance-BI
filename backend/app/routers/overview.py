from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..kpis import overview
from ..schemas import Overview

router = APIRouter(tags=["overview"])


@router.get("/api/overview", response_model=Overview)
def get_overview(db: Session = Depends(get_db)):
    """Global KPIs: totals, machines, records, overall avg MTBF/MTTR."""
    return overview(db)
