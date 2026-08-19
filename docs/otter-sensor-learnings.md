# Otter Transcript Sensor — Field Notes from a Working Ingestion Pipeline

**Status:** reference document for the Otter transcript sensor (the SDK's first
reference sensor) and for the Output Record contract design.
**Source:** a personal Otter → knowledge-base ingestion pipeline operated
continuously since spring 2026, covering ~1,700 meeting transcripts across
sync, enrichment, and downstream task extraction. Everything below was learned
by running it, usually the hard way.

The pipeline predates this SDK and lives outside it, but it exercises the same
job the Otter sensor will do: pull messy transcripts from a third-party API and
emit structured, trustworthy records for downstream consumers. These notes are
what we would want to inherit rather than rediscover.

---

## 1. Identity: key on the source's stable ID, never on title or filename

The single most load-bearing decision. Every meeting gets exactly one local
record, keyed on the source's meeting ID (`otter_id`), and every write path
resolves identity through that key.

What went wrong before this rule existed:

- **"Skip if filename exists" silently dropped meetings.** Recurring meetings
  and title collisions produce identical title slugs. An existence check on
  filename treated a *new* meeting as already-synced and dropped it. Keying on
  ID makes the same situation an in-place update of the right record.
- **Two writers with their own slug functions produced two files per meeting.**
  One ASCII-stripped accents (`Reunión` → `reunin`), the other kept raw
  unicode; one used UTC dates, the other local. The fix was a single canonical
  identity module (slug + date rules) imported by every writer. In SDK terms:
  identity normalization belongs in the SDK core, not in individual sensors.
- **Notation drift splits recurring meetings.** `1:1`, `1x1`, `1-1`, and
  `1 on 1` are the same meeting series to a human and four different slugs to
  a naive slugifier. Normalize known notation before slugging.
- **Real collisions still happen.** Two *different* meetings can legitimately
  share a title and date. The guard: if the canonical filename exists but its
  stored source ID differs, suffix with a short ID fragment — never clobber.

**Contract implication:** the Output Record needs a required, stable
`source_record_id` (native to the upstream system), and dedup/update semantics
must be defined on that field.

## 2. Dates: local time, decided once, documented

Otter serves `start_time` as a local-time string in one context and other
formats elsewhere. We standardized on the meeting's **local start date**
because that is how the source UI names the meeting and how a human refers to
it ("Tuesday's standup") — a UTC date puts evening meetings on the wrong day.
Whatever a sensor chooses, the choice must be made once, shared by every write
path, and recorded in the contract. Split-brain date logic was a real source
of duplicate records.

**Contract implication:** timestamp fields need an explicit timezone rule in
the schema, not per-sensor convention.

## 3. The source is eventually consistent — design for placeholder bodies

Fetching a transcript too early returns something that *looks* like a
transcript but isn't: empty bodies, "No transcript available", "still
processing" notices, deferral pointers back to the source, HTTP-error stubs.
If you write these as finished records, they poison the corpus quietly.

What held up:

- **A conservative placeholder detector.** Flag known placeholder phrases only
  in *short* bodies, bare placeholder tokens, and ultra-short stubs. Never use
  length alone — genuinely short transcripts exist (a meeting that captured a
  single line is still a real record), and a long real transcript can mention
  "still processing" mid-conversation.
- **Self-healing re-queue.** A record marked enriched whose body is
  empty/placeholder re-enters the scan queue automatically on the next run,
  so early fetches repair themselves without manual intervention.
- **Never clobber a real body.** Automatic replacement is allowed only when
  the existing body is classified as a placeholder **and** the new fetch is a
  valid, non-placeholder body. Being substantially longer may be an additional
  conservative check; it is never sufficient on its own. A real body is not
  automatically replaced merely because another fetch is longer. Metadata
  refreshes must not be able to destroy transcript content, even when the API
  returns junk. If a source supports legitimate edits to a completed
  transcript, handle those through an explicit, versioned update path rather
  than this placeholder-repair rule.

**Contract implication:** records need a processing-state signal (or the
sensor must guarantee it only emits completed records), and re-emission of an
updated record for the same `source_record_id` must be legal and well-defined.

## 4. Speakers: calendar participants are hints, not labels

The hardest data-quality problem in the whole pipeline.

- **Calendar participant metadata misaligns with actual speakers** — the
  name↔email pairings Otter returns are frequently shifted or wrong, and
  invitees are not attendees. Treat calendar metadata as a hint for
  role-inference, never as ground truth for who spoke.
