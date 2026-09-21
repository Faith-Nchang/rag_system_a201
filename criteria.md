# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:** My chunking strategy merges each document's paragraphs
into one chunk, so on this corpus every retrieved chunk either contains the
whole answer or none of it — there's no partial-chunk case to worry about.
When I ran all 5 questions through `python app.py retrieve` in Milestone 4,
the correct document came back as the #1 result every time, with distances
between 0.194 and 0.345. Still, two of my topics have near-duplicate
documents with similar phrasing (dining halls each have a "followup" thread,
and every course has a matching `_workload` file), so an embedding mismatch
could plausibly rank a near-duplicate above the right document. 4 of 5 leaves
room for exactly one such near-miss without hiding a real retrieval problem.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:** This isn't a fuzzy judgment call the way "contains the
answer" is — `generate.py`'s `GROUNDING_INSTRUCTION` explicitly instructs the
model to name the filename of the excerpt it used, and `build_prompt` labels
every chunk with `[from <source>]` before it ever reaches the model. Since
citing the source is a mechanical instruction-following task rather than a
reasoning one, I expect it to succeed every time, not just 4 of 5 — a miss
here would mean the prompt itself is broken, not that the question was hard.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:** When I measured this in Milestone 4, the two groups
didn't overlap at all: my 5 real questions came back with best distances of
0.194-0.345, and the 5 `OUT_OF_SCOPE` questions came back at 0.825-0.934 — a
gap of nearly half a point with nothing in it. I set the cutoff at 0.585, the
middle of that gap. Given how clean the separation was, I'd expect 5 of 5,
not 4 of 5, but I'm keeping the target at 4 of 5 because I've only tried five
out-of-scope questions once; a sixth one phrased in a way that happens to
share vocabulary with the corpus (e.g. asking about an "engine" the way a
noise complaint might) could still slip under the cutoff, and 4 of 5 is the
honest floor for a gate I've only stress-tested once.

---

## 4. Chunks read as complete documents, never a mid-sentence cut

For 5 of my 5 sampled chunks, the chunk starts at the document's title line
and ends at the document's last full sentence — no sentence is cut in half at
either end.

**Why this target:** `split_documents` in `chunker.py` merges a document's
paragraphs into one chunk as long as the result fits under `CHUNK_SIZE`
(1000 characters), and only falls back to a fixed character window for a
paragraph too long to keep whole. When I ran it on `campus_life`, the longest
resulting chunk was 549 characters — well under the cap — so the fallback
path never triggered once across all 88 chunks. Because the merge is bounded
by paragraph breaks rather than a character count, a mid-sentence cut is not
just unlikely here, it's structurally impossible unless a document exceeds
1000 characters (none currently does). That's why I can set this at 5 of 5
instead of 4 of 5 — a miss here would mean my understanding of the pipeline
is wrong, not that I got unlucky.

---

## 5. Retrieved chunks surface the specific fact, not just the topic

For at least 4 of my 5 test questions, the model's answer contains the exact
`expects` phrase I wrote for it in `questions.py` (e.g. "9 to 11 hours" for
the BIOL 160 workload question) — not a paraphrase or a vaguer restatement.

**Why this target:** Criterion 1 only checks that the right chunk came back;
it says nothing about whether the model's answer actually surfaces the
specific number or phrase a person asked for, versus a technically-true but
useless answer like "it varies." I wrote `expects` for each question in
Milestone 2 before seeing any results, specifically so I'd have something
concrete to check the generated answer against rather than eyeballing it. I
set 4 of 5 rather than 5 of 5 because this depends on the model's phrasing as
well as retrieval — the model could restate a fact accurately in words that
don't literally match my `expects` string even when the answer is correct,
and I don't want one strict string match to fail a criterion whose real
target is retrieval quality.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
