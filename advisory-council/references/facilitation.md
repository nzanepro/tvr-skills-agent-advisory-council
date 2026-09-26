# Facilitation: against groupthink, sycophancy and anchoring

Read before convening a council, when the result looks too tidy, or when the user pushes for a
particular answer.

## Contents

1. The facilitator's job
2. Rules that protect independence
3. Rules against sycophancy
4. Rules for evidence
5. Failures seen in the method's first use
6. What made the council useful
7. Before the recommendation: a smell test

## 1. The facilitator's job

The facilitator (the agent running the skill) owns the process, not the answer: it frames the
decision, seats the council, writes the dossier, publishes corrections, writes the tally and the
recommendation. Its own view is one more position to test. It never votes.

## 2. Rules that protect independence

1. **Independent, then informed.** Round 1 members read only COUNCIL.md, the dossier and addenda.
2. **Hold votes in escrow.** Positions stay in the round files. They never go into the dossier,
   an addendum or another member's brief.
3. **No synthesis before every vote is in.** A synthesis written early, placed in a document that
   "wins", and framed as the convergence of independent lines is advocacy, even when its content
   is right.
4. **Options, not verdicts.** The tally offers lettered options with who backs each; it does not
   claim any option satisfies every member.
5. **Keep raw reports.** Summaries lose attribution: in the first use, only digests survived and
   most seats became indistinguishable from their teammates in the record.
6. **Members can read each other in Round 2.** Two seats in the first use could not read their
   teammates' work and so could not converge; deposit every report in the folder as it lands.

## 3. Rules against sycophancy

1. **Do not tell members what the user wants** except as a labelled position to test.
2. **Seat the contrarian.** One seat argues against doing the work at all.
3. **Ask members to find the dossier's errors.** It turns agreement-seeking into error-seeking.
4. **A changed vote names its cause.** "Persuaded by the discussion" is not a reason; "the CFO's
   payback table in ROUND1-cfo §3" is.
5. **Dissent is carried at full strength.** The recommendation states each dissent as its holder
   would, with what would prove it right. Never paraphrase a dissent into a caveat.
6. **Do not grade the user's idea generously.** If the council says the user's preferred option
   is weak, the recommendation says so in its first lines. If the user disagrees with the
   recommendation, offer a follow-up dossier that tests their objection, rather than rewriting
   the recommendation to please them.
7. **No urgency framing**, in the dossier or the briefs: "the only thing between us and
   launch", "this is settled", "the user is exhausted". Constraints are facts; pressure is not.

## 4. Rules for evidence

1. **Evidence beats argument.** A member that checks a source or runs an analysis does more for
   the decision than one that argues well. Say so in the brief.
2. **Pre-declare tests.** For any proposed experiment, pilot or research step, state before it
   runs what result would change the decision.
3. **Translate into the decision's currency.** A 3% error in a model input means little until
   it is expressed as what the customer pays, what the company earns, or what the user
   experiences, and compared with ordinary variation (seasonal swings, price noise). In the first
   use, the disputed error turned out to be smaller than one ordinary day's variation in the
   end product, which settled a long argument.
4. **Assert the denominator.** Any count ("12 of 15 competitors charge monthly") says how many
   were examined and how they were chosen.
5. **Verified absent vs never reached.** A search that found nothing proves nothing unless it
   could have found the thing.
6. **The dangerous failures look like success.** A check that returns "no problems" while
   checking nothing, a green metric that passes by cancellation, a survey with no respondents
   from the segment in question. Assume that is the default failure mode and design against it.

## 5. Failures seen in the method's first use

All of these happened and all are designed out above:

| Failure | Guard |
|---|---|
| An addendum embedded one team's votes as shared fact | Addenda hold corrections only; `check` enforces it |
| A synthesis written before all teams voted, placed in the winning document | Tally only after all Round 1 reports; options not verdicts |
| Urgency framing ("the only thing between this and completion", "settled by measurement") | Framing rules in the dossier guide |
| Only facilitator digests archived; per-seat attribution lost | Raw reports are the record |
| No verifier; dossier errors reached the vote | Persona-free verifier every time |
| Fifteen seats, about six did distinct work | 5-7 seats; tally section E flags redundant seats |
| Missing constituencies (product owner, the people who build on the output, a lawyer) | Seat checklist in `council-design.md` |
| Dossier errors every round: mixed baselines, wrong-case numbers, favourable point only, mislabelled rows | Members check the dossier; verifier checks labels and baselines |
| A question that was mis-posed; several seats said so independently | Members may re-pose the question; the tally records it |

## 6. What made the council useful

- Members **found things no single reviewer would have**: a design proposal buried in comments
  nobody read past the first post; a measurement that overturned a policy debate; a tool that was
  already installed; a public example of a competitor doing exactly the risky thing under debate.
- **The seat against doing the work** forced a business question to the decision owner that no
  other seat could answer.
- **The safety-minded seat reframed** an inventory as a missing risk analysis and found problems
  no other method reached.
- **Several seats measured instead of arguing**, and settled more questions that way than the
  argument did.
- **Splits did not block decisions** when the tally showed the action did not depend on them.

## 7. Before the recommendation: a smell test

- Did every seat make at least one point no other seat made?
- Did the contrarian seat argue its case, and is its dissent in the recommendation at full strength?
- Did any vote change without a named cause?
- Is every load-bearing number in the recommendation CONFIRMED, or labelled otherwise?
- Would the recommendation read the same if the user had wanted the opposite answer?
- Does the recommendation say what real-world check (customers, counsel, data) comes next?

If any answer is no, fix it before reporting.
