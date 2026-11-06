# F1 Super Licence Tracker

## Project summary

Build a readable, source-backed tracker for FIA Super Licence eligibility points. It should cover every driver with points across eligible championships and explain how each total was calculated.

This is the first project in a personal motorsport section at `myname.dev/f1` (domain name is a placeholder). The second planned project is a stewards' decisions analyzer that reuses the same driver database.

Existing sites are hard to read. This project competes on clarity, traceability, and coverage.

**Status (2026-11-06):** Phase 0 partly done. Appendix L 2022–2026 archived and verified against the rule summary. Monorepo created and pushed. Prototype Steps 0–2 done: uv + pytest set up in `super-licence/`; scope fixed (5 series, application years 2026–2027, bonuses excluded); CSV format decided (`super-licence/data/`, conventions in `PROTOTYPE_PLAN.md` Step 2). Steps 3–4 in progress: scales and seasons entered for all 5 series, standings for F2 2024–2025. No code yet. Next: the "To fix" lists in `PROTOTYPE_PLAN.md` Steps 3–4 (incl. a wrong FRECA 2023 scale), then more standings.

## Repository layout

One repo (`f1`) for both projects, because they share driver identities, event data, source storage, and deployment. Split later only if needed.

```text
f1/
├── CLAUDE.md
├── PROTOTYPE_PLAN.md          ← step-by-step prototype plan, read this to continue
├── .gitignore
├── super-licence/
│   ├── pyproject.toml, uv.lock             ← uv project (Python >= 3.14, pytest dev dep)
│   ├── data/                               ← drivers, scales, seasons, standings CSVs
│   └── rules/appendix-l/<year>/meta.json   (+ PDF, not committed)
└── stewards/                  ← later
```

- Do not create a `shared/` folder up front. Extract shared code when the stewards project actually needs it.
- Folder names match the planned URLs (`f1/super-licence`, `f1/stewards`).

## Working with me

- I'm comfortable with Python, React, TypeScript, and Node/Express, and I'm aiming toward backend and systems work.
- Explain the why behind important technical decisions, not only what changed.
- Prefer simple, understandable solutions over heavy infrastructure.
- Do not invent rules, standings, or data sources. Mark uncertainty clearly.
- Before scraping a site, check its terms and robots rules. Use a low request rate.
- Keep rule data separate from application logic.
- I would like to write a majority of the code myself, also choose the technologies myself, but might need help with basic setup of environments or things like that, dont overwrite clean up or write logic without me asking for it.

## Core principles

1. **Rules are versioned data.** A result uses the regulations applicable to the year it was achieved. Never hardcode one current points table.
2. **Every number is traceable.** Store its source URL, fetch time, and raw source snapshot.
3. **Separate points from eligibility.** Reaching 40 points does not by itself make a driver eligible.
4. **Label confidence.** Use states such as confirmed, provisional, incomplete, and manual.
5. **Keep history.** Corrections create new records or revisions. Do not silently overwrite past data.
6. **Validate before publishing.** Suspicious data should stop and alert, not reach the site.
7. **Totals are unofficial.** Calculated totals must be labelled as unofficial and not FIA-issued.

## Primary rule source

Use the latest applicable FIA International Sporting Code Appendix L as the authority:
https://www.fia.com/regulation/category/662

The regulations page lists the 2026 version as published on 23 June 2026. Treat Wikipedia and media articles as secondary references only.

**Verification status:** the rule summary below was checked against the official Appendix L PDFs for 2022–2026 (Article 13 and Supplement 1) on 2026-11-04. Article numbers refer to 2026 unless stated. Items marked *not in Appendix L* come from secondary sources or are undefined, so treat them as provisional.

### Archived rule documents

Stored in `super-licence/rules/appendix-l/<year>/`. Each folder has the PDF and a `meta.json`:

```json
{
  "year": 2024,
  "publication_date": "2024-12-11",
  "source_url": "https://www.fia.com/regulation/category/662",
  "file_url": "<direct PDF link>",
  "archive_url": "<web.archive.org capture of file_url>",
  "filename": "<pdf filename>",
  "sha256": "<lowercase sha256 of the PDF>",
  "fetch_date": "2026-11-04"
}
```

