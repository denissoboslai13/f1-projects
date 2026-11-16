from collections import defaultdict, Counter
from super_licence.models import Driver, Issue, Standing, Season, Scale

def check_unknown_drivers(standings: list[Standing], drivers: list[Driver]) -> list[Issue]:
    known = {d.driver_id for d in drivers}
    issues = []
    for s in standings:
        if s.driver_id not in known:
            issues.append(Issue(file="standings.csv", line=None, message=f"{s.series_id} {s.season} unknown driver {s.driver_id}"))
    return issues

def check_positions(standings: list[Standing]) -> list[Issue]:
    by_season: dict[tuple[str, int], list[int]] = defaultdict(list)
    for s in standings:
        by_season[(s.series_id, s.season)].append(s.position)
    issues = []
    for (series_id, season), positions in by_season.items():
        if len(positions) != len(set(positions)):
            cnt = []
            for position, count in Counter(positions).items():
                if count > 1:
                    cnt.append(position)
            issues.append(Issue(file="standings.csv", line=None, message=f"{series_id} {season} duplicate positions: {cnt}"))
        gaps = set(range(1, max(positions) + 1)) - set(positions)
        if gaps:
            issues.append(Issue(file="standings.csv", line=None, message=f"{series_id} {season} positions have gaps: {sorted(gaps)}"))
    return issues

def check_scales_exist(standings, seasons, scales) -> list[Issue]:
    season_by_key = {(s.series_id, s.season): s for s in seasons}
    scale_keys = {(sc.regulation_year, sc.series_id) for sc in scales}
    issues = []
    for s in standings:
        if (s.series_id, s.season) not in season_by_key:
            issues.append(Issue(file="seasons.csv", line=None, message=f"{s.series_id} {s.season}: no season row"))
            continue
        season = season_by_key[(s.series_id, s.season)]
        year = season.end_date.year
        if (year, s.series_id) not in scale_keys:
            issues.append(Issue(file="scales.csv", line=None, message=f"{s.series_id} {s.season}: no scale for end year {year}"))
    return issues

def check_duplicate_drivers(standings: list[Standing]) -> list[Issue]:
    by_season: dict[tuple[str, int], list[str]] = defaultdict(list)
    for s in standings:
        by_season[(s.series_id, s.season)].append(s.driver_id)
    issues = []
    for (series_id, season), driver_ids in by_season.items():
        duplicates = []
        for driver_id, count in Counter(driver_ids).items():
            if count > 1:
                duplicates.append(driver_id)
        if duplicates:
            issues.append(Issue(file="standings.csv", line=None, message=f"{series_id} {season} duplicate driver(s): {duplicates}"))
    return issues

def check_two_series_per_year(standings, seasons) -> list[Issue]:
    season_by_key = {(s.series_id, s.season): s for s in seasons}
    series_by_driver_year: dict[tuple[str, int], set[str]] = defaultdict(set)
    for s in standings:
        season = season_by_key.get((s.series_id, s.season))
        if season is None:
            continue
        end_year = season.end_date.year
        series_by_driver_year[(s.driver_id, end_year)].add(s.series_id)
    issues = []
    for (driver_id, year), series_ids in series_by_driver_year.items():
        if len(series_ids) > 1:
            issues.append(Issue(file="standings.csv", line=None, message=f"{driver_id} {year} multiple series: {sorted(series_ids)}", severity="warning"))
    return issues

def check_end_date_year(seasons) -> list[Issue]:
    issues = []
    for s in seasons:
        if s.season != s.end_date.year:
            issues.append(Issue(file="seasons.csv", line=None, message=f"{s.series_id} {s.season} end date year is: {s.end_date.year}", severity="warning"))
            continue
    return issues

def check_scale_order(scales) -> list[Issue]:
    issues = []
    for s in scales:
        for n, n1 in zip(s.points, s.points[1:]):
            if n1 > n:
                issues.append(Issue(file="scales.csv", line=None, message=f"{s.series_id} {s.regulation_year} scale order is wrong: {n, n1}"))
                continue
    return issues

def validate_all(drivers, standings, seasons, scales) -> list[Issue]:
    return (check_unknown_drivers(standings, drivers)
            + check_positions(standings)
            + check_scales_exist(standings, seasons, scales)
            + check_duplicate_drivers(standings)
            + check_two_series_per_year(standings, seasons)
            + check_end_date_year(seasons)
            + check_scale_order(scales))