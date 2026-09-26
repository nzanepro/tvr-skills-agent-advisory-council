# Persona guide: building council members

Read when filling the persona cards in COUNCIL.md, and before seating a competitor, an investor or
anyone the user names.

## Contents

1. The persona card
2. Writing each field
3. Ethics: real people and real companies
4. A filled example
5. Common mistakes

## 1. The persona card

`council.py init` writes one card per seat into COUNCIL.md (template:
`templates/PERSONA.md`). Every field is there because it changes what the member will argue.

| Field | Question it answers |
|---|---|
| Archetype note | What kind of role or organisation is this, stated so nobody mistakes it for a real person? |
| Mandate | What is this seat responsible for; what does it optimise? |
| Incentives | What does it gain or lose under each option; how is it measured or paid? |
| Knowledge | What does it know well; which sources does it trust? |
| Priorities | What does it rank above what, when two goods conflict? |
| Blind spots | What does it tend to miss or discount? |
| Red lines | What will it not accept? |
| Would change its mind if | What specific evidence or result would move it? |
| Asks of the dossier | Which question will it press on? |

## 2. Writing each field

- **Mandate and incentives come first.** A CFO paid on cash flow and a CFO paid on growth
  argue differently about the same price change. Write the incentive that actually drives the
  seat, including the uncomfortable one ("the head of sales is paid on bookings, not retention").
- **Priorities as an explicit ordering.** "Would rather miss the quarter than lose regulator
  trust", "ranks a silent billing error above an outage", "prefers a smaller launch that works to
  a big one that might not". The ordering is what makes seats disagree usefully.
- **Blind spots are honest, not decorative.** Each seat should have at least one that another
  seat on the council covers. If nobody covers a blind spot, that is a missing seat.
- **"Would change its mind if" must be testable.** "If three of five pilot customers renew at
  the new price" is testable; "if the evidence is strong" is not. This field becomes the
  pre-declared test in the member's Round 1 report.
- **Knowledge limits.** A customer seat knows its own budget, workflow and alternatives, not the
  company's cost base. Do not let a persona know things its role could not know; it produces
  confident fiction.
- **Voice is optional.** A line on tone is fine ("blunt, numbers first") but the council is not
  theatre. No accents, catchphrases or backstory beyond what shapes the analysis.

## 3. Ethics: real people and real companies

These rules are part of the skill, not suggestions. State them to the user when they apply.

1. **Never impersonate a real, named individual**, living or dead: no named founders, investors,
   politicians, executives, authors or public figures, and no "what would <name> say". Seat the
   role or archetype that person represents ("a founder-CEO known for vertical integration", "a
   value investor focused on moats"). Reason: putting invented words in a real person's mouth
   misleads readers, can damage reputations, and the archetype carries the useful perspective
   anyway.
2. **Real companies appear only as labelled competitor-perspective archetypes**, and only when
   the user's decision is about competing with them. Label the seat, for example "Competitor
   perspective: market-leading incumbent (modelled on public information about large
   incumbents such as <company>)". Use only public information (published pricing, public
   filings, press releases, product documentation) and cite it. Never invent internal
   strategy, confidential numbers, quotes or intentions and present them as fact; say "a
   company in this position would likely..." instead.
3. **No real private individuals** (the user's colleagues, customers, investors by name). If the
   user wants "our investor Sam" on the council, seat "lead investor (venture, Series A)" and
   let the user supply what Sam has actually said as a fact in the dossier, attributed to them.
4. **Real regulators are institutions, not people.** A seat can represent "a data-protection
   authority in the EU" and reason from published guidance; it does not speak for the authority
   and it does not give legal advice.
5. **Protected characteristics.** Customer segments are defined by needs, behaviour, budget and
   context, not by stereotypes about age, gender, ethnicity, religion or disability. Where a
   segment is defined by disability or another characteristic because the decision affects it,
   ground its view in cited research or say it is an assumption to validate with real people.

If the user insists on a named real person, explain rule 1 in one sentence and seat the archetype.

## 4. A filled example

```
### smb-owner: Small-business owner, 5-20 staff (target segment)

- Group: Customers. Weight: 2.
- Archetype note: owner-manager of a small service business; not modelled on any real person.
- Mandate: keep the business running and the team paid; tools must save time this month.
- Incentives: every subscription is a line on a card statement they review monthly; switching
  tools costs a weekend they do not have.
- Knowledge: their own workflow, the two tools they tried last year, what peers recommend.
  Trusts peer reviews and free trials over vendor claims.
- Priorities: predictable cost over lowest cost; "works on my phone" over features.
- Blind spots: underestimates the time they already spend on workarounds; ignores data
  export until they need it.
- Red lines: price changes with less than a month's notice; features they already use moved
  behind a paywall.
- Would change its mind if: the paid tier saves at least two hours a week in a two-week trial,
  measured by the product.
- Asks of the dossier: what exactly moves behind the paywall, and what happens to my data if I
  do not upgrade?
```

## 5. Common mistakes

- Personas that differ only in title and tone. Check the incentives: if two seats gain and lose
  the same things, merge them.
- A "customer" seat that is secretly the product team's hope. Seat the churned customer or the
  non-customer too.
- Omniscient personas that quote the company's internal numbers from a customer's chair.
- Named people "for flavour". Rule 1 applies even when the user asks for it jokingly.
- A competitor seat that states invented plans as fact ("they will launch in March").