- PDFs are FIA copyright and are **not committed** (`**/rules/**/*.pdf` in `.gitignore`). Only `meta.json` is public, and anyone can verify a downloaded copy with the hash. Keep the PDFs backed up outside the repo.
- A reissued document with a different hash is a **new record**, not a replacement.
- Documents are bilingual (French/English side by side). Text extraction mixes the columns, so check rendered pages for anything subtle.
- **The 2024 PDF is a redline** (pink = added, strikethrough = removed). Plain text extraction merges old and new text (e.g. "13.1.32", "53 points"). Read it visually.
- Known drafting error: 13.1.3 a) in 2025 and 2026 still refers to "13.1.6 c)", which was renumbered to 13.1.5 c).

Monitor the FIA Appendix L page for changes and alert me when it changes. Compare file hashes to detect reissues.

## Rule summary (verified against Appendix L 2022–2026)

Applicability (Supplement 1 notes i and ii, all years): each year's table applies to championships **completed** in that year, and points use the regulatory text of the year in which the **final championship result** was achieved. So a result keeps the scale of its own year.

### Main qualification

For an application year `Y`, the qualifying total is the higher of:

- points from `Y-3`, `Y-2`, and `Y-1`
- points from `Y-2`, `Y-1`, and championships contested during `Y`

Baseline logic:

```python
def qualifying_points(driver, year):
    previous_three = points(driver, year - 3, year - 1)
    current_window = points(driver, year - 2, year)
    return max(previous_three, current_window)
```

Article 13.1.5 a) (13.1.6 a) in 2022–2023). Normal full Super Licence threshold: 40 points.

Historical best-of-N rule (only needed for applications up to 2024):

| Document | Rule |
| -------- | ---- |
| 2022, 2023 | If a window includes **2020 or 2021**: window (i) becomes the best 3 of the previous 4 years, and window (ii) becomes the best 2 of the previous 3 years plus the current year. |
| 2024 | Only window (i), only for **2021**: best 3 of the previous 4 years. |
| 2025 onward | Removed. |

### Championship points

- Points are based on final championship position (top 10 only).
- Each year's document has **one** scale per row. There are no "old scale" rows in 2022–2026. Older results use the document from their own year.

Scale changes for the first-batch series, 2022–2026:

| Series | Scale |
| ------ | ----- |
| F2 | 40-40-40-30-20-10-8-6-4-3, all years |
| F3 | 30-25-20-15-12-9-7-5-3-2, all years |
| FRECA | 25-20-15-10-7-5-3-2-1-0, all years |
| Super Formula | 25-20-15-10-7-5-3-2-1-0 until 2024; **30-25-20-15-12-9-7-5-3-2 from 2025** |
| IndyCar | 40-30-20-10-8-6-4-3-2-1 until 2025; **40-30-25-20-15-10-8-6-3-1 in 2026** |
| DTM (later) | 15-12-10-7-5-3-2-1-0-0 until 2024; **6-4-2 from 2025** |

### Calendar and field conditions (Supplement 1)

- At least **5 competitions**, with at least **72 hours** between the end of one competition and the start of the next.
- At least **3 tracks**. An FIA-licensed alternative layout may count as a separate track.
- Regularly sanctioned by its ASN, held on FIA-homologated tracks.
- Karting is exempt from the first two criteria.
- If fewer than 16 drivers start the **first race of a competition**, all of that championship's points are reduced by 10% per missing driver. If this happens at several competitions, the one with the fewest starters decides.
- Temporary exception: championships ending in 2022 and no later than 31.03.2023 needed only 3 competitions, 2 tracks, and 10 starters for full points.
- Rows marked `*` (IndyCar, Indy NXT, USF Pro 2000, NASCAR, IMSA, Supercars): "subject to all (road course) rounds being held on FIA homologated tracks".
- F4 South East Asia 2023: 50% of points, with 3 events on 2 layouts. From the 2024 document also: F4 India 2023 at 100%, with 4 events on 2 layouts.
- F4 age rule: a driver racing in certified F4 under 15 scores no points that year or the next 2.
- Rows marked `**` in 2026 (FR Middle East and Oceania Trophies, F4 Middle East Trophy) are exempt from the 5-competition minimum.

