from pathlib import Path
from super_licence.load import read_rows, load_drivers, load_standings, load_seasons, load_scales
from super_licence.models import Driver, Standing
from decimal import Decimal
from datetime import date

DATA = Path(__file__).parent.parent / "data"   # path relative to this test file, not the terminal
DATA_WRONG = Path(__file__).parent / "fixtures" / "drivers_broken.csv"

def test_read_drivers():
    rows = read_rows(DATA / "drivers.csv")
    assert len(rows) == 24
    assert rows[0]["driver_id"] == "leonardo-fornaroli"

def test_driver_class():
    drivers, issues = load_drivers(DATA / "drivers.csv")
    assert len(drivers) == 24
    for i in range(len(drivers)):
        print(drivers[i])
    first = drivers[0]
    assert first == Driver(driver_id="leonardo-fornaroli", display_name="Leonardo Fornaroli", nationality="ITA", notes=None)
    assert issues == []

def test_driver_negative():
    drivers, issues = load_drivers(DATA_WRONG)
    print(drivers, issues)
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

def test_season_class():
    seasons, issues = load_seasons(DATA / "seasons.csv")
    print(seasons)

def test_scale_class():
    scales, issues = load_scales(DATA / "scales.csv")
    print(scales)