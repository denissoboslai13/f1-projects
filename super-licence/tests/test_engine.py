from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from super_licence.engine import season_points, year_points, qualifying_points
from super_licence.models import Scale, Season, Standing

STANDING = Standing(series_id="f2", season=2025, driver_id="a", position=1, series_points=Decimal("100"),
                    source_url="x", fetch_date=date(2026, 11, 6), second_source_url=None,
                    status="confirmed", notes=None)
SEASON = Season(series_id="f2", season=2025, end_date=date(2025, 12, 7), status="completed",
                multiplier=Decimal("1.0"), multiplier_reason=None, source_url="x", notes=None)
SCALE = Scale(regulation_year=2025, series_id="f2", points=(40, 40, 40, 30, 20, 10, 8, 6, 4, 3),
              page=64, row_label="Formule 2 de la FIA / FIA Formula 2", notes=None)

SF_SCALE_2024 = Scale(regulation_year=2024, series_id="super-formula", points=(25, 20, 15, 10, 7, 5, 3, 2, 1, 0),
                      page=65, row_label="Japonese Super Formula / Japanese Super Formula", notes=None)
SF_SCALE_2025 = Scale(regulation_year=2025, series_id="super-formula", points=(30, 25, 20, 15, 12, 9, 7, 5, 3, 2),
                      page=64, row_label="Japonese Super Formula / Japanese Super Formula", notes=None)

def test_p1():
    result = season_points(STANDING, SEASON, SCALE)
    assert result.base_points == 40
    assert result.points == Decimal("40")


def test_p10():
    result = season_points(replace(STANDING, position=10), SEASON, SCALE)
    assert result.points == Decimal("3")


@pytest.mark.parametrize("position", [11, 20])
def test_outside_top_10_scores_zero(position):
    result = season_points(replace(STANDING, position=position), SEASON, SCALE)
    assert result.base_points == 0
    assert result.points == Decimal("0")

def test_super_formula_p1_differs_between_2024_and_2025():
    sf_standing = replace(STANDING, series_id="super-formula", season=2024)
    sf_season = replace(SEASON, series_id="super-formula", season=2024, end_date=date(2024, 12, 8))
    r2024 = season_points(sf_standing, sf_season, SF_SCALE_2024)

    r2025 = season_points(replace(sf_standing, season=2025),
                          replace(sf_season, season=2025, end_date=date(2025, 12, 14)),
                          SF_SCALE_2025)

    assert r2024.points == Decimal("25")
    assert r2025.points == Decimal("30")

def test_multiplier_below_one():
    f3_scale = Scale(regulation_year=2025, series_id="f3", points=(30, 25, 20, 15, 12, 9, 7, 5, 3, 2),
                     page=64, row_label="Formule 3 de la FIA / FIA Formula 3", notes=None)
    result = season_points(replace(STANDING, series_id="f3"),
                           replace(SEASON, series_id="f3", multiplier=Decimal("0.8")),
                           f3_scale)
    assert result.base_points == 30
    assert result.multiplier == Decimal("0.8")
    assert result.points == Decimal("24")

def test_wrong_series_scale_raises():
    f3_scale = replace(SCALE, series_id="f3")
    with pytest.raises(ValueError):
        season_points(STANDING, SEASON, f3_scale)


def test_wrong_season_raises():
    with pytest.raises(ValueError):
        season_points(replace(STANDING, season=2024), SEASON, SCALE)


def test_wrong_year_scale_raises():
    with pytest.raises(ValueError):
        season_points(STANDING, SEASON, replace(SCALE, regulation_year=2024))

def test_season_ending_next_year_uses_end_year_document():
    late_season = replace(SEASON, end_date=date(2026, 1, 18))
    scale_2026 = replace(SCALE, regulation_year=2026)
    result = season_points(STANDING, late_season, scale_2026)
    assert result.regulation_year == 2026

def test_explain_mentions_position_series_and_document_year():
    text = season_points(replace(STANDING, position=4), SEASON, SCALE).explain()
    assert "4" in text
    assert "f2" in text
    assert "2025" in text
    assert "30" in text

def test_year_two_series():
    sf_standing = replace(STANDING, series_id="super-formula", season=2025)
    sf_season = replace(SEASON, series_id="super-formula", season=2025, end_date=date(2025, 12, 8))

    driver_a_f2 = season_points(STANDING, SEASON, SCALE)
    driver_a_sf = season_points(sf_standing, sf_season, SF_SCALE_2025)

    result = year_points("a", 2025, [driver_a_f2, driver_a_sf])
    assert len(result.seasons) == 2
    assert result.total == Decimal("70.0")

