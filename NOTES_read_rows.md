# Notes: review + next steps for Step 5a (2026-11-09)

Pick-up notes from a review session. Code here is skeletons only: the logic is still to be written.
Delete this file once the items are done and `PROTOTYPE_PLAN.md` is updated.

## Review findings (still open)

Bugs:

- [ ] `load_seasons`: multiplier `0` still loads (`< 0` should be `<= 0`; the plan says `0 < multiplier <= 1`).
- [ ] `load_seasons`: the message says "multiplier is negative" for `1.5` too. Use something like
  "multiplier must be between 0 (exclusive) and 1".
- [ ] A value of just a space (e.g. `multiplier_reason` = `" "`) counts as present, because
  `empty_required` strips values only to check them. The "strip values in the shared helper" item fixes this.
- [ ] `load_scales`: negative points still load with no issue.

Tests (main weakness):

- [ ] The `*_negative` tests only assert `len(...) == 1` and print. Almost every broken row fails
  with `empty: X`, so the new checks (series, multiplier range, multiplier reason) aren't tested.
  - Assert lines: `assert [i.line for i in issues] == [3, 4, ...]`
  - Assert part of the message too, e.g. `assert "series" in issues[0].message`
- [ ] Add broken rows that each break exactly one thing:
  - seasons: `F2`, multiplier `0`, `1.5` and `NaN`, `0.9` with no reason, an unknown status
  - standings: unknown series, negative points, an unknown status
  - scales: unknown series, a negative point value, a non-number like `x`
  - drivers: an empty nationality that **should load**
- [ ] `seasons_broken.csv` line 6 has 7 fields instead of 8 (no trailing comma). Check whether that's intended.
- [ ] `test_scale_class`: don't use `scales[14]` / `scales[19]`; find rows by `(regulation_year, series_id)`
  and assert exact tuples, e.g. Super Formula 2025 = `(30, 25, 20, 15, 12, 9, 7, 5, 3, 2)`.

Smaller things:

- [ ] `check_series_id` can be `return series_id in SERIES`, taking the string, with `-> bool`.
- [ ] `scales.csv` and `seasons.csv` lost their final newline (the only change in them). Restore with
  `git checkout -- super-licence/data/scales.csv super-licence/data/seasons.csv`.
- [ ] `PROTOTYPE_PLAN.md` is out of date: it says 6 tests (now 9), and these are done but not ticked:
  `utf-8-sig`, `blank_to_none` on `multiplier_reason`, the `NaN`/`Infinity` check, nationality optional,
  the series check, the confirmed-without-a-second-source check, the series_points message.

Suggested order: fix the `0` multiplier, add fixture rows and strict asserts for the existing checks,
then finish `read_rows` (below), update the plan, commit.

## 1. New `read_rows`

Order of checks matters, because each step relies on the previous one:

1. **Is there a header?** For a 0-byte file `reader.fieldnames` is `None`, and `len()`/`set()` on it
   crash, so check this first.
2. **Do the columns match?** Only now is it safe to look at the names.
3. **Read the rows.**
4. **Were there any rows?** Only knowable after step 3. (The old `len(reader.fieldnames) < 1` check
   ran before anything was read, so it couldn't work.)

```python
def read_rows(path: Path, expected: set[str]) -> tuple[list[tuple[int, dict[str, str]]], list[Issue]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            ...  # TODO: return no rows and one Issue on line 1 ("file is empty")

        # TODO: compare set(reader.fieldnames) with expected.
        #   If they differ, return no rows and an Issue on line 1.
        #   Bonus: say which columns are missing / unexpected, e.g. expected - set(...)

        rows = [(reader.line_num, row) for row in reader]

    # TODO: if there are no rows -> return [] and an Issue ("no data rows")
    return rows, []
```

Why:

- **Return `[], [issue]` straight away for header problems.** If the columns are wrong every row
  fails anyway; one clear issue on line 1 beats 30 confusing ones.
- **Accessing `reader.fieldnames` reads the header line**, which is why it's only `None` for an empty file.
- **`reader.line_num` is read just after each row is read**, so it's that row's real line in the
  file, even after blank lines. For a quoted field spanning several lines it gives the row's last line. Good enough.
- **Set subtraction gives useful messages:** `expected - set(reader.fieldnames)` = missing columns,
  `set(reader.fieldnames) - expected` = extra ones. "missing: multiplier_reason" beats "field names mismatch".
- **Use a set, not a length check plus a loop.** `set(...) != expected` replaces both. (The old
  length + membership check passes `a,a,b` against `{a, b, c}`, then crashes later with `KeyError`.)
  To also catch a duplicated header, add `len(reader.fieldnames) != len(expected)`.
- Keep the return a tuple everywhere (the old draft mixed `[[], issues]` and `rows, issues`), and drop the `print`.

### Wiring it into the loaders

Expected columns as constants at the top of `load.py`, next to `SERIES`:

```python
DRIVER_COLUMNS = {"driver_id", "display_name", "nationality", "notes"}
# STANDING_COLUMNS = ..., SEASON_COLUMNS = ..., SCALE_COLUMNS = ...
```

The start of every loader then changes the same way:

```python
rows, issues = read_rows(path, DRIVER_COLUMNS)   # issues now starts with the file-level ones
for line, row in rows:                           # no more enumerate(start=2)
    ...
```

`issues = []` goes away, because `read_rows` gives you the starting list.

`test_read_drivers` will break, because `read_rows` now returns `(line, row)` pairs. Update it, and
assert `rows[0][0] == 2` while you're there.

### Tests to write

Each case needs its own fixture file, because these are whole-file problems:

| Fixture | Expected |
| --- | --- |
| 0-byte file | 0 rows, 1 issue on line 1 |
| header only | 0 rows, 1 issue |
| a column renamed (e.g. `nation`) | 0 rows, 1 issue on line 1, `"nation"` or `"nationality"` in the message |
| a blank line between rows 1 and 2 | the second driver's issue is on **line 4**, not 3 (the bug `line_num` fixes) |
| saved from Excel as "CSV UTF-8" | loads like the normal file (tests the BOM fix) |

## 2. The `p1`–`p10` line in `load_scales`

Build the column names from the pattern instead of typing them out (a typo like `p9, p9` would never be noticed):

```python
POINT_COLUMNS = [f"p{i}" for i in range(1, 11)]   # ["p1", ..., "p10"]
```

Inside the `try`:

```python
points = tuple(int(row[col]) for col in POINT_COLUMNS)
```

Why:

- **`int(...) for col in ...` is a generator.** `tuple()` uses it up straight away, so a bad value
  like `x` still raises `ValueError` *inside* the `try`, and the existing `except` catches it.
- **Reuse `POINT_COLUMNS` in `SCALE_COLUMNS`**, e.g.
  `SCALE_COLUMNS = {"regulation_year", "series_id", *POINT_COLUMNS, "page", "row_label", "notes"}`,
  so the column list exists in one place only.
- **The negative-points check becomes a one-liner**, e.g. with `any(...)` over `points`.
- **Drop `InvalidOperation` from that `except`.** Nothing in `load_scales` uses `Decimal` (a cleanup item in the plan).
