# F1 Super Licence Tracker

## Project summary

Build a readable, source-backed tracker for FIA Super Licence eligibility points. It should cover every driver with points across eligible championships and explain how each total was calculated.

This is the first project in a personal motorsport section at `myname.dev/f1` (domain name is a placeholder). The second planned project is a stewards' decisions analyzer that reuses the same driver database.

Existing sites are hard to read. This project competes on clarity, traceability, and coverage.

**Status:** planning complete, implementation not started.

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

**Verification warning:** the rule summary below came from Wikipedia, Formula 1 coverage, and a bilingual 2025 copy of Appendix L. The official 2026 PDF was not read, and the general Supplement 1 conditions were not found in the reviewed section. Verify every rule against the official documents before implementing it.

Store each rule document version with:

- document year
- publication date
- source URL
- local archived copy
- effective date or applicable seasons, once verified

Monitor the FIA Appendix L page for changes and alert me when it changes.

## Rule summary to verify

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

The rule allowing the best three of four years applied only when the three-year window included 2021. Keep it only for historical calculations if needed.

Normal full Super Licence threshold: 40 points.

### Championship points

- Points are based on final championship position.
- Scales vary by championship and regulation year.
- Old and new scales can coexist while older results remain valid.

Known examples requiring versioned rules:

- IndyCar old and new scales
- Super Formula old and new scales
- DTM old and new scales

### Calendar and field conditions

- A championship season needs at least five events across at least three circuits.
- Alternative circuit layouts count as separate circuits.
- If fewer than 16 drivers start the first race of an event, points are reduced by 10% per missing driver.
- If this happens at several events, use the event with the lowest number of starters.
- Some North American series have an FIA-homologated circuit condition. Confirm the exact rule.
- Some season-specific exceptions exist, such as F4 South East Asia at 50% in 2023.

### Combining championships

- At most two championships can count from one calendar year.
- The second championship must start after the first ends.
- Confirm how the best valid combination is selected.

### Bonus points

- Free practice: 1 point for at least 100 km in a free practice session.
- Free practice is limited to one point per World Championship event and 10 points in total.
- Penalty-free season: 2 points for completing an entire FIA championship with a penalty point system without receiving penalty points.
- Macau: F4 win = 2, FR win = 3, F3 win = 5.

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

Confirm rounding and all edge cases.

### Other eligibility conditions

Show these separately from the points total:

- Grade A licence
- age requirement and FIA discretion exception
- theory test
- 80% of each of two full seasons in Supplement 1 single-seater championships for first-time applicants
- previous licence holder routes
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

Rows in the FIA table are not always one championship. For example, the F4 row covers many series, the LMP2 row combines several series, and old-scale rows are rule versions.

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
- Macau winners
- karting results
- crew lists
- FIA driver categorisations

Free practice distance and penalty-free data are likely hard. Find sources before assuming automation. Race results do not show licence penalty points.

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

- [ ] Download and archive applicable Appendix L versions.
- [ ] Verify the rule summary against official text.
- [ ] Build a rule-to-data matrix.
- [ ] Audit 2023-2026 sources for the first five series.
- [ ] Record each source's format, terms, starter availability, and fallback.

### Phase 1: manual proof of concept

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

- Exact 2026 Supplement 1 conditions
- Whether the 80% rule uses races, events, or another measure
- How points are assigned for championships spanning calendar years
- Rounding rules for reduced and shared-car points
- How tied final positions are handled
- Best sources for free practice distance
- Best sources for penalty records in each eligible FIA series
- Which F4 championships are eligible for each season
