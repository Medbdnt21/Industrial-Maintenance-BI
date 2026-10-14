from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import TimePoint, Timeseries
from ..series import monthly

router = APIRouter(tags=["timeseries"])

METRICS = ["cost", "breakdowns", "mtbf", "mttr"]


@router.get("/api/timeseries", response_model=Timeseries)
def timeseries(metric: str = Query(..., description="cost|breakdowns|mtbf|mttr"),
               db: Session = Depends(get_db)):
    """Monthly trend of one metric across all machines."""
    if metric not in METRICS:
        raise HTTPException(status_code=422, detail="metric must be one of " + str(METRICS))

    points = []
    for row in monthly(db):
        point = TimePoint(
            month=row["month"],
            cost=row["cost"],
            breakdowns=row["breakdowns"],
            mtbf=row["mtbf"],
            mttr=row["mttr"],
        )
        points.append(point)

    return Timeseries(metric=metric, points=points)