- **Parse speakers from the transcript itself** (the timestamped speaker
  lines), and filter unknown-speaker markers before emitting.
- **Structured fields arrive as convention-formatted strings.** Action items
  come as `"Person - email : action text"` — parse defensively and keep a
  fallback for lines that don't match, because some never do.

**Contract implication:** distinguish `participants` (claimed/invited) from
`speakers` (observed in the evidence) as separate fields with different trust
levels. Collapsing them loses information the claims layer needs.

## 5. Auth: session expiry is a first-class failure mode

Third-party session auth expires, and scheduled/headless runs cannot complete
an interactive login. Design consequences:

- Bootstrap credentials interactively once; persist the session material the
  sensor needs; expect it to expire.
- On auth failure, **degrade gracefully and surface a distinct
  `AUTH_EXPIRED`-type status** instead of crashing or, worse, emitting empty
  results that look like "no new meetings."
- An auth failure that presents as an empty sync is the most dangerous
  variant — the pipeline looks healthy while silently going stale. Distinguish
  "authenticated and found nothing" from "could not look."

## 6. The sync loop that held up

```
search(created_after=window) ──► diff by source ID against local manifest
        ──► fetch only missing ──► write/update keyed on ID
```

- **Idempotent and resumable:** re-running any stage is always safe; a crashed
  batch just re-runs.
- **Overlapping windows, not checkpoints:** sync "last 7 days" daily rather
  than tracking a high-water mark. Costs a few redundant diffs, eliminates an
  entire class of missed-meeting bugs.
- **Separate stages:** raw sync, metadata enrichment, and downstream
  extraction (e.g. action items → task queue) are independent passes. Baking
  enrichment into ingestion couples failure modes; keeping extraction
  downstream lets the record schema stay stable while consumers evolve.
- **Batch runs maintain a live in-memory ID index** so later items in the same
  batch see earlier writes — otherwise a batch can create twins that the
  per-item logic would have caught.
- **Keep an ingested-vs-missing inventory.** Never report a corpus "complete"
  from the absence of errors; report it from a diff against what the source
  says exists.

## 7. Enrichment: what earned its place in the record

The enriched record format that proved useful downstream (knowledge-base
search, meeting recall, task extraction):

- **Frontmatter:** title, local date, ISO start time, duration, stable source
  ID, source system, enrichment flag + enrichment date, speakers (with
  inferred roles), topics, tags, a relevance score, and an **access tier**.
- **Body sections:** Summary, Action Items, Identified Speakers, Key Themes,
  then the full raw transcript last.

Two of these deserve emphasis in the Output Record contract:

- **Enrichment versioning** (`enriched` + `enriched_date`, better: a version)
  — you will re-enrich; consumers need to know which vintage they're reading.
- **Access tier / consent on every record from day one.** Meeting transcripts
  are the clearest possible case: a team standup and a 1:1 have different
  sharing semantics even though they're the same record type from the same
  sensor. Retrofitting consent onto an existing corpus is far more painful
  than carrying a field that is mostly set to a default. This also aligns
  with downstream consumers of the claims engine (biocultural crediting work)
  where data sovereignty is non-negotiable and claim-makers can be
  collectives, not individuals.

Also: transcripts arrive in multiple languages. Slugging, enrichment, and
keyword logic must not assume English.

## 8. Prioritization beats completeness for the enrichment backlog

When the backlog exceeds what a run can process, a simple priority score
(recency + domain-keyword relevance) on the un-enriched queue keeps the
pipeline useful while it catches up. Design the sensor's enrichment stage to
process "top N by priority," not "oldest first."

---

## Quick checklist for the Otter sensor implementation

- [ ] Key all writes on the Otter meeting ID; updates in place, never
      filename-existence checks
- [ ] One shared slug/date normalization path (SDK core, not sensor code)
- [ ] Placeholder-body detection + self-heal re-queue; never clobber a real
      body
- [ ] `participants` (calendar) and `speakers` (observed) as separate fields
- [ ] `AUTH_EXPIRED` as a distinct, surfaced status; empty-sync ≠ auth-failure
- [ ] Overlapping sync windows; idempotent stages; ingested-vs-missing diff
- [ ] Enrichment version and access-tier/consent fields on every record
- [ ] Defensive parsing of convention-formatted metadata strings
- [ ] No English-only assumptions
