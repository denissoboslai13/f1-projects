from decimal import Decimal
from super_licence.models import Standing, Season, Scale, SeasonPoints, YearPoints, QualifyingPoints

def season_points(standing: Standing, season: Season, scale: Scale) -> SeasonPoints:
    seasons_match = standing.season == season.season and season.end_date.year == scale.regulation_year
    series_match = standing.series_id == scale.series_id and standing.series_id == season.series_id

    if not seasons_match or not series_match:
        raise ValueError(f"not the same year or series_id")
    
    if standing.position > 10:
        base_points = 0
    else:
        base_points = scale.points[standing.position - 1]
    
    return SeasonPoints(standing=standing, regulation_year=season.end_date.year, scale=scale, base_points=base_points, multiplier=season.multiplier, points=base_points*season.multiplier)

def year_points(driver_id: str, year: int, all_points: list[SeasonPoints]) -> YearPoints:
    kept = []
    total = Decimal("0")

    for sp in all_points:
        if sp.standing.driver_id != driver_id:
            continue
        if sp.regulation_year != year:
            continue
        kept.append(sp)
        total += sp.points

    return YearPoints(driver_id=driver_id, year=year, seasons=tuple(kept), total=total)

def qualifying_points(driver_id: str, application_year: int, all_points: list[SeasonPoints]) -> QualifyingPoints:
    window_i = []
    window_ii = []
    for y in range(application_year - 3, application_year):
        window_i.append(year_points(driver_id, y, all_points))
    for y in range(application_year - 2, application_year + 1):
        window_ii.append(year_points(driver_id, y, all_points))

    total_i = Decimal("0.0")
    total_ii = Decimal("0.0")
    for yp in window_i:
        total_i += yp.total
    for yp in window_ii:
        total_ii += yp.total

    if total_i > total_ii:
        used = "i"
        total = total_i
    else:
        # My own decision, if the windows totals are tied, use the more recent one, not backed up by any official document
        used = "ii"
        total = total_ii
    return QualifyingPoints(driver_id=driver_id, application_year=application_year, window_i=tuple(window_i), window_ii=tuple(window_ii), total_i=total_i, total_ii=total_ii, used=used, total=total)