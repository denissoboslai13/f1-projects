from pathlib import Path
from super_licence.load import read_rows, load_drivers, load_standings, load_seasons, load_scales
from super_licence.models import Driver, Standing, Season, Scale
from decimal import Decimal
from datetime import date

DATA = Path(__file__).parent.parent / "data"   # path relative to this test file, not the terminal
WRONG_DRIVERS = Path(__file__).parent / "fixtures" / "drivers_broken.csv"
WRONG_STANDINGS = Path(__file__).parent / "fixtures" / "standings_broken.csv"
WRONG_SEASONS = Path(__file__).parent / "fixtures" / "seasons_broken.csv"
WRONG_SCALES = Path(__file__).parent / "fixtures" / "scales_broken.csv"

def test_read_drivers():
    rows = read_rows(DATA / "drivers.csv")
    assert len(rows) == 24
    assert rows[0]["driver_id"] == "leonardo-fornaroli"

def test_driver_class():
    drivers, issues = load_drivers(DATA / "drivers.csv")
    assert len(drivers) == 24
    first = drivers[0]
    assert first == Driver(driver_id="leonardo-fornaroli", display_name="Leonardo Fornaroli", nationality="ITA", notes=None)
    assert issues == []

def test_driver_negative():
    drivers, issues = load_drivers(WRONG_DRIVERS)
    assert len(drivers) == 1
    assert drivers[0].driver_id == "leonardo-fornaroli"
    assert [i.line for i in issues] == [3, 4]

def test_standing_class():
    standings, issues = load_standings(DATA / "standings.csv")
    assert issues == []
    assert len(standings) == 30
    assert standings[0] == Standing(series_id="f2", season=2025, driver_id="leonardo-fornaroli",
                                    position=1, series_points=Decimal("211"), source_url="https://en.wikipedia.org/wiki/2025_Formula_2_Championship#Results_and_standings",
                                    fetch_date=date(2026, 11, 6), second_source_url="https://www.motorsport.com/fia-f2/standings/2025/", 
                                    status="confirmed",notes=None)

    decimal_test = standings[10]
    assert decimal_test.series_points == Decimal("214.5")

def test_standing_negative():
    standings, issues = load_standings(WRONG_STANDINGS)
    assert len(standings) == 1
    print(standings, issues)

def test_season_class():
    seasons, issues = load_seasons(DATA / "seasons.csv")
    assert issues == []
    assert len(seasons) == 25
    assert seasons[0] == Season(series_id='f2', season=2022, end_date=date(2022, 11, 20), status='completed', multiplier=Decimal('1.0'), multiplier_reason=None, source_url='https://www.fiaformula2.com/en/latest/article/fia-formula-2-championship-2022-season-calendar-announced.17xLlSIJ5U2K8Fje0YvUbM', notes=None)

def test_season_negative():
    seasons, issues = load_seasons(WRONG_SEASONS)
    assert len(seasons) == 1
    print(seasons, issues)

def test_scale_class():
    scales, issues = load_scales(DATA / "scales.csv")
    assert issues == []
    assert len(scales) == 25
    sf2024 = scales[14]
    sf2025 = scales[19]
    assert sf2024.points != sf2025.points
    assert scales[0] == Scale(regulation_year=2022, series_id='f2', points=(40, 40, 40, 30, 20, 10, 8, 6, 4, 3), page=60, row_label='Formule 2 de la FIA / FIA Formula 2', notes=None)

def test_scale_negative():
    scales, issues = load_scales(WRONG_SCALES)
    assert len(scales) == 1
    print(scales, issues)