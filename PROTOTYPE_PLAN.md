# Prototype Plan: Super Licence Points Calculator

**Goal:** for 5–10 single-seater series, calculate each driver's unofficial
Super Licence total for a given application year, with an explanation, from
hand-entered data.

## Progress

| Step | Status |
| ---- | ------ |
| 0. Housekeeping | Done (2026-11-06) |
| 1. Fix the scope | Done (2026-11-06) |
| 2. Design data files | Done (2026-11-06) |
| 3. Rule data | Done for all 5 series, 2022–2026 (FRECA 2023/2025 fixed 2026-11-07). |
| 4. Standings | Enough for the pilot: F2 2023–2025 (two sources each). More later, before Step 8. |
| 5. Loading + validation | In progress: all 4 loaders work on the real data. Their fixes, cleanup and tests are still open, and the cross-file checks (5b) haven't started. |
| 6–9 | Not started |

Last updated: 2026-11-08. Next: work through the "Open before moving on" list in
Step 5a, then the cross-file checks (Step 5b).

---

## Step 0: Housekeeping (about 30 min)

- [x] `git init`, `.gitignore`, first commit pushed to GitHub (PDFs ignored).
- [x] Fix `meta.json`: ISO dates, category/662 source URL, `file_url`,
  `archive_url`, `filename`, `sha256` added.
- [x] Python environment with pytest (for `super-licence/`): uv project,
  Python >= 3.14, pytest as a dev dependency. Run `uv run pytest` from `super-licence/`.
- [ ] ~~Optional: add a `notes` field to 2024 `meta.json` marking it as the redline version.~~ Skipped.
- [x] Optional: confirm the 2026 `archive_url` (captured 2026-10-05) has the same hash. Matches.
- [x] Back up the PDFs outside the repo.
- **Done when:** `pytest` runs, even with no tests yet.

## Step 1: Fix the scope

**Decided 2026-11-06.**

- **Series:** FIA Formula 2, FIA Formula 3, Formula Regional European
  Championship (FRECA), IndyCar, Super Formula.
- **Application years:** 2026 and 2027.
  - 2026: window (i) 2023–2025, window (ii) 2024–2026.
  - 2027: window (i) 2024–2026, window (ii) 2025–2027 (2027 has no results yet).
  - So results from **2023–2026** are needed, scored with the 2023–2026 Appendix L documents.
  - The historical best-of-N rule (windows with 2020/2021) never applies, so it is not built.
