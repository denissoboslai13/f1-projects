import csv
from pathlib import Path
from super_licence.models import Driver, Issue, Standing, Season, Scale
from decimal import Decimal, InvalidOperation
from datetime import date

SERIES = {'f2', 'f3', 'freca', 'super-formula', 'indycar'}
POINT_COLUMNS = [f"p{i}" for i in range(1, 11)]   # ["p1", "p2", ..., "p10"]
DRIVER_COLUMNS = {"driver_id", "display_name", "nationality", "notes"}
STANDING_COLUMNS = {"series_id", "season", "driver_id", "position", "series_points",
                    "source_url", "fetch_date", "second_source_url", "status", "notes"}
SEASON_COLUMNS = {"series_id", "season", "end_date", "status", "multiplier",
                  "multiplier_reason", "source_url", "notes"}
SCALE_COLUMNS = {"regulation_year", "series_id", *POINT_COLUMNS, "page", "row_label", "notes"}

def clean_row(row: dict) -> dict:
    return {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}

def read_rows(path: Path, expected: set[str]) -> tuple[list[tuple[int, dict[str, str]]], list[Issue]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames

        if header is None:
            return [], [Issue(file=path.name, line=1, message="file is empty")]

        missing = expected - set(header)
        extra = set(header) - expected
        if missing or extra:
            return [], [Issue(file=path.name, line=1, message=f"wrong columns, missing: {sorted(missing)}, unexpected: {sorted(extra)}")]
        if len(header) != len(set(header)):
            return [], [Issue(file=path.name, line=1, message="duplicate column name")]

        rows = [(reader.line_num, clean_row(row)) for row in reader]

    if not rows:
        return [], [Issue(file=path.name, line=1, message="no data rows")]
    return rows, []

def blank_to_none(value: str) -> str | None:
    if value == "":
        return None

    return value

def empty_required(row: dict[str, str], optional: set[str]) -> list[str]:
    empty = []
    for key in row.keys():
        item = row[key].strip()
        if item == "" and key not in optional:
            empty.append(key)
    return empty

def check_series_id(row: dict[str, str]):
    if row["series_id"] not in SERIES:
        return False

    return True

def parse_field(row: dict[str, str], column: str, convert):
    try:
        return convert(row[column])
    except (ValueError, InvalidOperation):
        raise ValueError(f"column {column} has bad value of {row[column]}")


def load_drivers(path: Path) -> tuple[list[Driver], list[Issue]]:
    drivers = []
    rows, issues = read_rows(path, DRIVER_COLUMNS)
    for line, row in rows:
        if None in row.values() or None in row:
            issues.append(Issue(file=path.name, line=line, message="Wrong number of fields"))
            continue
        empty = empty_required(row, optional={"nationality", "notes"})
        if empty:
            issues.append(Issue(file=path.name, line=line, message=f"empty: {', '.join(empty)}"))
            continue
        d = Driver(driver_id=row["driver_id"], display_name=row["display_name"], nationality=blank_to_none(row["nationality"]), notes=blank_to_none(row["notes"]))
        drivers.append(d)
    return drivers, issues

def load_standings(path: Path) -> tuple[list[Standing], list[Issue]]:
    standings = []
    statuses = {"confirmed", "provisional", "manual"}
    rows, issues = read_rows(path, STANDING_COLUMNS)
    for line, row in rows:
        if None in row.values() or None in row:
            issues.append(Issue(file=path.name, line=line, message="Wrong number of fields"))
            continue
        empty = empty_required(row, optional={"second_source_url", "notes"})
        if empty:
            issues.append(Issue(file=path.name, line=line, message=f"empty: {', '.join(empty)}"))
            continue
        try:
            season = parse_field(row, "season", int)
            position = parse_field(row, "position", int)
            series_points = parse_field(row, "series_points", Decimal)
            fetch_date = parse_field(row, "fetch_date", date.fromisoformat)
        except ValueError as e:
            issues.append(Issue(file=path.name, line=line, message=f"issue with parsing data: {e}"))
            continue
        if position < 1:
            issues.append(Issue(file=path.name, line=line, message="position is less than one"))
            continue
        if row["status"] not in statuses:
            issues.append(Issue(file=path.name, line=line, message=f"{row["status"]} not accepted as a status"))
            continue
        if not series_points.is_finite() or series_points < 0:
            issues.append(Issue(file=path.name, line=line, message="series_points is not finite or negative"))
            continue
        if row["status"] == "confirmed" and row["second_source_url"] == "":
            issues.append(Issue(file=path.name, line=line, message="status is confirmed, but no second source url was given"))
            continue
        if not check_series_id(row):
            issues.append(Issue(file=path.name, line=line, message="series not recognized"))
            continue
        s = Standing(series_id=row["series_id"],season=season,driver_id=row["driver_id"],position=position,series_points=series_points,source_url=row["source_url"],fetch_date=fetch_date,second_source_url=blank_to_none(row["second_source_url"]),status=row["status"],notes=blank_to_none(row["notes"]))
        standings.append(s)
    return standings, issues

def load_seasons(path: Path) -> tuple[list[Season], list[Issue]]:
    seasons = []
    statuses = {"completed", "in_progress"}
    rows, issues = read_rows(path, SEASON_COLUMNS)
    for line, row in rows:
        if None in row.values() or None in row:
            issues.append(Issue(file=path.name, line=line, message="Wrong number of fields"))
            continue
        empty = empty_required(row, optional={"multiplier_reason", "notes"})
        if empty:
            issues.append(Issue(file=path.name, line=line, message=f"empty: {', '.join(empty)}"))
            continue
        try:
            season = parse_field(row, "season", int)
            multiplier = parse_field(row, "multiplier", Decimal)
            end_date = parse_field(row, "end_date", date.fromisoformat)
        except ValueError as e:
            issues.append(Issue(file=path.name, line=line, message=f"issue with parsing data: {e}"))
            continue
        if not multiplier.is_finite() or multiplier <= Decimal("0.0") or multiplier > Decimal("1.0"):
            issues.append(Issue(file=path.name, line=line, message="multiplier is outside normal range"))
            continue
        if multiplier < Decimal("1.0") and row["multiplier_reason"] == "":
            issues.append(Issue(file=path.name, line=line, message="multiplier is not 1 but no reason was given"))
            continue
        if row["status"] not in statuses:
            issues.append(Issue(file=path.name, line=line, message=f"{row["status"]} not accepted as a status"))
            continue
        if not check_series_id(row):
            issues.append(Issue(file=path.name, line=line, message="series not recognized"))
            continue
        s = Season(series_id=row["series_id"],season=season,end_date=end_date,status=row["status"],multiplier=multiplier, multiplier_reason=blank_to_none(row["multiplier_reason"]), source_url=row["source_url"], notes=blank_to_none(row["notes"]))
        seasons.append(s)
    return seasons, issues

def load_scales(path: Path) -> tuple[list[Scale], list[Issue]]:
    scales = []
    rows, issues = read_rows(path, SCALE_COLUMNS)
    for line, row in rows:
        if None in row.values() or None in row:
            issues.append(Issue(file=path.name, line=line, message="Wrong number of fields"))
            continue
        empty = empty_required(row, optional={"notes"})
        if empty:
            issues.append(Issue(file=path.name, line=line, message=f"empty: {', '.join(empty)}"))
            continue
        try:
            regulation_year = parse_field(row, "regulation_year", int)
            points = tuple(parse_field(row, col, int) for col in POINT_COLUMNS)
            page = parse_field(row, "page", int)
        except ValueError as e:
            issues.append(Issue(file=path.name, line=line, message=f"issue with parsing data: {e}"))
            continue
        if not check_series_id(row):
            issues.append(Issue(file=path.name, line=line, message="series not recognized"))
            continue
        if any(p < 0 for p in points):
            issues.append(Issue(file=path.name, line=line, message="points include negative value"))
            continue
        s = Scale(regulation_year=regulation_year, series_id=row["series_id"], points=points, page=page, row_label=row["row_label"], notes=blank_to_none(row["notes"]))
        scales.append(s)
    return scales, issues