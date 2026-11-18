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
    line: int | None
    message: str
    severity: str = "error"

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

@dataclass(frozen=True)
class SeasonPoints:
    standing: Standing
    regulation_year: int
    scale: Scale
    base_points: int
    multiplier: Decimal
    points: Decimal

    def explain(self) -> str:
        return f"{self.standing.position} in {self.standing.series_id} {self.standing.season} -> {self.base_points} points as per FIA Appendix L {self.regulation_year} x {self.multiplier} = {self.points}"