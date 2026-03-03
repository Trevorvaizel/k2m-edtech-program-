---
key: story-1.5.3
title: Build Bridge Section
epic: 1.5
status: ready-for-dev
priority: P0 (BLOCKING)
estimatedHours: 2-3

## User Story

As a visitor who has experienced emotional recognition through Constellation Zones,
I want to understand WHY "thinking matters more than tools" through the Five Whys demonstration,
So that I can intellectually understand the methodology before committing to the program.

## Context

**Strategic Purpose:** Convert emotional recognition (Constellation Zones) → intellectual understanding (thinking methodology)

**Foundation Impact:**
- Without Bridge: Intellectual Foundation 2/10, Conversion Foundation 4/10
- With Bridge: Intellectual Foundation 9/10, Conversion Foundation 9/10
- **Overall Epic 2 Readiness: 4/10 → 9/10 with Bridge**

**User Journey:**
- Hero (Emotional confusion validated) → Constellation Zones (Voice recognition) → Bridge (Methodology understanding) → Discord (Social proof) → CTA (Conversion)

**Bridge Position:** After Constellation Zones, before Discord section

**Strategic Analysis Finding:**
> "The Bridge is THE DIFFERENTIATOR. If you enter Epic 2 with users thinking 'tool training,' you lose. If they think 'habit transformation,' you win."

## Acceptance Criteria

### Given: Constellation Zones create emotional recognition
**When:** I create the Bridge section
**Then:**
- Bridge.html exists with complete HTML structure
- Bridge.css matches Constellation Zones visual theme (ocean mint accents)
- Bridge.js implements accordion interactions with GSAP
- Bridge positioned between Constellation Zones and Discord in main.js
- Scroll flow: Hero → Constellation Zones → Bridge → Discord → CTA

### Given: Bridge must explain the methodology
**When:** I add Bridge content
**Then:**
- **Hook** (3 lines):
  - "You just saw your voice."
  - "Here's the thing:"
  - "The leap isn't tools. It's thinking."
- **Five Whys Demo**:
  - Problem: "AI gives me garbage"
  - Why 1: → "I don't know what to ask"
  - Why 2: → "I'm not clear on my goal"
  - Why 3: → "I haven't structured my thinking"
  - Why 4: → "I jump straight to tools"
  - Why 5: → "Nobody taught me a framework"
  - Aha moment: "Aha. There it is."
- **Promise** (2 lines):
  - "We don't teach prompts."
  - "We install thinking habits."
- **CTA**:
  - "6 weeks. Zone 0 → Zone 4. One habit at a time."
  - "[Find Your Zone]" button

### Given: Visual design must match Constellation Zones
**When:** I create Bridge.css
**Then:**
- Spotlight reveal effect (radial gradient ocean-mint 0.03 opacity)
- Ocean-mint gradient text on "thinking" and "habits"
- Accordion styling:
  - Closed: Shows question only, subtle border
  - Open: Reveals answer with smooth height transition
  - Active: Ocean-mint left border accent
- Responsive design (mobile/desktop)
- Content max-width: 680px (readable)

### Given: Bridge must animate cinematically
**When:** I create Bridge.js
**Then:**
- GSAP ScrollTrigger reveals content progressively:
  - Hook text: Staggered line-by-line (0.2s between lines)
  - Five Whys: Accordion opens on scroll (why 1 → 2 → 3 → 4 → 5)
  - Promise: Fades in with scale (emphasis)
  - CTA: Pulse animation (draws attention)
- Only one accordion open at a time (exclusive expand)
- Smooth height animation: `height: 0 → height: auto`
- Lenis smooth scroll integrates with Bridge animations

### Given: Bridge completes the foundation
**When:** I validate Epic 2 readiness
**Then:**
- Emotional Foundation: 8/10 (Hero + ConstellationZones)
- Intellectual Foundation: 9/10 (Bridge implemented)
- Practical Foundation: 8/10 (Bridge demonstrates Five Whys)
- Conversion Foundation: 9/10 (Bridge connects to CTA)
- **Overall Epic 2 Readiness: 9/10 (READY)**

## Tasks

### P0 - Create Bridge Structure (BLOCKING)
- [ ] **Task 1.5.3.1:** Create Bridge.html
  - [ ] Create `/src/components/Bridge/Bridge.html`
  - [ ] Add section with Five Whys accordion
  - [ ] Each Why level expands/collapses to show explanation
  - [ ] Content structure: Hook → Five Whys → Promise → CTA
  - [ ] **Evidence:** HTML exists, semantic structure, accessible markup

- [ ] **Task 1.5.3.2:** Create Bridge.css
  - [ ] Create `/src/components/Bridge/Bridge.css`
  - [ ] Match Constellation Zones visual theme (ocean mint accents)
  - [ ] Accordion styling (closed, open, active states)
  - [ ] Spotlight reveal effect (radial gradient ocean-mint 0.03 opacity)
  - [ ] Responsive design (mobile/desktop)
  - [ ] **Evidence:** Styles match Constellation Zones, accordion animations smooth

