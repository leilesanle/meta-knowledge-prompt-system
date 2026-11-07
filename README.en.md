[中文](README.md) | English

# A Meta-Knowledge-Driven Problem-Solving System

## What problem it solves

When an AI answers professional questions, it tends to stay generic: it doesn't look up a method, and it doesn't distinguish "this problem needs a professional framework" from "this one doesn't."
This system makes the AI first locate "problem type → applicable method," then fill in the terms, and only then solve — and it uses admission gates and logs to guarantee the AI actually looked things up and used them, instead of just saying it did.

## The entry point is natural language: you speak plainly, the jargon is handled inside the system

The caller of this system is an AI, not a person. The full chain is:

**A plain-language request → the AI first rewrites it into professional terms via "prompt optimization" (M021) → keyword retrieval hits a method card → the AI executes by the card → the receipt cites the entry IDs**

A measured example (2026-11-07):

> Asked: "I want to use one photo plus a voice recording to make a talking-head video I can post. What should I figure out before I start, and where is it most likely to go wrong?"
> The AI split the terms (lip sync / animated base plate / talking-head video) → hit M014 · Lip-Sync Talking-Head Production → answered by the card: master-image standards, audio specs, route selection, and that card's known pitfalls.

The boundary, stated up front so there's no misunderstanding: the retriever itself only does keyword matching — **feeding it a whole sentence scores 0 hits**. That's not a defect, it's a division of labor: understanding plain language and splitting it into keywords is the front layer's job (the AI + prompt optimization); the retriever only fetches cards precisely by term. The same set of 7 test questions run through this chain hit 7/7, so the acceptance metric is set as "the first-pass rate of optimized prompts," not whole-sentence lookup dressed up as ability.

Companion document: `PROMPT_OPTIMIZATION.en.md` (the full prompt-optimization method).

## How it differs from an ordinary prompt collection

- Three-layer structure: problem-type index → method cards → term list (terms hang under methods and explain their role there; definitions are never stockpiled in isolation)
- Admission has gates: a three-question provenance check + a Feynman gate + admission ablation + two rounds of deduplication — nothing enters without passing
- Triggering has a test: "Remove this term — would the solution go wrong or degrade?" When exemption is right, it exempts cleanly
- The process has logs: failure records, a version line, ablation baselines — reproducible and auditable

## How to use it (two ways, pick either)

**Option 1: paste it to an AI**
Paste the full text of RULES.en.md into custom instructions / project rules, and put the dictionary (dictionary/terms.json) in the knowledge base.

**Option 2: run the retriever locally**

```
python scripts/find_term.py "银行对账"
python scripts/find_term.py --index        # problem-type index
python scripts/find_term.py --card M009    # full text of one method card
python scripts/find_term.py --flows        # flow cards (orchestration layer), brief table
python scripts/find_term.py --flow F001    # full text of one flow card
```

## What's in the dictionary

30 problem-type index entries / 26 method cards / 68 terms / 2 long-term principles (P001 "learn the terms first, then solve the problem," P002 the collection-and-application mechanism) / 1 flow card (F001 · Talking-Head Video Production, the orchestration layer: multiple method cards chained in real production order into a pipeline).
Examples: M009 Bank Reconciliation, M002 Monte Carlo Simulation, M014 Lip-Sync Talking-Head Production, M021 Prompt Optimization.
Every card contains: what problem it solves, trigger conditions, core steps, judgment criteria, common pitfalls, the original problem it came from, premises, and a Feynman self-explanation.

When a lookup hits a cell that is charted but not yet built, the system only reports "this cell is charted but unbuilt" — it never fabricates a card. See examples/ for instances.

## What it is not

- Retrieval is keyword matching (backed by an alias layer), not semantic search; rephrase a question and it may miss
- Card depth is filled in from primary classics; syllabi and standards only draw the boundaries of a field
- Charted-but-unbuilt cells are reported as such; no card is ever fabricated
- This system grew out of real tasks, so card quality varies: sources and confidence are labeled, and single-source experience cards say "unverified" out loud

## File guide

- `RULES.en.md` — the full rules (v1.3 final + patches; for dictionary data versions see VERSION_LOG.md)
- `PROMPT_OPTIMIZATION.en.md` — prompt optimization: the eight-step method for turning a plain-language task into an executable prompt (the expanded version of M021)
- `dictionary/terms.json` — the dictionary data (the full three-layer structure; currently in Chinese)
- `scripts/find_term.py` — the retriever (zero dependencies, Python 3 standard library)
- `scripts/check_reply.py` — a hard format check for replies: two-line opening / evidence line / measured values / self-check conclusion, gated before sending (zero dependencies)
- `scripts/seal_metadata.py` — a pre-publish metadata gate: if the four delivery-information fields are incomplete, the item may not enter the publish queue (zero dependencies)
- `RUNLOG.md` — process records, failures and fixes (how this system grew; currently in Chinese)
- `VERSION_LOG.md` — the version line, v1.0 → v1.4
- `examples/` — five real receipt cases: hit / charted-but-unbuilt / exempt / cross-domain / alias (currently in Chinese)
- `CONTRIBUTING.md` — how others add cards (they must pass the same gates)

## License

Content (rules, dictionary, logs, examples): CC BY-SA 4.0; scripts: MIT. See LICENSE.md.
