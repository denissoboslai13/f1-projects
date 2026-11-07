from dataclasses import dataclass

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