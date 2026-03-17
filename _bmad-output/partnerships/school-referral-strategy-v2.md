# K2M School Referral Strategy — v2 (Hardened)

**Date:** 2026-03-11
**Author:** Dr. Quinn (Creative Problem Solver) + Trevor
**Status:** Ready for implementation
**Supersedes:** Initial nominee list collection approach

---

## Origin: What Broke and Why

The original approach asked school contacts to collect and share parent email lists — nominating students on K2M's behalf. During outreach calls, schools were non-committal, delayed, and when pressure was applied, one contact cited the **Data Protection Act**.

### Root Cause Analysis

The anger and legal citation were not the real problem. They were the name the contact gave to a discomfort that existed from the moment the request arrived. The school contact was being asked to:

- Collect and transfer **parent personal data** to an unknown third party
- Do so without a formal institutional relationship with K2M
- Bear the **legal and reputational liability** if a parent later asked "who gave you my contact?"

> **The assumption that failed:** *"The school is a safe intermediary to route parent data through."*
>
> It never was. The strategy placed the wrong kind of burden on the wrong person.

---

## The Revised Strategy: Schools Announce, Parents Opt In

### Core Principle

> Remove the school as a data custodian. Make their role purely one of endorsement and access. Parents self-refer with consent built in from the first interaction.

---

## The Revised Flow

```
Outreach call → Sign Activation Agreement (name the Coordinator)
        ↓
Coordinator adds K2M WhatsApp contact to parent group (30 seconds)
        ↓
K2M sends engineered message directly into the group
        ↓
Parents reply with child's name + their WhatsApp number (opt-in)
        ↓
K2M follows up directly with opted-in parents (warm leads)
        ↓
Support call to Coordinator: "How's response looking? Want us to send a follow-up?"
        ↓
School receives certificate + personal acknowledgment letter
```

---

## Change 1 — MOU → Activation Agreement with Named Coordinator

**The problem with the old MOU:** Signed by the principal, no specific action owner. The right person never knew it existed.

**The fix:** The Activation Agreement names a **School Coordinator** — the specific person responsible for one action only:

> *Adding K2M's WhatsApp contact to the parent group they already manage.*

That is their entire obligation. 30 seconds. No data handling. No liability.

K2M sends the message directly — the coordinator never touches the content, never transfers data, never bears any legal exposure.

### What the Activation Agreement Contains
- School name and principal signature
- Named coordinator (name + role + WhatsApp)
- One stated obligation: add K2M to the parent group
- K2M's obligation: deliver the program to selected students, acknowledge the school publicly
- Validity period (e.g., Cohort 2 window: [dates])

---

## Change 2 — The Message Does the Heavy Lifting

K2M sends a crafted message into the parent WhatsApp group. The message is engineered for response, not just awareness.

### Template

```
Hi [School Name] parents 👋

[School Name] has partnered with K2M EdTech to offer
selected Form 3 & 4 students a fully funded tech skills
program this term.

Only 3 spots are reserved for your school.

If your child is interested, reply to this message with:
👉 Your child's name + your WhatsApp number

We'll reach out within 24 hours.

— [K2M Caller Name] | K2M EdTech
[Phone number]
```

### Why This Works
| Element | Function |
|---|---|
| School name in opening | Social proof — endorsed by their institution |
| "Fully funded" | Removes cost as an objection immediately |
| "3 spots reserved" | Scarcity — creates urgency without pressure |
| Reply with name + number | Lowest possible barrier — no form, no link, no drop-off |
| Human name + number | Builds trust — a person, not a brand |

---

## Change 3 — WhatsApp-First Funnel (No Forms)

**The problem with QR codes and forms:** Parents scan, see a form, close it. Drop-off is built into the architecture.

**The fix:** Parents reply directly to the WhatsApp message. The opt-in happens in the reply itself.

K2M receives:
- Parent's name
- Child's name
- A WhatsApp number they actively chose to send

The follow-up call is now **warm** — the parent already raised their hand. Conversion rate is fundamentally different.

---

## Change 4 — Caller Role Completely Rebuilt

**The old caller role:** Chase schools for lists → apply pressure → trigger defensiveness → Data Protection Act.

**The new caller role:** Two modes only.

### Mode 1 — Activation Call
*Trigger: School has signed agreement but hasn't added K2M to parent group yet*

> "Hi [Coordinator name], it's [Caller] from K2M. We just need you to add this number to your parents' WhatsApp group — it takes about 30 seconds. Do you want to do it now while we're on the call?"

Walk them through it in real time. Done.

### Mode 2 — Support Call
*Trigger: School has activated, checking in on response*

> "Hi [Coordinator], just checking in — how many parents have replied so far? We can drop a follow-up message into the group if response has been slow, just let us know."

### What Was Removed From the Script
- Any ask for parent data or email lists
- Any deadline pressure applied by the caller
- Any language that implies the school owes K2M something

> Pressure is structurally impossible — there is nothing to chase, only someone to support.

---

## Change 5 — Recognition Must Be Physical and Personal

**The problem with digital recognition:** "We'll list your school on our website" has no perceived value. It doesn't sit in a frame on a wall.

**The fix:** Two tangible artifacts delivered after the activation window closes:

### Artifact 1 — Partner School Certificate
A physical framed certificate delivered to the school:

> *"Official K2M Partner School — Cohort 2, 2026"*

Signed by the K2M founder. Designed to be displayed.

### Artifact 2 — Personal Acknowledgment Letter
A letter addressed specifically to the coordinator, from the K2M founder, acknowledging their name and their role in the students' outcomes.

> This is social currency that matters in a school environment. It's something they can show their principal, their peers, their appraisal review.

---

## Pre-Mortem: Five Failure Modes and Their Mitigations

| Failure Mode | Mitigation Built Into Strategy |
|---|---|
| MOU signed but wrong person acts | Agreement names specific coordinator + their one action |
| Message ignored in noisy group | Engineered message: school name, scarcity, human sender, reply-based CTA |
| Form/link abandoned | No form. Parents reply directly to WhatsApp message |
| Callers revert to pressure-based follow-up | Old ask removed from script entirely. Two support-mode scripts only |
| Recognition feels hollow | Physical certificate + personal named letter, not website listing |

---

## What Was Removed Entirely

| Removed Element | Reason |
|---|---|
| Asking schools for parent email lists | Root cause of the Data Protection objection |
| QR codes and external forms | Drop-off point, unnecessary friction |
| Pressure-based follow-up calls | Triggered the exact defensive reaction encountered |
| Generic "partner school" recognition | No perceived value, no enforcement leverage |

---

## Implementation Checklist

- [ ] Draft and finalise Activation Agreement template (with coordinator name field)
- [ ] Write 3 WhatsApp message variants (A/B test scarcity vs. aspiration hook)
- [ ] Rebuild caller script — activation mode + support mode only
- [ ] Design Partner School certificate (print-ready)
- [ ] Draft personal acknowledgment letter template (founder-signed)
- [ ] Set up WhatsApp number for inbound parent replies
- [ ] Define follow-up cadence for warm leads (parent replied)
- [ ] Define activation window per school (open/close dates)

---

## Connection to Playbook v2

This strategy feeds the **School Referral Channel** in the Cohort v2 playbook. It replaces the nominee list collection method and integrates with the enrolment funnel at the point where warm leads (parent opt-ins) are handed to the enrolment team.

See also:
- [k2m-pioneer-school-partnership-script.md](k2m-pioneer-school-partnership-script.md) — original outreach script (to be updated)
- [school-referral-strategy.md](school-referral-strategy.md) — prior version of this document
