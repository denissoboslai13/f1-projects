from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from super_licence.engine import season_points
from super_licence.models import Scale, Season, Standing

# One matching set: F2 2025. Change only the field a test is about with replace().
STANDING = Standing(series_id="f2", season=2025, driver_id="a", position=1, series_points=Decimal("100"),
                    source_url="x", fetch_date=date(2026, 11, 6), second_source_url=None,
                    status="confirmed", notes=None)
SEASON = Season(series_id="f2", season=2025, end_date=date(2025, 12, 7), status="completed",
                multiplier=Decimal("1.0"), multiplier_reason=None, source_url="x", notes=None)
SCALE = Scale(regulation_year=2025, series_id="f2", points=(40, 40, 40, 30, 20, 10, 8, 6, 4, 3),
              page=64, row_label="Formule 2 de la FIA / FIA Formula 2", notes=None)

# Super Formula rows copied from scales.csv: the scale changed in the 2025 document.
SF_SCALE_2024 = Scale(regulation_year=2024, series_id="super-formula", points=(25, 20, 15, 10, 7, 5, 3, 2, 1, 0),
                      page=65, row_label="Japonese Super Formula / Japanese Super Formula", notes=None)
SF_SCALE_2025 = Scale(regulation_year=2025, series_id="super-formula", points=(30, 25, 20, 15, 12, 9, 7, 5, 3, 2),
                      page=64, row_label="Japonese Super Formula / Japanese Super Formula", notes=None)


# --- position lookup ---

def test_p1():
    # scales.csv 2025 f2 p1 = 40, x 1.0
    result = season_points(STANDING, SEASON, SCALE)
    assert result.base_points == 40
    assert result.points == Decimal("40")


def test_p10():
    # last scoring position: 2025 f2 p10 = 3
    result = season_points(replace(STANDING, position=10), SEASON, SCALE)
    assert result.points == Decimal("3")


@pytest.mark.parametrize("position", [11, 20])
def test_outside_top_10_scores_zero(position):
    result = season_points(replace(STANDING, position=position), SEASON, SCALE)
    assert result.base_points == 0
    assert result.points == Decimal("0")


# --- the year's document decides the scale ---

def test_super_formula_p1_differs_between_2024_and_2025():
    # 2024 document: 25 for P1. 2025 document: 30 for P1.
    sf_standing = replace(STANDING, series_id="super-formula", season=2024)
    sf_season = replace(SEASON, series_id="super-formula", season=2024, end_date=date(2024, 12, 8))
    r2024 = season_points(sf_standing, sf_season, SF_SCALE_2024)

    r2025 = season_points(replace(sf_standing, season=2025),
                          replace(sf_season, season=2025, end_date=date(2025, 12, 14)),
                          SF_SCALE_2025)

    assert r2024.points == Decimal("25")
    assert r2025.points == Decimal("30")


# --- multiplier ---

def test_multiplier_below_one():
    # F3 2025 p1 = 30, x 0.8 = 24
    f3_scale = Scale(regulation_year=2025, series_id="f3", points=(30, 25, 20, 15, 12, 9, 7, 5, 3, 2),
                     page=64, row_label="Formule 3 de la FIA / FIA Formula 3", notes=None)
    result = season_points(replace(STANDING, series_id="f3"),
                           replace(SEASON, series_id="f3", multiplier=Decimal("0.8")),
                           f3_scale)
    assert result.base_points == 30
    assert result.multiplier == Decimal("0.8")
    assert result.points == Decimal("24")


# --- mismatched inputs fail loudly ---

def test_wrong_series_scale_raises():
    f3_scale = replace(SCALE, series_id="f3")
    with pytest.raises(ValueError):
        season_points(STANDING, SEASON, f3_scale)


def test_wrong_season_raises():
    # standing is from 2024, season and scale are 2025
    with pytest.raises(ValueError):
        season_points(replace(STANDING, season=2024), SEASON, SCALE)


def test_wrong_year_scale_raises():
    with pytest.raises(ValueError):
        season_points(STANDING, SEASON, replace(SCALE, regulation_year=2024))


# --- championship ending in the next calendar year ---

def test_season_ending_next_year_uses_end_year_document():
    # Hypothetical: the 2025 season's final round is in January 2026.
    # Supplement 1 notes i/ii: the year the championship ends picks the document,
    # so the 2026 scale applies and regulation_year is 2026.
    late_season = replace(SEASON, end_date=date(2026, 1, 18))
    scale_2026 = replace(SCALE, regulation_year=2026)
    result = season_points(STANDING, late_season, scale_2026)
    assert result.regulation_year == 2026


# --- explanation ---

def test_explain_mentions_position_series_and_document_year():
    text = season_points(replace(STANDING, position=4), SEASON, SCALE).explain()
    # check the key parts, not the exact wording
    assert "4" in text
    assert "f2" in text
    assert "2025" in text
    assert "30" in text