### Combining championships

- At most two championships can count from one calendar year.
- The second championship must start after the first ends.
- *Not in Appendix L:* how the best valid combination is selected.

### Bonus points

- **Free practice:** only for **Free Practice Only Super Licence** holders. 1 point per F1 event with at least 100 km in a free practice session, only if no penalty points were imposed, maximum 10 in total.
  - 2022–2024: counted in the calendar year of the session, so they expire with the window.
  - 2025 onward: "independent of the calendar year", so they effectively do not expire.
- **Penalty-free season:** +2 for completing the whole championship without penalty points, only in "FIA Championships where a penalty points system is in place". *Not in Appendix L:* which championships those are. F2 and F3 clearly; FRECA and F4 to confirm; IndyCar and Super Formula do not apply.
- **World Cup winners.** Appendix L does not mention Macau; the bonuses are tied to the FIA World Cup titles:
  - 2022–2023: FIA F3 World Cup winner +5.
  - 2024: FIA Formula Regional World Cup winner +3. The F3 World Cup bonus was removed.
  - 2025 onward: FR World Cup winner +3, FIA F4 World Cup winner +2.

### Karting

- FIA karting points are capped at 12 total.
- Karting points are valid for five years.
- Keep karting logic separate from the normal window logic.

### Shared cars

When multiple drivers complete a season in the same car:

| FIA categorisation | Share of points |
| ------------------ | --------------: |
| Platinum or Gold   |            100% |
| Silver             |             75% |
| Bronze             |             50% |
| No categorisation  |              0% |

Since 2023, the FIA may calculate a categorisation for a driver who did not have one. *Not in Appendix L:* rounding.

### Other eligibility conditions

Show these separately from the points total:

- Grade A licence
- age 18, with FIA discretion to grant at 17 (discretion added in 2024)
- driving licence requirement (removed in 2024)
- theory test
- 80% of each of two full seasons in Supplement 1 single-seater championships for first-time applicants. *Not in Appendix L:* whether this means events or races. Working assumption from a secondary source: **events** (a driver who crashes in practice and misses the race still counts as having competed). Provisional.
- previous licence holder routes, including 13.1.5 b): a former full Super Licence holder with 100 km in an F1 free practice session in the previous 3 years
- FIA discretion and force-majeure routes, including the 30-point route
- free-practice-only licence route, including the 25-point route

Do not attempt to calculate FIA discretionary decisions. Show them as statuses or notes.

## Scope

### Initial scope

Single-seater championships first. Build this first batch before expanding:

1. FIA Formula 2
2. FIA Formula 3
3. Formula Regional European Championship
4. IndyCar
5. Super Formula

### Expansion order

1. Formula E, Indy NXT, Super Formula Lights, Euroformula Open, GB3, Eurocup-3, F1 Academy, USF Pro 2000, Formula Regional series
2. FIA-certified F4 championships
3. Karting
4. GT, endurance, stock cars, and other categories, including shared-car handling

Rows in the FIA table are not always one championship. For example, the F4 row covered many series until 2025 (2026 lists them individually), and the LMP2 row combines several series. Scale changes are handled by the year of the document, not by separate rows.

## Data to collect

### Final standings

- championship and season
- driver
- position and championship points
- source and status

### Race entries

- driver
- championship, season, event, and race
- started
- classified
- finishing position

Race entries support the field-size and 80% rules. They also support part of the penalty-free rule.

### Season data

- start and end dates
- completed events
- circuits and layouts
- eligibility flag
- points multiplier
- homologation or exception notes
- source

Calculate calendar checks from completed event data where possible.

### Extra data

- free practice sessions and distance
- penalty records
- FIA World Cup winners (F3 / Formula Regional / F4, depending on year)
- karting results
- crew lists
- FIA driver categorisations

Free practice distance and penalty-free data are likely hard. Find sources before assuming automation. Race results do not show licence penalty points.

Planned approaches (not yet verified):

