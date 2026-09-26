# Worked example: a complete council session

Read when you want to see a complete session: every file the method produces, filled in, in the
order they were written.

**Scenario.** Fennick Home, a fictional 40-person maker of a Wi-Fi water-leak sensor (49, sold
online and through two retail partners in the UK, Ireland, the Netherlands and Belgium), asks
whether remote phone alerts, free today, should become a 3.50-a-month subscription for new
customers from spring 2027. Six voting seats (a CFO, a home owner with weight 2, a small landlord,
an insurance partner, a competitor-perspective platform archetype and a consumer advocate) and a
persona-free verifier ran in parallel mode. The dossier carried deliberate and accidental errors;
members and the verifier caught them, the CEO's leaning (option A) drew no vote, and the council
recommended a staged alternative (option C, 5 of 6 seats, weighted 6 of 7) with the insurer
dissenting.

| # | File | Lines | What it shows |
|---:|---|---:|---|
| 1 | `COUNCIL.md` | 198 | The decision, the roster with weights, and one persona card per seat |
| 2 | `DOSSIER-01-alert-subscription.md` | 119 | Facts with sources, estimates with methods, unknowns with where searched, the CEO's leaning as a position to test |
| 3 | `ROUND1-cfo.md` | 52 | Payback and break-even model; pre-declares the take-up and churn results that would move it |
| 4 | `ROUND1-homeowner.md` | 54 | The buyer's view: a siren in an empty house protects nothing; the silent expired-card failure |
| 5 | `ROUND1-landlord.md` | 56 | Per-device pricing against a portfolio; the tenant's Wi-Fi problem |
| 6 | `ROUND1-insurer.md` | 56 | Pay per sensor online and alerting, not per unit sold |
| 7 | `ROUND1-platform.md` | 60 | A competitor archetype reasoning from public-type information, not a real company |
| 8 | `ROUND1-advocate.md` | 55 | The seat against the change, arguing its case at full strength |
| 9 | `VERIFICATION.md` | 63 | 65 of 65 claims checked, verdicts, the four-group summary |
| 10 | `ADDENDUM-01A.md` | 145 | Eleven corrections with "found by", open items, a disagreement recorded without adjudication |
| 11 | `ROUND1-TALLY.md` | 119 | Positions, agreement on action versus reasons, splits, a redundant-seat flag, options A-D |
| 12 | `ROUND2-cfo.md` | 41 | The one changed vote, naming the addendum items that changed it |
| 13 | `ROUND2-homeowner.md` | 41 | Round 2 vote answering other seats by id |
| 14 | `ROUND2-landlord.md` | 39 | Round 2 vote with a portfolio-pricing condition |
| 15 | `ROUND2-insurer.md` | 37 | The minority vote, with its dissent stated at full strength |
| 16 | `ROUND2-platform.md` | 43 | Accepts corrections to its own Round 1 figures |
| 17 | `ROUND2-advocate.md` | 43 | Conditional vote; records the dissent it would carry if D were adopted |
| 18 | `RECOMMENDATION.md` | 100 | Start here for the outcome: vote, dissent, risks, next steps with results that would change the decision, limits |
| - | `council.json` | 46 | The roster `council.py` reads |

Planted dossier errors: a price table mixing a yearly price into a monthly column; a pilot
figure from the best of four cohorts; a churn figure true only for annual billing; two country
rows swapped. Members also found errors that were not planted (a supplier rise applied to the
whole cost, a year-end denominator); the swapped rows, the insurer's missing conditions and an
unread checkout measurement were found only by the verifier.

**Everything here is fictional.** The company, its partners, every seat and every number are
invented for this example. No real law, regulator's rule, market statistic or company is
described; legal questions are left for qualified counsel, as the method requires.
