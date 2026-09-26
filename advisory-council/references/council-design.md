# Council design: seats, sizes and weights

Read when choosing who sits on the council for a decision, how many seats, and how to weight them.

## Contents

1. Principles
2. How many seats
3. Seats every council needs
4. Seat menus by domain
5. Weights and grouped votes
6. Proposing a council in one message
7. Changing the council between sessions

## 1. Principles

- **A seat earns its place by changing the analysis, not the prose.** Pick seats whose mandate
  and incentives would lead them to different conclusions or to look at different evidence. Two
  seats that would argue the same way from the same facts are one seat.
- **Seat constituencies, not job titles for their own sake.** Ask who gains, who pays, who
  operates, who can block, who is harmed quietly, and who competes. Each answer is a candidate.
- **Include the party nobody thought of.** In the first use of this method the most valuable
  finding came from a seat added late, at the user's suggestion, for a constituency the original
  roster missed. Before confirming, ask: who is affected by this decision and has no seat?
- **Missing perspectives cost more than extra ones.** The same run repeatedly stalled on a
  business question no technical seat could answer (a product owner was missing), and the
  council itself said several times that it needed a lawyer. Check the roster against the
  questions in the dossier: every question should have at least one seat able to answer it.

## 2. How many seats

| Voting seats | Use for |
|---:|---|
| 3-4 | A narrow decision with few affected parties, or a quick first pass |
| **5-7** | **The default.** Enough spread to disagree, few enough that every seat is distinct |
| 8-9 | Many distinct constituencies (policy, platform, regulated markets) |
| 10+ | Avoid. The first run seated fifteen; an audit found about six did distinct work |

Five was chosen in the original method because it "gives proper weight to all the parties
actually involved" and makes a genuine split possible; with three, a split is too easy to paper
over.

## 3. Seats every council needs

1. **The seat whose interest is in not doing the work.** It argues for "do nothing", "do less" or
   "do it later", and counts the cost of support, distraction and opportunity. A council without
   it is a rubber stamp. In the first run this seat forced a business question no one else asked
   and produced a trigger-and-reversion plan nobody else proposed.
2. **The seat for the party with the least voice.** End users with no buyer power, the people who
   maintain what gets built, affected communities, the customer segment that churns quietly.
3. **A seat with an inverted priority ordering.** Most seats rank "fails loudly" above "is
   quietly wrong". A safety, compliance, trust or finance seat often ranks the other way: it
   would rather stop than ship something silently wrong. That inversion surfaces risks the others
   rank low.
4. **The persona-free verifier** (not a voting seat): no mandate, no incentives, checks facts.

## 4. Seat menus by domain

Pick from these, then adapt titles to the user's market. Groups are for the roster table.

### Business and product

| Group | Seats |
|---|---|
| Leadership (C-suite) | CEO or general manager; CFO; CTO or head of engineering; CMO or head of growth; COO or head of operations; chief product officer; head of sales; head of customer success or support; chief people officer |
| Governance | Independent board member; board chair; investor board member (venture or private equity); audit or risk committee chair |
| Capital markets and critics | Activist investor; short-seller or sceptical analyst; industry journalist; consumer advocate |
| Customers and market segments | Early adopter; mainstream buyer; price-sensitive buyer; enterprise economic buyer; enterprise end user; churned customer; non-customer who chose an alternative; a segment in another geography |
| Competitors (archetypes) | Market-leading incumbent; low-cost challenger; well-funded start-up; adjacent platform that could bundle the feature; open-source or free alternative |
| Partners and supply | Channel partner or reseller; key supplier; platform or app-store owner; integration partner; insurer or financier |
| Oversight | Sector regulator; data-protection authority; competition authority; standards body; general counsel |
| Inside the company | Front-line staff who will operate or sell it; engineering team who will maintain it; finance or billing operations |
| Experts | Domain expert; pricing specialist; security or privacy specialist; accessibility specialist; economist |

### Engineering and technical

| Group | Seats |
|---|---|
| Delivery | Tech lead or architect; delivery or programme manager; product owner |
| Operations and safety | Site reliability or operations engineer; security engineer; safety engineer (hazard analysis); QA or test lead |
| Upstream | Maintainers of a dependency the change touches (how they review, where the project is heading, the CI bar) |
| Host platform | The platform or runtime the work ships inside (its gatekeepers, build system, compatibility rules) |
| Consumers | The largest downstream consumer; safety-critical or regulated consumers; end users; people who author content on top of it |
| Governance | Licensing and legal; fork and contribution governance; finance (run cost) |

### Public policy

| Group | Seats |
|---|---|
| Affected people | Two or three distinct affected communities (by region, income, age, disability, business size) |
| Government | Implementing agency; treasury or budget office; enforcement body; local government |
| Opposition and critics | Opposition spokesperson (as a role); civil-liberties advocate; think-tank sceptic |
| Economy | Affected businesses, small and large; trade union or workers' representative; independent economist |
| Law | Constitutional or administrative lawyer (flags issues; refer real legal questions to counsel) |

### Research

| Group | Seats |
|---|---|
| The team | Principal investigator; early-career researcher doing the work |
| Method | Statistician or methodologist; replication specialist; data manager |
| Review | Sceptical peer reviewer; journal editor; ethics board |
| Money and use | Funder; practitioners who would use the results; industry partner |
| Field | Competing lab (archetype); expert from an adjacent field |

## 5. Weights and grouped votes

- **Default: every voting seat has weight 1.** The tally always reports headcount and weighted
  count side by side, so weighting is visible and can be challenged.
- **Weight a seat up** when its constituency bears most of the consequence (customers of a
  pricing change, the regulated party in a compliance decision). Keep any seat to at most twice
  the lightest one, or the council becomes one voice with an audience.
- **Grouped votes.** The original method used five teams of three, each team agreeing internally
  and casting one vote. To reproduce that, give each team member weight 1/3 (for example
  `--seat cfo:CFO:Leadership:0.333`). Prefer single seats unless a group really would split
  internally.
- **Weight 0** seats an observer: it writes Round 1 and Round 2 reports but does not vote.
  `council.py init` writes no round files for weight-0 seats; add them by hand if wanted.

## 6. Proposing a council in one message

When the user gives little detail, do not send a questionnaire. Send one short message like this
and act on the reply:

```
Proposed council for: <decision, with "do nothing" as an option>
Market: <segment, geography>. Goal: <measure>. Folder: council/

| Seat | Why it is here |
|---|---|
| CFO | Owns the cash and payback case |
| Mainstream customer (small business) | Pays the price; weight 2 |
| Churned customer | Knows why people leave |
| Low-cost challenger (competitor archetype) | How the market answers |
| Consumer advocate | Argues against doing it at all |
| Head of support | Lives with the consequences |
+ a persona-free verifier who checks facts and does not vote.

Reply "go", or add, remove or re-weight seats. Anything I should know that is not public
(numbers, constraints, a leaning you want tested)?
```

## 7. Changing the council between sessions

- After the tally, look at section E (what each seat added). A seat that added nothing distinct
  should be replaced next time by a missing perspective, not kept for balance.
- For a follow-up question to the same council, start a new folder with
  `council.py init NEW_FOLDER --roster OLD_FOLDER/council.json --dossier 2 --title ...`, so the
  dossier and addendum numbers stay unique across sessions.
