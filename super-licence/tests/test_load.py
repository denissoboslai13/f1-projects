from pathlib import Path
from super_licence.load import read_rows, load_drivers
from super_licence.models import Driver

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