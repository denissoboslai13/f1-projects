from pathlib import Path
from super_licence.load import read_rows, load_drivers, load_standings, load_seasons, load_scales, DRIVER_COLUMNS
from super_licence.models import Driver, Standing, Season, Scale, Issue
from decimal import Decimal
from datetime import date

DATA = Path(__file__).parent.parent / "data"
WRONG_DRIVERS = Path(__file__).parent / "fixtures" / "drivers_broken.csv"
WRONG_STANDINGS = Path(__file__).parent / "fixtures" / "standings_broken.csv"
WRONG_SEASONS = Path(__file__).parent / "fixtures" / "seasons_broken.csv"
WRONG_SCALES = Path(__file__).parent / "fixtures" / "scales_broken.csv"

def test_read_drivers():
    rows, issues = read_rows(DATA / "drivers.csv", DRIVER_COLUMNS)
    assert issues == []
    assert len(rows) == 24
    line, first = rows[0]
    assert line == 2
    assert first["driver_id"] == "leonardo-fornaroli"

def test_driver_class():
    drivers, issues = load_drivers(DATA / "drivers.csv")
    assert len(drivers) == 24
    first = drivers[0]
    assert first == Driver(driver_id="leonardo-fornaroli", display_name="Leonardo Fornaroli", nationality="ITA", notes=None)
    assert issues == []

def test_driver_negative():
    drivers, issues = load_drivers(WRONG_DRIVERS)
    assert len(drivers) == 3
    assert drivers == [Driver(driver_id='leonardo-fornaroli', display_name='Leonardo Fornaroli', nationality='ITA', notes=None), Driver(driver_id='luke-browning', display_name='Luke Browning', nationality=None, notes=None), Driver(driver_id='roman-stanek', display_name='Roman Staněk', nationality='CZE', notes=None)]
    assert [(i.line, i.message) for i in issues] == [
        (3, "empty: driver_id"),
        (4, "Wrong number of fields")
    ]
    

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
    assert len(standings) == 2
    assert standings == [Standing(series_id='f2', season=2025, driver_id='leonardo-fornaroli', 
                                  position=1, series_points=Decimal('211'), source_url='https://en.wikipedia.org/wiki/2025_Formula_2_Championship#Results_and_standings', 
                                  fetch_date=date(2026, 11, 6), second_source_url='https://www.motorsport.com/fia-f2/standings/2025/', 
                                  status='confirmed', notes=None), Standing(series_id='f2', season=2025, driver_id='roman-stanek', position=10, series_points=Decimal('105'), source_url='https://en.wikipedia.org/wiki/2025_Formula_2_Championship#Results_and_standings', fetch_date=date(2026, 11, 6), second_source_url='https://www.motorsport.com/fia-f2/standings/2025/', status='confirmed', notes=None)]
    assert [(i.line, i.message) for i in issues] == [
        (3, "empty: series_id"),
        (4, "empty: season"),
        (5, "empty: driver_id"),
        (6, "empty: position"),
        (7, "empty: series_points"),
        (8, "empty: source_url"),
        (9, "empty: fetch_date"),
        (10, "status is confirmed, but no second source url was given"),
        (11, "empty: status"),
        (13, "position is less than one"),
        (14, "idk not accepted as a status"),
        (15, "series_points is not finite or negative"),
        (16, "series not recognized"),
        (17, "issue with parsing data: column season has bad value of 20x5")
    ]

def test_season_class():
    seasons, issues = load_seasons(DATA / "seasons.csv")
    assert issues == []
    assert len(seasons) == 25
    assert seasons[0] == Season(series_id='f2', season=2022, end_date=date(2022, 11, 20), status='completed', multiplier=Decimal('1.0'), multiplier_reason=None, source_url='https://www.fiaformula2.com/en/latest/article/fia-formula-2-championship-2022-season-calendar-announced.17xLlSIJ5U2K8Fje0YvUbM', notes=None)

