from super_licence.models import Standing, Season, Scale, SeasonPoints

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