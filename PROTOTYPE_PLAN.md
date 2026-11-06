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
| 3. Rule data | Entered for all 5 series, 2022–2026. One known error to fix (see Step 3). |
| 4. Standings | In progress: F2 2024 and 2025 entered. Seasons file complete for 2022–2026. |
| 5–9 | Not started |

Last updated: 2026-11-06. Next: work through the "To fix" lists in Steps 3 and 4,
then continue entering standings (F2 2023 and 2026, then the other series).

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

- [ ] **FRECA 2023 is wrong:** entered `30,25,20,10,8,6,4,3,2,1`, which is the Formula E
  row directly above it on page 66. Correct: `25,20,15,10,7,5,3,2,1,0` (checked
  against the PDF text 2026-11-06).
- [ ] Rows with an empty `notes` have 16 fields (`,,` at the end); should be 15 (one trailing comma).
- [ ] Optional: IndyCar 2026 `notes` is missing the final period that the other years have.
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

- [ ] `fetch_date` is `2026-06-11` on all rows, should be `2026-11-06` (ISO is yyyy-mm-dd).
- [ ] "Richard Vershoor" → **Richard Verschoor**: fix `driver_id` (`richard-verschoor`),
  `display_name`, and his two standings rows.
- [ ] `seasons.csv`: F3 2026 `end_date` is `2023-09-13`, should be 2026.
- [ ] `seasons.csv`: rows have 9 fields, should be 8 (one trailing comma, not two).
- [ ] `drivers.csv`: rows have 3 fields, add the trailing comma for `notes`.
- [ ] Standings currently use Wikipedia as `source_url` with no second source but are
  marked `confirmed`. Move Wikipedia to `second_source_url`, add the official
  standings as `source_url`, or mark `provisional` until then.
- [ ] Optional: many `seasons.csv` sources are pre-season calendars; replace with
  final-round results where easy.

Remaining entry: F2 2023 and 2026, then F3, FRECA, IndyCar, Super Formula for 2023–2026.

## Step 5: Validation checks

A script that stops and lists problems:

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
