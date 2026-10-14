from sqlalchemy import CheckConstraint, Column, Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .db import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True)
    name = Column(String(16), unique=True, nullable=False)

    records = relationship("MaintenanceRecord", back_populates="machine")


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"
    __table_args__ = (
        UniqueConstraint("id_reg", name="uq_id_reg"),
        CheckConstraint("operational_hours >= 0", name="ck_operational_hours"),
        CheckConstraint("breakdowns > 0", name="ck_breakdowns"),
        CheckConstraint("repair_hours >= 0", name="ck_repair_hours"),
        CheckConstraint("cost >= 0", name="ck_cost"),
        CheckConstraint("mtbf >= 0", name="ck_mtbf"),
        CheckConstraint("mttr >= 0", name="ck_mttr"),
        CheckConstraint("cost_per_breakdown >= 0", name="ck_cost_per_breakdown"),
    )

    id = Column(Integer, primary_key=True)
    id_reg = Column(String(16), nullable=False)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    operational_hours = Column(Integer, nullable=False)
    breakdowns = Column(Integer, nullable=False)
    repair_hours = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    mtbf = Column(Float, nullable=False)
    mttr = Column(Float, nullable=False)
    cost_per_breakdown = Column(Float, nullable=False)

    machine = relationship("Machine", back_populates="records")
