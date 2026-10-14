from typing import List, Optional

from pydantic import BaseModel


class Overview(BaseModel):
    machines: int
    records: int
    total_cost: float
    total_breakdowns: int
    total_repair_hours: float
    operational_hours: int
    avg_mtbf: float
    avg_mttr: float


class MachineKpi(BaseModel):
    machine_id: int
    machine: str
    records: int
    operational_hours: int
    total_cost: float
    total_breakdowns: int
    total_repair_hours: float
    avg_mtbf: float
    avg_mttr: float
    avg_cost_per_breakdown: float
    flags: Optional[List[str]] = None
    flag_reasons: Optional[List[str]] = None
    score: Optional[int] = None
    priority: Optional[str] = None


class TimePoint(BaseModel):
    month: str
    cost: Optional[float] = None
    breakdowns: Optional[int] = None
    mtbf: Optional[float] = None
    mttr: Optional[float] = None


class MachineDetail(BaseModel):
    machine: MachineKpi
    series: List[TimePoint]


class Timeseries(BaseModel):
    metric: str
    points: List[TimePoint]