- **Excluded from the prototype** (totals may differ from published ones; note
  differences, don't fix them):
  - Penalty-free bonus (+2). Expect frequent 2-point gaps for F2/F3 drivers.
  - Free practice points.
  - FIA World Cup bonuses.
  - Two-championships-per-year rule (validation flags drivers in two series in one year for a manual check).
  - Field-size reduction (season multiplier stays 1.0 unless set by hand).
  - 80% rule and all other eligibility conditions (they don't affect points).
- **Done when:** the scope is written in CLAUDE.md or a README. Done (written here).

## Step 2: Design the data files before entering anything

Decide the columns. At minimum:

- **drivers:** a stable ID you assign, plus a display name. Don't use the
  name as the key.
- **scales:** series, regulation year, position, points, plus a reference
  to the document and page.
- **seasons:** series, season, end date, multiplier (default 1.0),
  status (complete or in progress), notes.
- **standings:** series, season, driver ID, position, source URL,
  fetch date, status.

- **Done when:** you have headers and 2–3 sample rows per file, and you're happy with them.

**Decided 2026-11-06.** Files live in `super-licence/data/`, UTF-8.

| File | Columns |
| ---- | ------- |
| `drivers.csv` | `driver_id,display_name,nationality,notes` |
| `scales.csv` | `regulation_year,series_id,p1,…,p10,page,row_label,notes` |
| `seasons.csv` | `series_id,season,end_date,status,multiplier,multiplier_reason,source_url,notes` |
| `standings.csv` | `series_id,season,driver_id,position,series_points,source_url,fetch_date,second_source_url,status,notes` |

Conventions:

- **`series_id`** fixed list: `f2`, `f3`, `freca`, `indycar`, `super-formula`.
- **`driver_id`** is a slug assigned once and never changed (display name can change).
  Same-name different drivers get `-2`. Never merge on name similarity.
  Nationality: FIA three-letter codes, optional.
- **`scales.csv` is wide** (one row per series and year, like the PDF table), positions
  11+ score 0. `regulation_year` = the `rules/appendix-l/<year>/` folder; `page` and
  `row_label` (copied exactly as printed, including FIA typos like "Japonese") point to the line in the PDF.
- **`seasons.csv`:** `end_date` decides the regulation year and window year.
  `status` is `completed` or `in_progress`. Prefer a final-round result or final
  classification over a pre-season calendar as the source.
- **`standings.csv`:** key is `series_id + season + driver_id`. `series_points` is the
  championship's own points (decimal, e.g. 214.5 for half points), used only for
  validation. **Super Licence points are never stored**, always calculated.
  `status`: `confirmed` (season completed and two sources agree), `provisional`
  (in progress or one source), `manual`. Ties: enter the official position, note "countback".
  Official series standings in `source_url`, second source (e.g. Wikipedia) in
  `second_source_url`. Snapshot: put a web.archive.org link in `notes`.
- **Every row has exactly as many fields as the header** (empty trailing fields
  still need their comma). First thing validation should check.
- Top 10 per season is enough; enter a few more for in-progress 2026 seasons.
- If editing in Excel, save as "CSV UTF-8".

## Step 3: Enter the rule data

- For each series and each regulation year from 2023 to 2026, enter the
  scale from the PDF.
- Known changes in this range:
  - Super Formula: new scale from 2025 (30-25-20-15-12-9-7-5-3-2)
  - IndyCar: new scale in 2026 (40-30-25-20-15-10-8-6-3-1)
  - DTM: 6-4-2 from 2025 (out of scope, but noted)
- **Done when:** every in-scope series has a scale for every year, and each
  one is checked against the PDF by hand.

**Status 2026-11-06:** all 5 series entered for 2022–2026 (2022 is outside scope, harmless).

To fix:

- [x] **FRECA 2023 was wrong:** entered `30,25,20,10,8,6,4,3,2,1`, which is the Formula E
  row directly above it on page 66. Correct: `25,20,15,10,7,5,3,2,1,0` (checked
  against the PDF text 2026-11-06).
- [x] Rows with an empty `notes` have 16 fields (`,,` at the end); should be 15 (one trailing comma).
- [x] Optional: IndyCar 2026 `notes` is missing the final period that the other years have.
- [x] FRECA 2025 had the same Formula E copy error; fixed to `25,20,15,10,7,5,3,2,1,0` (2026-11-07).
- Idea for Step 5: warn when a series' scale changes between years without a note.

## Step 4: Enter standings

- Enter the top 10 (or the full standings) for each series and season from
  2023 to 2026, with a source URL for each.
- Some 2026 seasons haven't finished (F2 and F3 run until December), so mark
  them **in progress**.
- Ideally, check each season against a second source.
- **Done when:** every row has a source and the final positions are correct.

**Status 2026-11-06:** `seasons.csv` has all 5 series for 2022–2026 (F2 2026 and
Super Formula 2026 `in_progress`). `standings.csv` has F2 2024 and 2025 (top 10);
`drivers.csv` has those 17 drivers.

To fix:

- [x] `fetch_date` is `2026-06-11` on all rows, should be `2026-11-06` (ISO is yyyy-mm-dd).
- [x] "Richard Vershoor" → **Richard Verschoor**: fix `driver_id` (`richard-verschoor`),
  `display_name`, and his two standings rows.
- [x] `seasons.csv`: F3 2026 `end_date` is `2023-09-13`, should be 2026.
- [x] `seasons.csv`: rows have 9 fields, should be 8 (one trailing comma, not two).
- [x] `drivers.csv`: rows have 3 fields, add the trailing comma for `notes`.
- [x] Standings currently use Wikipedia as `source_url` with no second source but are
  marked `confirmed`. Move Wikipedia to `second_source_url`, add the official
  standings as `source_url`, or mark `provisional` until then.
- [ ] Optional: many `seasons.csv` sources are pre-season calendars; replace with
  final-round results where easy.

**Status 2026-11-07:** F2 2023–2025 entered (top 10, Wikipedia + Motorsport.com, `confirmed`),
24 drivers. Decided this is enough to build Steps 5–7; engine edge cases (scale changes,
multipliers, window (ii)) are tested with fixtures, not real data.

Remaining entry (before Step 8): F3 and FRECA 2023–2025 (needed for most published
totals), then IndyCar, Super Formula and 2026 standings.

## Step 5: Loading and validation checks

**Set up 2026-11-07.** `src/` layout, installed by `uv sync` (`uv_build` backend), tests in
`tests/`, run with `uv run pytest`.

```text
src/super_licence/
├── models.py   ← frozen dataclasses: Driver, Issue, Standing, Season, Scale
├── load.py     ← read_rows, blank_to_none, empty_required, one loader per file
└── validate.py ← later: cross-row / cross-file checks
tests/
├── test_load.py
└── fixtures/drivers_broken.csv   ← deliberately broken data lives here, never in data/
```

**5a. Loaders** (one per file). Pattern: `load_x(path) -> (list[X], list[Issue])`. Per row:
short row (`None in row.values()`) → issue + `continue`; empty required field → issue +
`continue`; optional fields via `blank_to_none`; line number = `enumerate(..., start=2)`.
A broken row is reported and skipped, never half-loaded. Tests assert exact counts and
issue line numbers, not just "some issues".

- [x] `load_drivers` + tests (real file: 24 drivers, no issues; broken fixture: 1 driver, issues on lines 3 and 4)
- [x] `load_standings`: bad rows checked by hand, positive test only (real file: 30 rows, no issues)
- [x] `load_seasons`: works on the real file (25 rows, no issues); see open list below
- [x] `load_scales`: `p1`–`p10` gathered into a tuple; works on the real file (25 rows, no issues); see open list below

Decided 2026-11-07: `Decimal` for `multiplier` and `series_points` (totals are compared
against a hard 40-point threshold, and floats can drift), `date` for dates, tuple for scale
points (a dict inside a frozen dataclass can still be changed).

**Open before moving on** (status 2026-11-08; `uv run pytest` passes 6 tests, but two of them only print).
Loader behaviour below was checked by running broken rows through each loader.

Bugs:

- [ ] `load_seasons`: `multiplier_reason` isn't wrapped in `blank_to_none`, so empty gives `''` instead of `None`.
- [ ] `load_seasons`: `multiplier` of `NaN` crashes the loader (`InvalidOperation` on the `<`
  comparison, outside the `try`). Check `is_finite()` first.
- [ ] `load_seasons`: `multiplier` of `10` and `0` load with no issue. Planned check: `0 < multiplier <= 1`.
- [ ] `load_scales`: negative points load with no issue.
- [ ] `load_drivers`: `nationality` is now required (`optional={"notes"}`), but Step 2 says it's
  optional. Decide which one is right, then fix the code or the convention.

Cleanup:

- [ ] Remove the leftover `Scale` docstring between `load_seasons` and `load_scales` in `load.py`.
- [ ] `load_standings`: the "series_points is not finite" message also fires for negative values.
- [ ] `load_scales`: `except` doesn't need `InvalidOperation` (no `Decimal` there); build `points`
  with a generator instead of listing `p1`–`p10`.
- [ ] Move the repeated row-length and empty-field checks into a helper.
- [ ] Optional: a bad `Decimal` gives the unhelpful message `[<class 'decimal.ConversionSyntax'>]`.

Tests:

- [ ] `test_season_class` and `test_scale_class` only print. Add `issues == []`, row counts and a
  full first-row comparison.
- [ ] Scales: assert Super Formula `points` differ between 2024 and 2025.
- [ ] Standings: find the 214.5 row by driver and season, not `standings[10]`.
- [ ] Add broken fixtures with exact line numbers: `standings_broken.csv`, `seasons_broken.csv`,
  `scales_broken.csv`. Each bug above gets a row, and `drivers_broken.csv` gets a row with too many fields.

**5b. Checks across rows and files** (`validate.py`), on the loaded records:

- duplicate or missing positions, and position gaps
- driver IDs not in `drivers`
- series and season combinations with no scale for that year
- a driver appearing in more than one championship in a year. That needs a
  manual check for the two-championship rule, which the prototype won't calculate.

- **Done when:** clean data passes, and data you've broken on purpose fails.

## Step 6: Rules engine

Pure functions, no file reading inside them:

1. **Season points:** points for one standing row = scale value for that
   position × multiplier. Return the number and how it was calculated.
2. **Year points:** a driver's total for one calendar year.
3. **Qualifying points:** for an application year Y, calculate window (i),
   Y-3 to Y-1, and window (ii), Y-2 to Y. Return the higher one, both window
   totals, and which window was used.

- **Done when:** every output includes an explanation, not only a number.

## Step 7: Tests

Work out each expected answer by hand before writing the test:

- position 1, position 10, position 11+ (0 points)
- the same position in Super Formula 2024 and 2025 gives different points
- window (i) higher, window (ii) higher, and both equal
- a multiplier below 1.0
- a driver with no results

- **Done when:** all tests pass, and every expected value came from your own
  calculation, not the code.

## Step 8: Check against real drivers

- Choose 3–5 drivers with known totals, published by the media or a tracker site.
- Calculate them by hand, then with the engine. Any difference must be explained.
- Expect gaps of exactly 2 points from the penalty-free bonus you excluded.
  Note those rather than fixing them.
- **Done when:** every difference is explained.

## Step 9: Output

- A script that prints a leaderboard for an application year, with a
  per-driver breakdown. Optionally, dump the same data as JSON.
- Label totals as unofficial and say that bonuses are excluded.
- **Done when:** you can run one command and see who's above 40 for 2027 and why.

---

**Rough order of effort:** steps 3–4 (data entry) and step 8 (checking
against real drivers) take the most time. The engine itself is small.

## Deferred to later phases

- Penalty-free bonus (+2): needs penalty-point data from stewards' decisions
  (planned FIA documents fetcher for F2/F3, manual entry elsewhere).
- Field-size reduction: needs starters in the first race of each event;
  use the manual season multiplier until then.
- Free practice points: FastF1 laps × per-event circuit length; mark
  borderline cases provisional; licence type and penalty points not in FastF1.
- 80% rule: treated as events, not races (secondary source, provisional).
  Appendix L does not define it.
- Two-championships-per-year rule, World Cup bonuses, karting, shared cars,
  F4 eligibility, rounding and ties (not defined in Appendix L).
