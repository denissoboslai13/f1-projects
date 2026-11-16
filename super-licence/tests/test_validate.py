from dataclasses import replace
from super_licence.models import Standing, Driver, Season, Scale
from decimal import Decimal
from datetime import date
from super_licence.validate import check_positions, check_unknown_drivers, check_scales_exist, check_duplicate_drivers, check_two_series_per_year, check_end_date_year, check_scale_order, validate_all
from pathlib import Path
from super_licence.load import load_drivers, load_standings, load_seasons, load_scales

BASE = Standing(series_id="f2", season=2024, driver_id="a", position=1, series_points=Decimal("100"),
                source_url="x", fetch_date=date(2026, 11, 6), second_source_url="y",
                status="confirmed", notes=None)
BASE_DRIVER = Driver(driver_id="a", display_name="A", nationality=None, notes=None)
BASE_SEASON = Season(series_id="f2", season=2024, end_date=date(2024,12,8), status="completed", multiplier=Decimal("1.0"), multiplier_reason=None, source_url="https://www.fiaformula2.com/en/latest/article/fia-formula-2-championship-2024-season-calendar-announced.4D3ZkvVJypjS5a0p4BmGHM", notes=None)
BASE_SCALE = Scale(regulation_year=2024, series_id="f2", points=(40,40,40,30,20,10,8,6,4,3), page=65, row_label="Formule 2 de la FIA / FIA Formula 2", notes=None)

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

def test_scales_fixture():
    assert check_scales_exist([BASE], [BASE_SEASON], [BASE_SCALE]) == []

def test_standing_no_season():
    season_n = [replace(BASE_SEASON, season=2025)]
    issues = check_scales_exist([BASE], season_n, [BASE_SCALE])
    assert len(issues) == 1
    assert [i.message for i in issues] == ["f2 2024: no season row"]

def test_wrong_end_date():
    season_n = [replace(BASE_SEASON, end_date=date(2030, 12, 8))]
    issues = check_scales_exist([BASE], season_n, [BASE_SCALE])
    assert len(issues) == 1
    assert [i.message for i in issues] == ["f2 2024: no scale for end year 2030"]

def test_duplicate_driver():
    standings = [BASE, replace(BASE, position=2), replace(BASE, driver_id="b", position=3), replace(BASE, driver_id="b", position=4)]
    issues = check_duplicate_drivers(standings)
    assert len(issues) == 1
    assert [i.message for i in issues] == ["f2 2024 duplicate driver(s): ['a', 'b']"]

def test_triple_driver():
    standings = [BASE, replace(BASE, position=2), replace(BASE, position=3)]
    issues = check_duplicate_drivers(standings)
    assert len(issues) == 1
    assert [i.message for i in issues] == ["f2 2024 duplicate driver(s): ['a']"]

def test_diff_season():
    standings = [BASE, replace(BASE, season=2025)]
    issues = check_duplicate_drivers(standings)
    assert issues == []

def test_multiple_seasons():
    standings, standing_issues = load_standings(DATA / "standings.csv")
    seasons, season_issues = load_seasons(DATA / "seasons.csv")

    assert standing_issues == []
    assert season_issues == []

    issues = check_two_series_per_year(standings, seasons)
    assert issues == []

def test_multiple_seasons_wrong():
    standings = [BASE, replace(BASE, series_id="f3")]
    seasons = [BASE_SEASON, replace(BASE_SEASON, series_id="f3")]

    issues = check_two_series_per_year(standings, seasons)
    assert len(issues) == 1
    assert [i.message for i in issues] == ["a 2024 multiple series: ['f2', 'f3']"]
    assert issues[0].severity == "warning"

def test_diff_seasons():
    standings = [BASE, replace(BASE, series_id="f3")]
    seasons = [BASE_SEASON, replace(BASE_SEASON, series_id="f3", end_date=date(2025, 11, 8))]

    issues = check_two_series_per_year(standings, seasons)
    assert issues == []

def test_end_date_year():
    seasons, season_issues = load_seasons(DATA / "seasons.csv")
    
    assert season_issues == []

    issues = check_end_date_year(seasons)
    assert issues == []

def test_end_date_year_mismatch():
    season = [replace(BASE_SEASON, end_date=date(2030, 12, 8))]

    issues = check_end_date_year(season)
    assert len(issues) == 1
    assert [i.message for i in issues] == ["f2 2024 end date year is: 2030"]
    assert issues[0].severity == "warning"

def test_scale_order():
    scales, scale_issues = load_scales(DATA / "scales.csv")
    assert scale_issues == []

    issues = check_scale_order(scales)
    assert issues == []

def test_scale_wrong():
    scale = [replace(BASE_SCALE, points=(40,50,40,30,20,10,8,6,4,3))]

    issues = check_scale_order(scale)
    assert len(issues) == 1
    assert [i.message for i in issues] == ["f2 2024 scale order is wrong: (40, 50)"]

def test_real_data_passes_checks():
    drivers, driver_issues = load_drivers(DATA / "drivers.csv")
    standings, standing_issues = load_standings(DATA / "standings.csv")
    seasons, season_issues = load_seasons(DATA / "seasons.csv")
    scales, scale_issues = load_scales(DATA / "scales.csv")

    assert driver_issues == []
    assert standing_issues == []
    assert season_issues == []
    assert scale_issues == []

    issues = validate_all(drivers, standings, seasons, scales)
    assert issues == []