- **Free practice distance:** FastF1 laps per session × circuit length. Store circuit length **per event**, because layouts change (e.g. Melbourne 2022, Barcelona 2023, Abu Dhabi 2021). Laps × length is an estimate because in- and out-laps are partial, so mark results within about one lap of 100 km as provisional. FastF1 does not show licence type or penalty points. Check FastF1 / F1 live timing terms and use its cache.
- **Penalty points:** come from stewards' decision documents, not results. Plan a small FIA documents fetcher **inside the tracker** (Phase 2) for F2 and F3 decisions, extracting penalty points with simple pattern matching (check real PDFs first). The stewards analyzer reuses it later. Other series: manual entry or "unverified".
- **Field size:** only the number of starters in the first race of each competition is needed. Use a manual season multiplier until automated; validation should flag any competition with fewer than 16 starters.
- **Scaling to many series:** data volume is small; the cost is maintaining one adapter per source website. Automate the important series, enter the long tail by hand, and check whether series share a timing provider.

## Data model

Start from these concepts and refine as needed:

- `drivers`
- `driver_aliases`
- `championships`
- `championship_seasons`
- `events`
- `races`
- `race_entries`
- `standings`
- `rule_documents`
- `rule_sets`
- `points_scales`
- `bonus_awards`
- `penalty_records`
- `driver_categorisations`
- `source_snapshots`
- `manual_overrides`
- `validation_issues`

`manual_overrides` must include a reason, source, and timestamp.

Driver identity is a major concern. Handle transliteration, spelling differences, nationality changes, and name changes. Never merge two drivers only because their names look similar.

## Architecture

### Pipeline

1. **Fetch:** use a per-source adapter and store the raw HTML, PDF, or API response.
2. **Parse:** convert raw data into structured records. Parsers must be replayable from saved snapshots.
3. **Normalize:** map championship, event, and driver names.
4. **Validate:** check row counts, position gaps, duplicates, source disagreements, and impossible values.
5. **Calculate:** run a pure rules engine that returns the total and a full explanation.
6. **Publish:** generate static JSON or serve the same data through an API.

### Suggested stack

- Python for scraping and data processing
- PostgreSQL for storage
- pytest for tests
- React and TypeScript for the frontend
- Docker Compose for local development and deployment
- A scheduled job after race weekends

Static JSON is enough for the first site. A public API comes later.

## Hosting

Planned host: Lenovo ThinkCentre M900 Tiny mini PC, i3-6100T, 8 GB RAM.

Requirements:

- Run services in containers.
- Prefer Cloudflare Tunnel over opening router ports.
- Keep public sites isolated from personal NAS storage.
- Automate off-site database backups.
- Use HTTPS. `.dev` domains require it.
- Keep development independent of the mini PC so local Docker Compose works first.

Possible URL structure:

```text
myname.dev/
├── f1/super-licence
├── f1/stewards
└── f1/api
```

If reliability becomes important, keep generating data on the mini PC but host static output on Cloudflare Pages.

## Roadmap

### Phase 0: research

- [x] Download and archive applicable Appendix L versions (2022–2026).
- [x] Verify the rule summary against official text.
- [ ] Build a rule-to-data matrix. Add the regulation year as a column on every rule row.
- [ ] Audit 2023-2026 sources for the first five series.
- [ ] Record each source's format, terms, starter availability, and fallback.

### Phase 1: manual proof of concept

Detailed steps: `PROTOTYPE_PLAN.md`.

- [ ] Create rule data for the required seasons.
- [ ] Enter first-batch standings in CSV.
- [ ] Build the rules engine and tests.
- [ ] Reproduce totals for several known drivers, checking every number by hand.

Do not scale scraping until this phase passes.

### Phase 2: first batch automation

- [ ] Build source adapters.
- [ ] Store raw snapshots.
- [ ] Add parsing and validation.
- [ ] Add race entries.
- [ ] Add scheduled updates.

### Phase 3: first public version

- [ ] Build the leaderboard.
- [ ] Add driver detail pages.
- [ ] Show source links and calculation breakdowns.
- [ ] Add eligibility filters and confidence labels.
- [ ] Deploy to `myname.dev/f1/super-licence`.

### Phase 4: expansion

