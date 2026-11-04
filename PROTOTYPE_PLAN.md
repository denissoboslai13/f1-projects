# Prototype Plan: Super Licence Points Calculator

**Goal:** for 5–10 single-seater series, calculate each driver's unofficial
Super Licence total for a given application year, with an explanation, from
hand-entered data.

---

## Step 0: Housekeeping (about 30 min)

- `git init`, a `.gitignore`, and a Python environment with pytest.
- Fix `meta.json`:
  - 2023 publication date should be 2023-12-06 (per PDF footer, not 19-10-23)
  - decide the source URL (category/116 or category/662)
  - switch to ISO dates (YYYY-MM-DD)
- **Done when:** the repo has a first commit and `pytest` runs, even with no tests yet.

## Step 1: Fix the scope

- Choose the series, for example F2, F3, FRECA, IndyCar, Super Formula,
  plus a few optional ones.
- Choose the application years to support. 2026 and 2027 are reasonable,
  which means 2023–2026 results are needed.
- Write down what's excluded: bonuses (penalty-free, free practice,
  World Cups), field-size logic, the 80% rule, other eligibility conditions.
- **Done when:** the scope is written in CLAUDE.md or a README.

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

## Step 3: Enter the rule data

- For each series and each regulation year from 2023 to 2026, enter the
  scale from the PDF.
- Known changes in this range:
  - Super Formula: new scale from 2025 (30-25-20-15-12-9-7-5-3-2)
  - IndyCar: new scale in 2026 (40-30-25-20-15-10-8-6-3-1)
  - DTM: 6-4-2 from 2025 (out of scope, but noted)
- **Done when:** every in-scope series has a scale for every year, and each
  one is checked against the PDF by hand.

## Step 4: Enter standings

- Enter the top 10 (or the full standings) for each series and season from
  2023 to 2026, with a source URL for each.
- Some 2026 seasons haven't finished (F2 and F3 run until December), so mark
  them **in progress**.
- Ideally, check each season against a second source.
- **Done when:** every row has a source and the final positions are correct.

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