- [ ] **Task 1.5.3.3:** Create Bridge.js
  - [ ] Create `/src/components/Bridge/Bridge.js`
  - [ ] Implement accordion open/close with GSAP
  - [ ] Only one accordion open at a time (exclusive expand)
  - [ ] Smooth height animation: `height: 0 → height: auto`
  - [ ] Ocean mint accent on active accordion
  - [ ] ScrollTrigger for accordion animations (as user scrolls through Bridge)
  - [ ] **Evidence:** Accordion opens/closes smoothly, no layout shift

- [ ] **Task 1.5.3.4:** Integrate Bridge into main.js
  - [ ] Import Bridge HTML/CSS/JS in main.js
  - [ ] Position Bridge between Constellation Zones and Discord
  - [ ] Verify scroll flow: Hero → Constellation Zones → Bridge → Discord → CTA
  - [ ] **Evidence:** Bridge renders in correct position, scroll transitions smooth

### Validation
- [ ] **Task 1.5.3.5:** Validate Epic 2 readiness
  - [ ] Review strategic analysis checklist:
    - [x] Emotional Foundation: 8/10 (Hero + Constellation Zones)
    - [ ] Intellectual Foundation: 9/10 (Bridge implemented)
    - [ ] Practical Foundation: 8/10 (Bridge demonstrates Five Whys)
    - [ ] Conversion Foundation: 9/10 (Bridge connects to CTA)
  - [ ] Overall Epic 2 Readiness: 9/10 (READY)
  - [ ] **Evidence:** Strategic analysis validates all foundations at 8+/10

- [ ] **Task 1.5.3.6:** Test Bridge interactions
  - [ ] Test accordion open/close on desktop
  - [ ] Test accordion open/close on mobile
  - [ ] Verify ScrollTrigger animations fire at correct scroll positions
  - [ ] Verify only one accordion open at a time
  - [ ] **Evidence:** All interactions work smoothly, no bugs

## Dev Agent Record

### Bridge Section Content Strategy
The Bridge explains "Why thinking > tools" using Five Whys:
1. Problem: "AI gives me garbage"
2. Why 1: "I don't know what to ask" (symptom)
3. Why 2: "I'm not clear on my goal" (deeper)
4. Why 3: "I haven't structured my thinking" (root cause)
5. Why 4: "I jump straight to tools" (behavior)
6. Why 5: "Nobody taught me a framework" (education gap)
7. Aha moment: "Aha. There it is." (epiphany)

This connects:
- **Hero's emotional validation** ("You're not alone")
- **Constellation Zones' recognition** ("Here's your voice")
- **Bridge's intellectual understanding** ("Here's the method")
- **CTA's conversion** ("Find Your Zone")

### Visual Design System
Bridge reuses Constellation Zones visual language:
- Ocean-mint gradient text: Same CSS variables
- Spotlight reveal: Same radial gradient system
- Accordion styling: Matches zone card styling
- Typography: Same Space Grotesk (headings) + Inter (body)
- Background: Pure black (#000000) matching theme

### Animation Choreography
Bridge uses GSAP ScrollTrigger for cinematic reveals:
1. Hook fades in (line 1 → line 2 → line 3)
2. Five Whys accordion opens sequentially (why 1 → 2 → 3 → 4 → 5)
3. Promise fades in with slight scale (emphasis)
4. CTA pulses (draws attention)
5. User scrolls to CTA or clicks

Total scroll duration: ~30-40 seconds to read and absorb

### Differentiation Strategy
Bridge directly addresses competitive positioning:
- **What others do:** "Learn 50 prompts!" "Master these tools!"
- **What K2M does:** "We don't teach prompts. We install thinking habits."
- **Why it matters:** Tools expire, habits last. Frameworks adapt, tricks don't.

**Market Position After Bridge:**
- NOT: "Another AI course"
- BUT: "Thinking framework program"

## Definition of Done

- [x] Story reviewed and accepted by product owner
- [x] Bridge design specified in strategic analysis
- [ ] All P0 tasks completed:
  - [ ] Bridge.html created with Five Whys accordion
  - [ ] Bridge.css matches Constellation Zones visual theme
  - [ ] Bridge.js implements accordion interactions
  - [ ] Bridge integrated into main.js in correct position
- [ ] Epic 2 readiness validated at 9/10
- [ ] All interactions tested (desktop + mobile)
- [ ] Code committed to git with clear commit message
- [ ] Story marked as completed in sprint status

## Related Stories
- **Story 1.5.2:** "Fix Constellation Zones Mobile Layout" - Prerequisite
- **Story 1.5.4:** "Add Accessibility & Reduced Motion" - Follow-up
- **Story 1.5.5:** "Validate Foundation & Epic 2 Readiness" - Next step

## References
- Strategic Analysis: `/_bmad-output/implementation-artifacts/mirror-zones-strategic-analysis.md`
- Bridge Spec: Lines 123-223 in strategic analysis
- Competitive Analysis: Lines 227-249 in strategic analysis
- Epic 2 Readiness Scorecard: Lines 319-330 in strategic analysis