- [ ] Add remaining single-seater series.
- [ ] Add FIA-certified F4 championships.
- [ ] Add karting.
- [ ] Add GT, endurance, shared-car handling, and other series.

### Phase 5: public API and analysis

- [ ] Publish a documented API.
- [ ] Add projections and what-if tools.
- [ ] Add alerts for rule or result changes.

## Testing and validation

Test at minimum:

- each rule version
- both qualification windows
- overlapping and non-overlapping championships
- karting cap and validity
- field-size reduction
- free practice cap
- ties and missing data, once rules are confirmed
- corrected results
- real driver examples

Use historical cases as tests where possible. The Colton Herta example is useful because a display error on IndyCar's website produced an incorrect points calculation: https://www.the-race.com/formula-1/why-colton-herta-still-one-point-off-f1-superlicence.md

Every external source can be wrong. Where possible, compare at least two sources.

## Manual maintenance

Expect manual checks for:

- new Appendix L versions
- new or removed championships
- changed points scales
- FIA-certified F4 changes
- unusual calendar or eligibility decisions
- broken scrapers
- post-season result changes

Calendar changes should mainly be handled through event data. For example, if the Qatar or Abu Dhabi rounds move, update events and let projections and checks recalculate.

## Ideal final version

The final site should let someone answer these questions quickly:

- Who is eligible for the next F1 season?
- Who is close to 40 points?
- What does a driver need to finish in the standings to qualify?
- Which points expire next?
- How was a driver's total calculated?
- Which source supports each number?
- Which points are confirmed, provisional, incomplete, or unofficial?

### Final feature set

- all eligible championships from every applicable year
- full historical rule versions
- driver pages with season-by-season breakdowns
- eligibility filters by year
- points expiry timeline
- what-if finishing position simulator
- projected totals during the season
- rule explanations linked to the relevant FIA text
- source and revision history
- data-quality indicators
- public, documented API
- automatic updates after race weekends
- alerts for regulation changes and source failures
- integrated penalty and stewards data

## Next project: stewards' decisions analyzer

Planned URL: `myname.dev/f1/stewards`

Goal: create a searchable database of stewards' decisions and show how similar investigated incidents have been handled.

Build this after the Super Licence tracker foundation exists. Reuse its driver identities, event data, source storage, and deployment setup.

Planned pipeline:

1. Collect FIA decision PDFs.
2. Extract text.
3. Convert decisions into a strict schema.
4. Hand-label a few hundred decisions.
5. Measure LLM extraction against the labelled set.
6. Compare decisions with FIA penalty guidelines and similar past cases.
7. Launch with one or two categories, such as causing a collision and leaving the track to gain an advantage.

Important constraints:

- Only say "of investigated cases like this", because the dataset excludes uninvestigated incidents.
- Label decisions by guideline era.
- Show sample sizes, such as `7 of 9`, not only percentages.
- Use "unusual compared with similar cases", not "wrong".
- Show comparable cases so readers can judge them.
- Be careful with text-based prediction because stewards' reasoning can reveal the outcome.
- Avoid individual steward rankings at first.
- Run extraction separately. The mini PC should serve results, not host a large model.

The analyzer can later supply penalty data to the Super Licence tracker.

## Open questions

Answered from Appendix L (2026-11-04):

- ~~Exact 2026 Supplement 1 conditions~~ See "Calendar and field conditions".
- ~~Which F4 championships are eligible~~ 2022–2025: one generic "National F4 certified by the FIA" row. 2026: 13 F4 championships named individually, plus the F4 Middle East Trophy at a lower scale.
- Championships spanning calendar years: partly answered. Notes i and ii imply the year a championship **ends** decides the scale and which year it counts in. The window part is an interpretation.

Still open (not defined in Appendix L 2022–2026):

- Whether the 80% rule uses races or events (working assumption: events, provisional)
- Rounding rules for reduced and shared-car points
- How tied final positions are handled
- How the best two-championship combination is selected
- Which championships count as having a penalty points system (FRECA, F4s?)
- Whether F2/F3 decision PDFs state penalty points in a consistent, parseable way
- Whether FastF1 FP data is complete for every needed session
- Best sources for penalty records in each eligible FIA series
- Whether to ask the FIA directly about the undefined rules
