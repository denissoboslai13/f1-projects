from dataclasses import replace
from super_licence.models import Standing, Driver
from decimal import Decimal
from datetime import date
from super_licence.validate import check_positions, check_unknown_drivers
from pathlib import Path
from super_licence.load import load_drivers, load_standings

BASE = Standing(series_id="f2", season=2024, driver_id="a", position=1, series_points=Decimal("100"),
                source_url="x", fetch_date=date(2026, 11, 6), second_source_url="y",
                status="confirmed", notes=None)

BASE_DRIVER = Driver(driver_id="a", display_name="A", nationality=None, notes=None)

DATA = Path(__file__).parent.parent / "data"   # same pattern as test_load.py

def test_gap_in_positions():
    standings = [BASE, replace(BASE, driver_id="b", position=3)]
    issues = check_positions(standings)
    assert [i.message for i in issues] == ["f2 2024 positions have gaps: [2]"]

def test_duplicate_does_not_leak_into_next_season():
    rows = ([replace(BASE, position=p) for p in [1, 2, 2, 3]]
            + [replace(BASE, season=2025, position=p) for p in [1, 2, 3]])
    issues = check_positions(rows)
    assert [i.message for i in issues] == ["f2 2024 duplicate positions: [2]"]

def test_clean():
    rows = ([replace(BASE, position=p) for p in [1, 2, 3, 4]])
    issues = check_positions(rows)
    assert issues == []

def test_duplicate_and_gap():
    rows = ([replace(BASE, position=p) for p in [1, 2, 2, 4]]
            + [replace(BASE, season=2025, position=p) for p in [1, 2, 3]])
    issues = check_positions(rows)
    assert [i.message for i in issues] == ["f2 2024 duplicate positions: [2]", "f2 2024 positions have gaps: [3]"]

def test_double_first_place():
    rows = ([replace(BASE, position=p) for p in [1, 1]])
    issues = check_positions(rows)
    assert [i.message for i in issues] == ["f2 2024 duplicate positions: [1]"]

def test_unknown_drivers():
    rows = ([replace(BASE, driver_id="a", position=1)] + [replace(BASE, driver_id="b", position=2)])
    drivers = ([BASE_DRIVER])
    issues = check_unknown_drivers(rows, drivers)
    assert [i.message for i in issues] == ["f2 2024 unknown driver b"]

def test_real_data_passes_checks():
    drivers, driver_issues = load_drivers(DATA / "drivers.csv")
    standings, standing_issues = load_standings(DATA / "standings.csv")

    assert driver_issues == []
    assert standing_issues == []

    assert check_unknown_drivers(standings, drivers) == []
    assert check_positions(standings) == []