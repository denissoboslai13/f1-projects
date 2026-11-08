from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass(frozen=True)
class Driver:
    driver_id: str
    display_name: str
    nationality: str | None
    notes: str | None

@dataclass(frozen=True)
class Issue:
    file: str
    line: int
    message: str

@dataclass(frozen=True)
class Scale:
    regulation_year: int
    series_id: str
    points: tuple[int, ...]
    page: int
    row_label: str
    notes: str | None

@dataclass(frozen=True)
class Season:
    series_id: str
    season: int
    end_date: date
    status: str
    multiplier: Decimal
    multiplier_reason: str | None
    source_url: str
    notes: str | None

@dataclass(frozen=True)
class Standing:
    series_id: str
    season: int
    driver_id: str
    position: int
    series_points: Decimal
    source_url: str
    fetch_date: date
    second_source_url: str | None
    status: str
    notes: str | None