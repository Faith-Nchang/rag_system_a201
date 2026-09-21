# The Unofficial Guide

Faith Nchang — `campus_life` corpus.

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

This is a retrieval-augmented Q&A system over `campus_life`, a corpus of 88
short, informal notes students wrote about registrar deadlines, housing,
dining halls, laundry, and course workloads. It answers specific questions
like "what happens if I drop a course after week two?" or "how many hours a
week does BIOL 160 take?" by retrieving the note that actually covers the
topic and having the model answer from that note alone, always naming which
file it used. If a question isn't covered by any of these notes — a general
trivia question, say — the relevance gate catches it before the model ever
sees it and the system says so instead of guessing.

## Chunking Strategy

**Chunk size:** 1000 characters
**Overlap:** 150 characters (only used on the fallback path — see below)

When I read through `campus_life` in Milestone 1, every document turned out
to be a short, single-topic post — the longest one is 563 characters
(checked with `wc -c corpora/campus_life/documents/*.txt`), and most are a
title plus one to three short paragraphs. The starter's original 800-char
fixed-window splitter (`fallback_split`) happened to never cut any of them
either, but only by accident of the round number — it pays no attention to
sentence or paragraph boundaries, so a slightly longer document would have
been sliced mid-sentence for no reason.

I replaced `split_documents` with a paragraph-merge strategy instead: it
merges a document's paragraphs into one chunk as long as the result stays
under `CHUNK_SIZE`, and only falls back to a fixed character window (with
`CHUNK_OVERLAP`) for a single paragraph too long to keep whole. I set
`CHUNK_SIZE` to 1000 — comfortably above the longest document in this
corpus — on purpose, so the cap is sized to what I actually read rather than
picked in the abstract. Running it produces 88 chunks (same count as the
fallback), but for a real reason this time: no document here is long enough
to need splitting, and the fallback window never triggers once. The longest
resulting chunk is 549 characters, the shortest 178.

I didn't change my mind partway through — the corpus made the "keep each
post whole" decision obvious before I wrote any code.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_biol_160.txt#0` — produced by: `chunker.py::split_documents`

```
BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: `course_hist_118_workload.txt#0` — produced by: `chunker.py::split_documents`

```
Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```

**Chunk 4** — source: `dining_pellew_dining_hall_followup.txt#0` — produced by: `chunker.py::split_documents`

```
Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_innisfree_hall.txt#0` — produced by: `chunker.py::split_documents`

```
Innisfree Hall — what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.
```

## Sample Answer

**Question:** What are the wait times at Kestrel Commons around lunchtime?

**Answer:**

```
Based on the documents, the wait times at Kestrel Commons are 20 to 25 minutes between 12:15 and 1:00, and under 5 minutes before 11:45.

Source: `dining_kestrel_commons.txt` (and also mentioned in `dining_kestrel_commons_followup.txt`).
```

**My relevance cutoff:** 0.585, set in `config.py`.

I ran the 5 questions in `questions.py`'s `QUESTIONS` and the 5 in
`OUT_OF_SCOPE` through `python app.py retrieve` and recorded the best
(lowest) distance for each. The two groups didn't overlap at all — every
real question came back under 0.35, every out-of-scope question came back
over 0.82 — so I set the cutoff at 0.585, the midpoint of that gap, rather
than leave the starter's 0.6 default unexamined.

| Question | In corpus? | Best distance |
|---|---|---|
| How is the housing lottery ordered for juniors and seniors? | Yes | 0.215 |
| What happens if I drop a course after week two? | Yes | 0.345 |
| How many hours a week does BIOL 160 take? | Yes | 0.325 |
| What are the wait times at Kestrel Commons around lunchtime? | Yes | 0.194 |
| When is the best time to do laundry in Old Brewhouse? | Yes | 0.325 |
| What is the capital of Mongolia? | No | 0.825 |
| How do I change the oil in a diesel engine? | No | 0.934 |
| Who won the 1994 World Cup? | No | 0.886 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.844 |
| How do I write a for loop in Rust? | No | 0.896 |

## How I Used AI

**1.** I asked Claude to implement the Milestone 3 chunking strategy in
`chunker.py`. Before writing anything, it read several documents and ran
`wc -c` across the whole corpus to check document lengths, and came back
with a paragraph-merge strategy (merge paragraphs up to `CHUNK_SIZE`, fall
back to a character window only for an oversized paragraph) instead of just
picking a new fixed chunk size. I kept the approach as given, since the
reasoning — that the corpus made "one post, one chunk" the obvious answer —
matched what I'd seen reading the documents myself.

**2.** I hadn't written the 5 `QUESTIONS` for Milestone 2 yet, so I asked
Claude to draft them from the corpus. It picked one question from each of
five different topic areas (housing, registrar deadlines, coursework,
dining, laundry) so retrieval wouldn't be tested against the same document
twice, and filled in an `expects` phrase for each per the file's own
instructions. I reviewed all five and kept them as given.

No stretch features attempted this unit.

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
