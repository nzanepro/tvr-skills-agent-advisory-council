# Verification and addenda

Read when running the persona-free verifier, writing VERIFICATION.md, or publishing corrections as
an addendum.

## Contents

1. Why a verifier
2. What counts as load-bearing
3. How to check a claim
4. Verdicts
5. Writing addenda
6. Disagreements between members

## 1. Why a verifier

In the method's first use there was no verifier at first. Three dossier errors, an unreplicated
result and a conclusion resting on an empty output file all got into the record, and each would
have been caught by one agent whose only job was checking. The verifier has no persona, no
mandate and no vote, so it has no reason to prefer one answer. It is the cheapest seat and the one
that should never be dropped.

## 2. What counts as load-bearing

A claim is load-bearing if an option, a vote or a risk would change were it false. Typically:

- numbers: market size, prices, conversion or churn rates, costs, dates, headcounts;
- rules: regulations, platform policies, contract terms, licence terms;
- market facts: what a competitor offers and charges (from public sources), who the customers are;
- attributions: "survey X found", "report Y says", "the pilot showed";
- comparisons: any table where rows are compared with each other or with a reference.

List them all first, with where each was made (dossier section, seat report section). State the
count: "Checked 14 of 14 listed claims". A verification that does not say how many claims it
covered cannot show it covered them all.

## 3. How to check a claim

1. **Go to the primary source**, or an independent one. Never check a number against the report,
   spreadsheet or tool that produced it; that repeats its arithmetic without testing it.
2. **Check the label as well as the value.** Is the number from the segment, year, version or
   case the text says? Mislabelled rows were among the most common errors in the first use.
3. **Check the baseline.** In a comparison, is every row measured against the same reference?
   Recompute any percentage from its two numbers.
4. **Check the selection.** Is the quoted figure the whole series or the favourable point? Look
   for the other data points.
5. **Check what "validated" means.** A baseline described as validated may never have been
   checked on the quantity now in dispute.
6. **Look for cancellation.** A total that looks right can hide two large errors of opposite sign;
   check the components when they are available.
7. **Positive control on searches.** Before recording "no such rule", "no competitor offers
   this" or "no data", confirm the search could have found it (search for something you know
   exists in the same place). Otherwise record UNVERIFIED with where you looked: never reached is
   not verified absent.
8. **Record your method** in one line, so another agent could repeat the check.

Without web access, the verifier checks internal consistency (arithmetic, units, labels,
baselines, whether cited sources say what is claimed if they are in the folder) and marks
everything else UNVERIFIED with "no web access" as the place searched.

## 4. Verdicts

| Verdict | Meaning | Goes into an addendum? |
|---|---|---|
| CONFIRMED | The source supports the claim as stated | No |
| CONTRADICTED | The source says otherwise; give the correct value | Yes |
| MISLEADING | True, but framed so it will mislead (wrong baseline, one favourable point, missing condition) | Yes, with the fuller statement |
| UNVERIFIED | Could not reach a source; say where you looked | Only if load-bearing: as an open item |
| ESTIMATE | Not checkable; method stated and judged reasonable or not | Only if the method is unsound |

End VERIFICATION.md with the summary in four groups: failed and load-bearing; failed and not
load-bearing; true but misleading; could not reach. Then "everything else confirmed".

## 5. Writing addenda

Create each with `council.py addendum FOLDER`; it picks the next letter and the next item number.

- **Corrections and measurements only.** No member's position, vote or reasoning ever appears in
  an addendum. In the first use, an addendum that embedded one team's votes as shared fact broke
  the independence of every later seat. `council.py check` fails an addendum with a Position or
  Vote line.
- **State precedence** at the top: "Wins over DOSSIER-01 and earlier addenda where they conflict."
- **Number items continuously** across addenda (01A items 1-9, 01B items 10-14), so every
  correction has one stable reference members can cite ("ADDENDUM-01A item 3").
- **Each item:** what the dossier said, what is correct, the source, who found it (verifier or
  the seat), and which question or option it affects.
- **Credit members who found errors** ("found by: cfo seat"); it is a fact about the record, not
  a position.
- **Publish corrections as soon as they are confirmed**, before the tally and Round 2. Hold votes
  in escrow; do not hold corrections.
- **Withdraw your own errors plainly.** "The dossier's figure is withdrawn" is better than a quiet
  edit. Never edit the dossier after Round 1 starts; the addendum is the edit.
- **End with the standing instruction** to keep checking the record.

## 6. Disagreements between members

When two members reach different answers on the same factual question, both backed by evidence,
the addendum records both with their evidence, **without adjudicating**, and says what each would
imply. The facilitator does not choose before every member has voted. The tally then says whether
the recommended action depends on which is right; often it does not, and the split can stay open
in the recommendation's open questions with the test that would settle it.