def test_year_diff_driver():
    driver_a = season_points(STANDING, SEASON, SCALE)
    driver_b = season_points(replace(STANDING, driver_id="b", position=10), SEASON, SCALE)

    result = year_points("b", 2025, [driver_a, driver_b])
    assert len(result.seasons) == 1
    assert result.total == Decimal("3.0")

def test_year_diff_year():
    driver_a_2025 = season_points(STANDING, SEASON, SCALE)
    driver_a_2024 = season_points(replace(STANDING, season=2024, position=10), replace(SEASON, season=2024, end_date=date(2024, 12, 7)), replace(SCALE, regulation_year=2024))

    result = year_points("a", 2025, [driver_a_2024, driver_a_2025])
    assert len(result.seasons) == 1
    assert result.total == Decimal("40.0")

def test_q_window_i():
    driver_a_2023 = season_points(replace(STANDING, season=2023), replace(SEASON, season=2023, end_date=date(2023, 12, 7)), replace(SCALE, regulation_year=2023))
    driver_a_2024 = season_points(replace(STANDING, season=2024, position=2), replace(SEASON, season=2024, end_date=date(2024, 12, 7)), replace(SCALE, regulation_year=2024))
    driver_a_2025 = season_points(replace(STANDING, position=10), SEASON, SCALE)
    driver_a_2026 = season_points(replace(STANDING, season=2026, position=8), replace(SEASON, season=2026, end_date=date(2026, 12, 7)), replace(SCALE, regulation_year=2026))

    result = qualifying_points("a", 2026, [driver_a_2023, driver_a_2024, driver_a_2025, driver_a_2026])

    assert result.used == "i"
    assert result.total == Decimal("83.0")

def test_q_window_ii():
    driver_a_2023 = season_points(replace(STANDING, season=2023, position=10), replace(SEASON, season=2023, end_date=date(2023, 12, 7)), replace(SCALE, regulation_year=2023))
    driver_a_2024 = season_points(replace(STANDING, season=2024, position=6), replace(SEASON, season=2024, end_date=date(2024, 12, 7)), replace(SCALE, regulation_year=2024))
    driver_a_2025 = season_points(replace(STANDING, position=3), SEASON, SCALE)
    driver_a_2026 = season_points(replace(STANDING, season=2026), replace(SEASON, season=2026, end_date=date(2026, 12, 7)), replace(SCALE, regulation_year=2026))

    result = qualifying_points("a", 2026, [driver_a_2023, driver_a_2024, driver_a_2025, driver_a_2026])

    assert result.used == "ii"
    assert result.total == Decimal("90.0")

def test_q_window_equal():
    driver_a_2023 = season_points(replace(STANDING, season=2023, position=2), replace(SEASON, season=2023, end_date=date(2023, 12, 7)), replace(SCALE, regulation_year=2023))
    driver_a_2024 = season_points(replace(STANDING, season=2024, position=3), replace(SEASON, season=2024, end_date=date(2024, 12, 7)), replace(SCALE, regulation_year=2024))
    driver_a_2025 = season_points(replace(STANDING, position=3), SEASON, SCALE)
    driver_a_2026 = season_points(replace(STANDING, season=2026, position=2), replace(SEASON, season=2026, end_date=date(2026, 12, 7)), replace(SCALE, regulation_year=2026))

    result = qualifying_points("a", 2026, [driver_a_2023, driver_a_2024, driver_a_2025, driver_a_2026])

    assert result.total_i == result.total_ii
    assert result.used == "ii"
    assert result.total == Decimal("120.0")

def test_q_window_explain():
    driver_a_2023 = season_points(replace(STANDING, season=2023, position=2), replace(SEASON, season=2023, end_date=date(2023, 12, 7)), replace(SCALE, regulation_year=2023))
    driver_a_2024 = season_points(replace(STANDING, season=2024, position=3), replace(SEASON, season=2024, end_date=date(2024, 12, 7)), replace(SCALE, regulation_year=2024))
    driver_a_2025 = season_points(replace(STANDING, position=3), SEASON, SCALE)
    driver_a_2026 = season_points(replace(STANDING, season=2026, position=2), replace(SEASON, season=2026, end_date=date(2026, 12, 7)), replace(SCALE, regulation_year=2026))

    result = qualifying_points("a", 2026, [driver_a_2023, driver_a_2024, driver_a_2025, driver_a_2026])

    assert "application windows for 'a'" in result.explain()
    assert "120.0" in result.explain()
    assert "window ii" in result.explain()
    assert "qualifying total: 120.0" in result.explain()
