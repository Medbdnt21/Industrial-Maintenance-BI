import csv
import sys
from datetime import datetime
from pathlib import Path

from .db import Base, SessionLocal, engine
from .models import MaintenanceRecord, Machine

CSV_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "mantenimiento_final.csv"
TOL = 0.05

COLUMNS = [
    "IDRegistro",
    "Fecha",
    "Maquina",
    "HorasOperativas",
    "Averias",
    "HorasReparacion",
    "Coste",
    "MTBF",
    "MTTR",
    "CostePorAveria",
]


def read_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        missing = []
        for c in COLUMNS:
            if c not in (reader.fieldnames or []):
                missing.append(c)
        if missing:
            raise SystemExit("Missing columns: " + str(missing))

        rows = []
        for row in reader:
            clean_row = {}
            for c in COLUMNS:
                value = row.get(c)
                if value is None:
                    value = ""
                clean_row[c] = value.strip()
            rows.append(clean_row)
        return rows


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def validate(rows):
    errors = []
    seen_ids = set()
    clean = []

    for i, row in enumerate(rows):
        line_number = i + 2
        label = "line " + str(line_number) + " (" + (row["IDRegistro"] or "no id") + ")"
        row_errors = []

        for col in COLUMNS:
            if row[col] == "":
                row_errors.append(col + " NULL/empty")

        if row_errors:
            errors.append(label + ": " + ", ".join(row_errors))
            continue

        if row["IDRegistro"] in seen_ids:
            errors.append(label + ": duplicate IDRegistro")
            continue
        seen_ids.add(row["IDRegistro"])

        try:
            record_date = datetime.strptime(row["Fecha"], "%Y-%m-%d").date()
        except ValueError:
            errors.append(label + ": bad date format " + row["Fecha"])
            continue

        parsed = {
            "IDRegistro": row["IDRegistro"],
            "Fecha": record_date,
            "Maquina": row["Maquina"],
        }

        number_columns = [
            "HorasOperativas",
            "Averias",
            "HorasReparacion",
            "Coste",
            "MTBF",
            "MTTR",
            "CostePorAveria",
        ]
        numeric_ok = True
        for col in number_columns:
            val = to_float(row[col])
            if val is None:
                errors.append(label + ": " + col + " not numeric " + row[col])
                numeric_ok = False
            elif val < 0:
                errors.append(label + ": " + col + " negative " + str(val))
                numeric_ok = False
            else:
                parsed[col] = val
        if not numeric_ok:
            continue

        if parsed["Averias"] == 0:
            errors.append(label + ": Averias must be > 0")
            continue

        parsed["MTBF_calc"] = round(parsed["HorasOperativas"] / parsed["Averias"], 2)
        parsed["MTTR_calc"] = round(parsed["HorasReparacion"] / parsed["Averias"], 2)
        parsed["CostePorAveria_calc"] = round(parsed["Coste"] / parsed["Averias"], 2)

        clean.append(parsed)

    return clean, errors


def drift_report(rows):
    warnings = []
    for row in rows:
        checks = [
            ("MTBF", "MTBF_calc", "MTBF"),
            ("MTTR", "MTTR_calc", "MTTR"),
            ("CostePorAveria", "CostePorAveria_calc", "CostePorAveria"),
        ]
        for src, calc, name in checks:
            if abs(row[src] - row[calc]) > TOL:
                warnings.append(
                    row["IDRegistro"]
                    + ": "
                    + name
                    + " file="
                    + str(row[src])
                    + " calc="
                    + str(row[calc])
                    + " (recomputed value stored)"
                )
    return warnings


def load(rows):
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        machines = {}
        inserted = 0
        skipped = 0

        for row in rows:
            name = row["Maquina"]

            if name not in machines:
                machine = db.query(Machine).filter_by(name=name).first()
                if machine is None:
                    machine = Machine(name=name)
                    db.add(machine)
                    db.flush()
                machines[name] = machine.id

            found = (
                db.query(MaintenanceRecord.id)
                .filter(MaintenanceRecord.id_reg == row["IDRegistro"])
                .first()
            )
            if found is not None:
                skipped += 1
                continue

            record = MaintenanceRecord()
            record.id_reg = row["IDRegistro"]
            record.machine_id = machines[name]
            record.date = row["Fecha"]
            record.operational_hours = int(row["HorasOperativas"])
            record.breakdowns = int(row["Averias"])
            record.repair_hours = row["HorasReparacion"]
            record.cost = row["Coste"]
            record.mtbf = row["MTBF_calc"]
            record.mttr = row["MTTR_calc"]
            record.cost_per_breakdown = row["CostePorAveria_calc"]
            db.add(record)
            inserted += 1

        db.commit()
        return inserted, skipped
    finally:
        db.close()


def main():
    rows = read_rows(CSV_PATH)
    clean, errors = validate(rows)
    warnings = drift_report(clean)

    print("CSV rows: " + str(len(rows)) + " | valid: " + str(len(clean)) + " | errors: " + str(len(errors)))
    for err in errors:
        print("  ERROR " + err)
    for warn in warnings:
        print("  DRIFT " + warn)

    if errors:
        print("Load aborted: fix data errors first.")
        return 1

    inserted, skipped = load(clean)
    print("Loaded: inserted=" + str(inserted) + " skipped_existing=" + str(skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
