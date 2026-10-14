"""
kpis.py - KPI engine for industrial maintenance analysis.

KPI definitions (per machine, aggregated over all maintenance_records):

- total_cost             SUM(cost)                      -> machines with major costs
- total_breakdowns       SUM(breakdowns)                -> machines that break down most
- total_repair_hours     SUM(repair_hours)              -> machines eating most repair time
- avg_mtbf               SUM(hours) / SUM(breakdowns)   -> average time between breakdowns (hours)
- avg_mttr               SUM(repair_hours) / SUM(breakdowns) -> average time to repair (hours)
- avg_cost_per_breakdown SUM(cost) / SUM(breakdowns)    -> average cost per event

"Should be checked" rule - rank based, no magic thresholds:

1. Rank all machines per KPI:
     cost / breakdowns / mttr   : highest value = worst
     mtbf                       : lowest value  = worst
2. Flag machine if it lies in the worst quartile.
   Example: 12 machines -> ceil(25% * 12) = 3 flagged per KPI.
3. score = number of flags (0..4). Machine with score >= 2 goes
   to the alert list, sorted by score (worst first).
"""

import math

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Machine, MaintenanceRecord

ALERT_THRESHOLD = 2
WORST_QUARTILE = 0.25

# KPIs where HIGH value is bad
HIGH_IS_BAD = {
    "total_cost": "major costs",
    "total_breakdowns": "frequent breakdowns",
    "avg_mttr": "slow repairs",
}

# KPIs where LOW value is bad
LOW_IS_BAD = {
    "avg_mtbf": "short time between breakdowns",
}


def machine_kpis(db):
    """
    Aggregates raw maintenance_records into one KPI row per machine.

    Returns a list of dicts with keys:
    machine_id, machine, records, total_cost, total_breakdowns,
    total_repair_hours, operational_hours, avg_mtbf, avg_mttr,
    avg_cost_per_breakdown - sorted by machine name.
    """
    rows = (
        db.query(
            MaintenanceRecord.machine_id,
            MaintenanceRecord.operational_hours,
            MaintenanceRecord.breakdowns,
            MaintenanceRecord.repair_hours,
            MaintenanceRecord.cost,
        )
        .all()
    )

    acc = {}
    for machine_id, hours, breakdowns, repair_hours, cost in rows:
        if machine_id not in acc:
            acc[machine_id] = {
                "machine_id": machine_id,
                "operational_hours": 0,
                "total_breakdowns": 0,
                "total_repair_hours": 0.0,
                "total_cost": 0.0,
                "records": 0,
            }
        a = acc[machine_id]
        a["operational_hours"] = a["operational_hours"] + hours
        a["total_breakdowns"] = a["total_breakdowns"] + breakdowns
        a["total_repair_hours"] = a["total_repair_hours"] + repair_hours
        a["total_cost"] = a["total_cost"] + cost
        a["records"] = a["records"] + 1

    names = dict(db.query(Machine.id, Machine.name).all())

    result = []
    for machine_id, a in acc.items():
        breakdowns = a["total_breakdowns"]
        a["machine"] = names[machine_id]
        a["avg_mtbf"] = round(a["operational_hours"] / breakdowns, 2)
        a["avg_mttr"] = round(a["total_repair_hours"] / breakdowns, 2)
        a["avg_cost_per_breakdown"] = round(a["total_cost"] / breakdowns, 2)
        result.append(a)

    result.sort(key=sort_by_machine_name, reverse=False)
    return result


def sort_by_machine_name(row):
    return row["machine"]


def _worst_count(n):
    """Number of machines in worst quartile: ceil(25% * n), minimum 1."""
    count = math.ceil(WORST_QUARTILE * n)
    if count < 1:
        count = 1
    return count


def pick_worst(kpis, kpi_name, highest_is_worst):
    """
    Returns the worst quartile of machines for one KPI.
    Uses a simple selection loop, no sorting tricks.
    """
    n = len(kpis)
    how_many = _worst_count(n)

    remaining = list(kpis)
    picked = []

    for step in range(how_many):
        best_index = 0
        for j in range(1, len(remaining)):
            if highest_is_worst:
                if remaining[j][kpi_name] > remaining[best_index][kpi_name]:
                    best_index = j
            else:
                if remaining[j][kpi_name] < remaining[best_index][kpi_name]:
                    best_index = j
        picked.append(remaining.pop(best_index))

    return picked


def score_machines(kpis):
    """
    Adds rank flags and priority score to each KPI row.

    Each row gets:
      flags        - list of KPI names where machine is in worst quartile
      flag_reasons - human readable reasons
      score        - number of flags (0..4)
      priority     - "CHECK" if score >= 2 else "OK"

    Returns rows sorted by score (worst first), then by total_cost.
    """
    flags_by_machine = {}
    for k in kpis:
        flags_by_machine[k["machine_id"]] = []

    for kpi_name in HIGH_IS_BAD:
        worst_rows = pick_worst(kpis, kpi_name, highest_is_worst=True)
        for k in worst_rows:
            flags_by_machine[k["machine_id"]].append(kpi_name)

    for kpi_name in LOW_IS_BAD:
        worst_rows = pick_worst(kpis, kpi_name, highest_is_worst=False)
        for k in worst_rows:
            flags_by_machine[k["machine_id"]].append(kpi_name)

    scored = []
    for k in kpis:
        flags = flags_by_machine[k["machine_id"]]

        reasons = []
        for f in flags:
            if f in HIGH_IS_BAD:
                reasons.append(HIGH_IS_BAD[f])
            else:
                reasons.append(LOW_IS_BAD[f])

        score = len(flags)
        if score >= ALERT_THRESHOLD:
            priority = "CHECK"
        else:
            priority = "OK"

        row = {}
        for key in k:
            row[key] = k[key]
        row["flags"] = flags
        row["flag_reasons"] = reasons
        row["score"] = score
        row["priority"] = priority
        scored.append(row)

    # two stable sorts: first by cost, then by score (score wins)
    scored.sort(key=sort_by_cost, reverse=True)
    scored.sort(key=sort_by_score, reverse=True)
    return scored


def sort_by_score(row):
    return row["score"]


def sort_by_cost(row):
    return row["total_cost"]


def alerts(kpis):
    """Machines with score >= ALERT_THRESHOLD, sorted worst first."""
    result = []
    for row in score_machines(kpis):
        if row["priority"] == "CHECK":
            result.append(row)
    return result


def overview(db):
    """
    Global KPIs across all machines:
    total_cost, total_breakdowns, total_repair_hours, operational_hours,
    avg_mtbf (overall), avg_mttr (overall), machines, records.
    """
    totals = (
        db.query(
            func.sum(MaintenanceRecord.cost),
            func.sum(MaintenanceRecord.breakdowns),
            func.sum(MaintenanceRecord.repair_hours),
            func.sum(MaintenanceRecord.operational_hours),
            func.count(MaintenanceRecord.id),
        )
        .one()
    )
    total_cost = totals[0]
    total_breakdowns = totals[1]
    total_repair = totals[2]
    total_hours = totals[3]
    records = totals[4]

    machines = db.query(func.count(Machine.id)).scalar()

    return {
        "machines": machines,
        "records": records,
        "total_cost": round(total_cost, 2),
        "total_breakdowns": total_breakdowns,
        "total_repair_hours": round(total_repair, 2),
        "operational_hours": total_hours,
        "avg_mtbf": round(total_hours / total_breakdowns, 2),
        "avg_mttr": round(total_repair / total_breakdowns, 2),
    }
