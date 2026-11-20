from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import textwrap

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

@dataclass(frozen=True)
class YearPoints:
    driver_id: str
    year: int
    seasons: tuple[SeasonPoints, ...]
    total: Decimal

    def explain(self) -> str:
        lines = [f"{self.year}: {self.total} points"]
        for sp in self.seasons:
            lines.append(" " + sp.explain())
        return "\n".join(lines)

@dataclass(frozen=True)
class QualifyingPoints:
    driver_id: str
    application_year: int
    window_i: tuple[YearPoints, ...]
    window_ii: tuple[YearPoints, ...]
    total_i: Decimal
    total_ii: Decimal
    used: str
    total: Decimal

    def explain(self) -> str:
        lines = [f"\napplication windows for '{self.driver_id}'", f"{self.application_year} windows: "]
        lines.append(" " + "window i " + f"({self.application_year - 3} - {self.application_year - 1}): {self.total_i}")
        for yp in self.window_i:
            #lines.append()
            lines.append(textwrap.indent(yp.explain(), "    "))
        lines.append(" " + "window ii " + f"({self.application_year - 2} - {self.application_year}): {self.total_ii}") 
        for yp in self.window_ii:
            lines.append(textwrap.indent(yp.explain(), "    "))

        if self.total_i == self.total_ii:
            lines.append(" " + "note: on a tie, window ii is used")
        lines.append(f"qualifying total: {self.total} (window {self.used})")
        return "\n".join(lines)