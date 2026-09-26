# Dossier guide: the shared factual record

Read when writing DOSSIER-NN-<slug>.md, or a follow-up dossier for a second question.

## Contents

1. What the dossier is for
2. Section by section
3. Framing rules
4. Errors that recur
5. Follow-up dossiers and addenda

## 1. What the dossier is for

Every member works from one identical record so nobody deliberates from different premises. It is
written once, before Round 1, and then kept current only through numbered addenda
(ADDENDUM-01A, 01B, ...). State at the top that later addenda win where they conflict.

The dossier is also the thing most likely to be wrong. In the method's first use, members found
real errors in it in every single round, and several settled a question by checking a source or
running the analysis the dossier said was missing. So the dossier ends by asking members to check
it, and the verifier checks its load-bearing claims independently.

## 2. Section by section

The template is `templates/DOSSIER.md`.

| Section | What goes in | Watch for |
|---|---|---|
| 0. The question in one line | The decision, neutrally | No verdict, no "settled", no "the only question left" |
| 1. Options | Every live option, always including do nothing, with reversibility and rough cost | An option missing because the author dislikes it |
| 2. Market or domain | Segments, geography, channel, competitors by type, size with source, trends | Market size from one vendor report with no method |
| 3. Goal, constraints, success | The measure of success, budget, time, red lines, who decides by when | Deadlines written as pressure rather than as a fact |
| 4. Facts | Numbered, each with a source and its date | Mixed baselines, stale numbers, one data point shown as a trend |
| 5. Estimates and assumptions | Numbered, each with its method and what would falsify it | Estimates promoted to facts by repetition |
| 6. What is not known | Gaps, and where each was searched for | "No data exists" when nobody looked |
| 7. Positions already held | The user's or organisation's leaning, labelled as a position to test | A leaning written as a premise |
| 8. What the council is asked | Three to six numbered questions, including the cheapest decisive step | Questions that presuppose the answer |

Keep it short enough to read in ten minutes: two to four pages. Detail belongs in linked sources.

## 3. Framing rules

1. **Neutral question.** "Should we introduce a paid tier, and if so for whom?" not "How do we
   roll out the paid tier?".
2. **No urgency framing.** "The council is the only thing between this and launch" or a heading
   such as "Decision 1 is settled by the data" tells members their vote is a formality. A
   deadline is a fact in section 3; the user's frustration is not a fact.
3. **The user's leaning is a position to test.** If the user or a previous reviewer has a view,
   put it in section 7 in their words and say the council should test it. When a later dossier
   exists because the user disagrees with an earlier verdict, say so plainly and quote the
   objection: that disagreement is often the most useful thing to examine.
4. **No member positions.** The dossier never carries a member's view, even from an earlier
   session. Earlier findings enter as facts with sources, not as votes.
5. **One baseline per table.** If a comparison table mixes baselines (different reference years,
   currencies, customer sets, or one source's number beside another's), it will mislead. Put
   every row on the same baseline and name it, or split the table.
6. **Show the whole series.** If you ran or found several data points, show all of them, not the
   one that looks best. Selective reporting is the error members are least likely to catch.
7. **Say what a number is.** A single point or an average; a fit or a measurement; which case or
   segment it came from. Mislabelled rows were a recurring error in the method's first use.

## 4. Errors that recur

Checked by the verifier, and worth checking before sending the dossier:

- A number attributed to the wrong case, segment, year or version.
- Two numbers with the same name that are computed differently (for example two definitions of
  "active user" or "margin") used interchangeably.
- A comparison where one row was scored against a different reference from the others.
- A favourable subset quoted as the whole ("the pilot converted at 12%" when that was one of four
  cohorts).
- A reassuring figure that is true only in one condition ("churn is 2%" for annual plans only).
- A claim that a risk "does not exist" when the search could not have found it.
- A "validated" baseline that was never checked on the quantity actually in dispute.
- A result that passes because two large errors cancel, hiding both.

## 5. Follow-up dossiers and addenda

- **Addenda** carry corrections and new measurements only, numbered continuously across addenda
  (items 1-9 in 01A, 10-14 in 01B, ...). See `verification.md`.
- **A follow-up question** gets a new dossier in a new folder (`--dossier 2`). Carry forward the
  facts that survived, the corrections, and the recommendation's open questions; do not carry
  forward any member's position as a premise.
- **When the user disagrees with the council**, that is a good reason for a follow-up dossier.
  Write the disputed verdict as a position to test and quote the user's objection verbatim.