def test_season_negative():
    seasons, issues = load_seasons(WRONG_SEASONS)
    assert len(seasons) == 1
    assert seasons == [Season(series_id='f2', season=2022, end_date=date(2022, 11, 20), status='completed', multiplier=Decimal('1.0'), multiplier_reason=None, source_url='https://www.fiaformula2.com/en/latest/article/fia-formula-2-championship-2022-season-calendar-announced.17xLlSIJ5U2K8Fje0YvUbM', notes=None)]
    assert [(i.line, i.message) for i in issues] == [
        (3, "empty: series_id"),
        (4, "empty: season"),
        (5, "empty: end_date"),
        (6, "Wrong number of fields"),
        (7, "empty: status"),
        (8, "empty: multiplier"),
        (9, "empty: source_url"),
        (11, "done not accepted as a status"),
        (12, "multiplier is outside normal range"),
        (13, "multiplier is not 1 but no reason was given"),
        (14, "multiplier is outside normal range"),
        (15, "multiplier is outside normal range"),
        (16, "series not recognized"),
        (17, 'issue with parsing data: column multiplier has bad value of abc'),
        (19, 'multiplier is not 1 but no reason was given')
    ]
    
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
    assert scales == [Scale(regulation_year=2022, series_id='f2', points=(40, 40, 40, 30, 20, 10, 8, 6, 4, 3), page=60, row_label='Formule 2 de la FIA / FIA Formula 2', notes=None)]
    assert [(i.line, i.message) for i in issues] == [
        (3, "empty: regulation_year"),
        (4, "empty: series_id"),
        (5, "empty: p3"),
        (6, "empty: row_label"),
        (8, "series not recognized"),
        (9, "points include negative value"),
        (10, 'issue with parsing data: column p4 has bad value of x')
    ]

def test_read_rows_empty_file(tmp_path):
    path = tmp_path / "drivers.csv"
    path.write_text("", encoding="utf-8")

    rows, issues = read_rows(path, DRIVER_COLUMNS)

    assert rows == []
    assert issues == [Issue(file="drivers.csv", line=1, message="file is empty")]

def test_read_rows_no_data_rows(tmp_path):
    path = tmp_path / "drivers.csv"
    path.write_text("driver_id,display_name,nationality,notes\n", encoding="utf-8")

    rows, issues = read_rows(path, DRIVER_COLUMNS)

    assert rows == []
    assert issues == [Issue(file="drivers.csv", line=1, message="no data rows")]


def test_read_rows_renamed_column(tmp_path):
    path = tmp_path / "drivers.csv"
    path.write_text("driver_id,display_name,nation,notes\nleonardo-fornaroli,Leonardo Fornaroli,ITA,", encoding="utf-8")

    rows, issues = read_rows(path, DRIVER_COLUMNS)

    assert rows == []
    assert issues == [Issue(file="drivers.csv", line=1, message="wrong columns, missing: ['nationality'], unexpected: ['nation']")]

def test_read_rows_duplicate_column(tmp_path):
    path = tmp_path / "drivers.csv"
    path.write_text("driver_id,display_name,nationality,notes,notes\nleonardo-fornaroli,Leonardo Fornaroli,ITA,", encoding="utf-8")

    rows, issues = read_rows(path, DRIVER_COLUMNS)

    assert rows == []
    assert issues == [Issue(file="drivers.csv", line=1, message="duplicate column name")]

def test_read_rows_BOM(tmp_path):
    path = tmp_path / "drivers.csv"
    path.write_text("driver_id,display_name,nationality,notes\nleonardo-fornaroli,Leonardo Fornaroli,ITA,", encoding="utf-8-sig")

    rows, issues = read_rows(path, DRIVER_COLUMNS)

    assert issues == []
    assert rows[0][1]["driver_id"] == "leonardo-fornaroli"

def test_read_rows_blank_line(tmp_path):
    path = tmp_path / "drivers.csv"
    path.write_text("driver_id,display_name,nationality,notes\nleonardo-fornaroli,Leonardo Fornaroli,ITA,\n\n,Leonardo Fornaroli,ITA,", encoding="utf-8")

    drivers, issues = load_drivers(path)
    assert drivers == [Driver(driver_id='leonardo-fornaroli', display_name='Leonardo Fornaroli', nationality='ITA', notes=None)]
    assert issues == [Issue(file="drivers.csv", line=4, message="empty: driver_id")]