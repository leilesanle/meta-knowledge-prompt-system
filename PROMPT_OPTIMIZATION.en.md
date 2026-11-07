# Prompt Optimization: The User Speaks Plainly, the AI Translates into Professional Language

中文版：[PROMPT_OPTIMIZATION.md](PROMPT_OPTIMIZATION.md)

> This is the operations manual for one of this repository's two core rules (the expanded version of method card M021). The other is "learn the terms first, then solve the problem" (P001) — the dictionary is its tool.

## What problem it solves

When users assign tasks, they speak plainly: with pronouns whose referents are implied, with omissions, and occasionally with homophone typos from voice input. Executing the literal words gets the task wrong most of the time; making the user learn the jargon and compose prompts themselves pushes the cost back onto the user.

This rule puts the translation cost on the AI's side: **the user just says it in their own words; the AI first optimizes those words into a directly executable prompt, then executes the optimized version, and afterwards accounts for the work against the optimized version.**

## The three-step flow

1. The user says it in their own words — no need to compose anything.
2. The AI produces the optimized prompt and sends a copy back to the user — the user picks up how that sentence is said in professional terms, and can spot on the spot whether the AI misunderstood.
3. The AI executes the optimized version; the receipt accounts for it item by item against the optimized version (which items were done, which fell short).

Scope: task-type messages only (assigning work, getting things done, producing deliverables). Casual chat and simple Q&A do not go through this flow.

## The eight optimization steps

1. **Lock the intent**: judge the real result the user wants; don't copy the literal action.
2. **Replace the terms**: swap plain words for the professional terms and card IDs in the dictionary; when a new field is hit, first add its terms per P001, then optimize.
3. **Restore the references**: resolve pronouns, omissions, and homophone typos back into concrete names, numbers, and paths.
4. **Order the steps**: organize the steps by that trade's standard workflow; don't improvise a homemade route.
5. **Write the constraints hard**: only / never / must / numeric thresholds — no soft words like "try to" or "appropriately."
6. **Two anchors**: a currency anchor (data as of when, which version is cited) + an object anchor (exactly which file, which object is being acted on).
7. **A stop-loss line**: write the retry limit and the fallback route in advance; when one route fails, switch immediately instead of grinding in place.
8. **Pre-wire the acceptance check**: write down in advance what will be checked against, what counts as failure, and the deviation threshold — then check against the table when done.

What gets delivered must be the full text of a directly executable prompt; passing off a one-line summary as the thing itself counts as not having optimized at all.

## How it connects to the dictionary

Step 2 is the pivot of the whole system: every professional term used in optimization is looked up in `dictionary/terms.json` — first use the retriever to locate the problem type and pull the method card, then write the card names, terms, and card IDs into the optimized version. That makes "saying it right" and "where the terms come from" a single chain:

plain-language request → prompt optimization (terms swapped in from the dictionary) → retrieval hits a method card → execute by the card → receipt accounts for it.

## Acceptance criteria

- Hit rate = the share of optimized prompts that pass review on the first pass; target ≥95%.
- Missed cases must be backfilled into the dictionary (add the term, the card, or the alias) — the same kind of problem may not miss twice.
- Term-splitting must cover every dimension the problem involves: splitting only the main dimension and missing a parallel one makes retrieval miss along with it (a measured lesson; see the pitfall field of card M021 in the dictionary).

## Common pitfalls

- Copying the literal action and losing the real intent.
- Soft words leaving ambiguity ("handle it," "make it better" going straight into execution).
- No currency or object anchors: grabbing the wrong version, touching the wrong file.
- Writing the method but not the review, so the finished work can't be accounted for.
- Delivering a one-line summary as if it were the prompt.
