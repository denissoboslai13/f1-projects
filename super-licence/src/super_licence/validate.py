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
    ...  # TODO: no season row -> error; season row but no scale for end_date.year -> error

def check_two_series_per_year(standings, seasons) -> list[Issue]: ...   # warning
def check_end_date_year(seasons) -> list[Issue]: ...                    # warning
def check_scale_order(scales) -> list[Issue]: ...                       # error

def validate_all(drivers, standings, seasons, scales) -> list[Issue]:
    return (check_unknown_drivers(standings, drivers)
            + check_positions(standings)
            + ...)