import csv
from pathlib import Path
from super_licence.models import Driver, Issue, Standing, Season, Scale
from decimal import Decimal, InvalidOperation
from datetime import date

def read_rows(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def blank_to_none(value: str) -> str | None:
    if value == "":
        return None

    return value

def empty_required(row: dict[str, str], optional: set[str]) -> list[str]:
    """Names of the columns that are empty and not optional."""
    empty = []
    for key in row.keys():
        item = row[key].strip()
        if item == "" and key not in optional:
            empty.append(key)
    return empty

def load_drivers(path: Path) -> tuple[list[Driver], list[Issue]]:
    drivers = []
    issues = []
    for line, row in enumerate(read_rows(path), start=2):
        if None in row.values() or None in row:
            issues.append(Issue(file=path.name, line=line, message="Wrong number of fields"))
            continue
        empty = empty_required(row, optional={"notes"})
        if empty:
            issues.append(Issue(file=path.name, line=line, message=f"empty: {', '.join(empty)}"))
            continue
        d = Driver(driver_id=row["driver_id"], display_name=row["display_name"], nationality=blank_to_none(row["nationality"]), notes=blank_to_none(row["notes"]))
        drivers.append(d)
    return drivers, issues

def load_standings(path: Path) -> tuple[list[Standing], list[Issue]]:
    standings = []
    issues = []
    statuses = {"confirmed", "provisional", "manual"}
    for line, row in enumerate(read_rows(path), start=2):
        if None in row.values() or None in row:
            issues.append(Issue(file=path.name, line=line, message="Wrong number of fields"))
            continue
        empty = empty_required(row, optional={"second_source_url", "notes"})
        if empty:
            issues.append(Issue(file=path.name, line=line, message=f"empty: {', '.join(empty)}"))
            continue
        try:
            season = int(row["season"])
            position = int(row["position"])
            series_points = Decimal(row["series_points"])
            fetch_date = date.fromisoformat(row["fetch_date"])
        except (ValueError, InvalidOperation) as e:
            issues.append(Issue(file=path.name, line=line, message=f"issue with parsing data: {e}"))
            continue
        if position < 1:
            issues.append(Issue(file=path.name, line=line, message="position is less than one"))
            continue
        if row["status"] not in statuses:
            issues.append(Issue(file=path.name, line=line, message=f"{row["status"]} not accepted as a status"))
            continue
        if not series_points.is_finite() or series_points < 0:
            issues.append(Issue(file=path.name, line=line, message="series_points is not finite"))
            continue
        s = Standing(series_id=row["series_id"],season=season,driver_id=row["driver_id"],position=position,series_points=series_points,source_url=row["source_url"],fetch_date=fetch_date,second_source_url=blank_to_none(row["second_source_url"]),status=row["status"],notes=blank_to_none(row["notes"]))
        standings.append(s)
    return standings, issues

def load_seasons(path: Path) -> tuple[list[Season], list[Issue]]:
    seasons = []
    issues = []
    statuses = {"completed", "in_progress"}
    for line, row in enumerate(read_rows(path), start=2):
        if None in row.values() or None in row:
            issues.append(Issue(file=path.name, line=line, message="Wrong number of fields"))
            continue
        empty = empty_required(row, optional={"multiplier_reason", "notes"})
        if empty:
            issues.append(Issue(file=path.name, line=line, message=f"empty: {', '.join(empty)}"))
            continue
        try:
            season = int(row["season"])
            multiplier = Decimal(row["multiplier"])
            end_date = date.fromisoformat(row["end_date"])
        except (ValueError, InvalidOperation) as e:
            issues.append(Issue(file=path.name, line=line, message=f"issue with parsing data: {e}"))
            continue
        if multiplier < Decimal("0.0"):
            issues.append(Issue(file=path.name, line=line, message="multiplier is negative"))
            continue
        if row["status"] not in statuses:
            issues.append(Issue(file=path.name, line=line, message=f"{row["status"]} not accepted as a status"))
            continue
        s = Season(series_id=row["series_id"],season=season,end_date=end_date,status=row["status"],multiplier=multiplier, multiplier_reason=row["multiplier_reason"], source_url=row["source_url"], notes=blank_to_none(row["notes"]))
        seasons.append(s)
    return seasons, issues

"""
@dataclass(frozen=True)
class Scale:
    regulation_year: int
    series_id: str
    points: tuple[int, ...]
    page: int
    row_label: str
    notes: str | None
"""

def load_scales(path: Path) -> tuple[list[Scale], list[Issue]]:
    scales = []
    issues = []
    for line, row in enumerate(read_rows(path), start=2):
        if None in row.values() or None in row:
            issues.append(Issue(file=path.name, line=line, message="Wrong number of fields"))
            continue
        empty = empty_required(row, optional={"notes"})
        if empty:
            issues.append(Issue(file=path.name, line=line, message=f"empty: {', '.join(empty)}"))
            continue
        try:
            regulation_year = int(row["regulation_year"])
            points = (int(row["p1"]), int(row["p2"]), int(row["p3"]), int(row["p4"]), int(row["p5"]), int(row["p6"]), int(row["p7"]), int(row["p8"]), int(row["p9"]), int(row["p10"]))
            page = int(row["page"])
        except (ValueError, InvalidOperation) as e:
            issues.append(Issue(file=path.name, line=line, message=f"issue with parsing data: {e}"))
            continue
        s = Scale(regulation_year=regulation_year, series_id=row["series_id"], points=points, page=page, row_label=row["row_label"], notes=blank_to_none(row["notes"]))
        scales.append(s)
    return scales, issues