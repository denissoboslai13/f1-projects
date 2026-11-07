import csv
from pathlib import Path
from super_licence.models import Driver, Issue

def read_rows(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def blank_to_none(value: str) -> str | None:
    if value == "":
        return None

    return value

def load_drivers(path: Path) -> tuple[list[Driver], list[Issue]]:
    drivers = []
    issues = []
    for line, row in enumerate(read_rows(path), start=2):
        if None in row.values():
            issues.append(Issue(file=path.name, line=line, message="Row has less values than expected"))
            continue
        if row["driver_id"] == "":
            issues.append(Issue(file=path.name, line=line, message="driver_id is empty"))
            continue
        if row["display_name"] == "":
            issues.append(Issue(file=path.name, line=line, message="display_name is empty"))
            continue
        d = Driver(driver_id=row["driver_id"], display_name=row["display_name"], nationality=blank_to_none(row["nationality"]), notes=blank_to_none(row["notes"]))
        drivers.append(d)
    return drivers, issues