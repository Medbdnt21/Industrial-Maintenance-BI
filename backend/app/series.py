from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import MaintenanceRecord


def monthly(db, machine_id=None):
    """
    Monthly aggregation for charts.
    MTBF/MTTR are computed on the monthly sums (not average of ratios).

    Returns a list of dicts:
    month, cost, breakdowns, operational_hours, repair_hours, mtbf, mttr
    """
    month = func.strftime("%Y-%m", MaintenanceRecord.date)

    query = db.query(
        month.label("month"),
        func.sum(MaintenanceRecord.cost),
        func.sum(MaintenanceRecord.breakdowns),
        func.sum(MaintenanceRecord.operational_hours),
        func.sum(MaintenanceRecord.repair_hours),
    )
    if machine_id is not None:
        query = query.filter(MaintenanceRecord.machine_id == machine_id)

    rows = query.group_by(month).order_by(month).all()

    result = []
    for m, cost, breakdowns, hours, repair in rows:
        row = {
            "month": m,
            "cost": round(cost, 2),
            "breakdowns": breakdowns,
            "operational_hours": hours,
            "repair_hours": round(repair, 2),
        }
        if breakdowns > 0:
            row["mtbf"] = round(hours / breakdowns, 2)
            row["mttr"] = round(repair / breakdowns, 2)
        else:
            row["mtbf"] = None
            row["mttr"] = None
        result.append(row)

    return result
