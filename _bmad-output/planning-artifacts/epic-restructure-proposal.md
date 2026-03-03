# Epic Restructure Proposal

**Date:** 2026-01-19
**Type:** Strategic Epic Reorganization
**Status:** PROPOSED
**Rationale:** Align epics with actual implementation (ConstellationZones) and strategic analysis (Foundation BEFORE Epic 2)

---

## PROBLEM

**Current Epic 2 (Obsolete):**
- Title: "Territory Map WHOA Moment"
- Scope: Particle coalescence (200 desktop, 50 mobile)
- Reality: Doesn't exist - TerritoryMap abandoned

**Actual Implementation:**
- Hero section (deep-mirror-v2 hybrid)
- ConstellationZones (star fields + voice cards) - NOT TerritoryMap
- Bridge section - NOT implemented yet

**Strategic Analysis Finding:**
- ConstellationZones + Bridge = "Foundation FOR Epic 2"
- NOT "PART OF Epic 2"
- Epic 2 readiness: 4/10 without Bridge, 9/10 with Bridge

---

## PROPOSED SOLUTION: Path B (Strategic Alignment)

### New Epic Structure

**Epic 0:** Conversion Foundation & Success Metrics (UNCHANGED)
**Epic 1:** Foundation & Hero Experience (UNCHANGED)
**Epic 1.5:** **[NEW]** Recognition to Understanding Foundation
**Epic 2:** **[REDEFINED]** Habit Installation & 6-Week Journey
**Epic 3:** Community Preview & Conversion (renumbered from Epic 3)
**Epic 4:** Graceful Degradation & Post-Launch (renumbered from Epic 4)

---

## EPIC 1.5: Recognition to Understanding Foundation

**Purpose:** Visitors experience emotional recognition through voice resonance (Constellation Zones), then intellectual understanding through the Bridge (Five Whys methodology), creating complete foundation for transformation.

**Strategic Foundation:**
- Act 1: The Mirror (Recognition) - Constellation Zones
- Act 2: The Method (Bridge) - Five Whys
- **Outcome:** 9/10 Epic 2 readiness

### Story 1.5.1: Implement Constellation Zones Structure

As a visitor,
I want to see 5 constellation zones with star fields and voice cards,
So that I can experience emotional recognition and identify which voice resonates with me.

**Acceptance Criteria:**

**Given** the Hero section is complete
**When** I create `/src/components/ConstellationZones/ConstellationZones.html`
**Then** 5 zones exist with:
  - Star field background (150 stars desktop, 50 mobile)
  - Constellation lines connecting thought-stars
  - Voice nebula card with zone name and quote
  - Zone 0: "AI isn't for me" (Orionis Confusio)
  - Zone 1: "I could try this" (Primus Spes)
  - Zone 2: "AI does tasks for me" (Tertius Operor)
  - Zone 3: "AI understands my intent" (Quartus Collaboratio)
  - Zone 4: "I control the quality" (Quintus Dominus)

**Given** I need constellation styling
**When** I create `/src/components/ConstellationZones/ConstellationZones.css`
**Then** zones have:
  - Ocean-mint glow on stars and lines
  - Voice nebula card with radial gradient
  - Zone 4 accent with warm ocean-mint
  - Responsive design (mobile/desktop)

**Given** I need scroll-based animations
**When** I create `/src/components/ConstellationZones/ConstellationZones.js`
**Then** GSAP ScrollTrigger activates zones as user scrolls
**And** stars reveal with stagger (0.2s between stars)
**And** constellation lines draw with stroke-dashoffset animation
**And** voice nebula fades in with scale

**FRs covered:** (Emotional recognition - new FR)
**Estimated Time:** 4 hours

---

### Story 1.5.2: Fix Constellation Zones Mobile Layout

As a visitor on mobile,
I want to see constellation zones with stars clearly positioned above and below the nebula card,
So that I can experience the same emotional impact as desktop users.

**Acceptance Criteria:**

**Given** Constellation Zones work on desktop
**When** I fix mobile CSS media query
**Then** `@media (max-width: 768px)` applies correctly
**And** stars position at:
  - 10-30% from top (above nebula)
  - 70-90% from top (below nebula)
**And** nebula has `max-width: 85%` on mobile
**And** no horizontal scrolling occurs

**Given** mobile performance is critical
**When** I optimize star count
**Then** desktop: 150 stars
**And** mobile: 50 stars (via `isMobile()` check)
**And** performance test shows 45fps+ on mobile

**Given** visual quality matters
**When** I run Playwright visual tests
**Then** all 5 zones render correctly on iPhone X (375×812)
**And** stars don't overlap with nebula card
**And** constellation lines connect stars correctly

**FRs covered:** NFR1, NFR2 (60fps desktop, 45fps mobile)
**Priority:** P0 (BLOCKING)
**Estimated Time:** 3-4 hours

---

### Story 1.5.3: Build Bridge Section

As a visitor,
I want to understand WHY "thinking matters more than tools" through the Five Whys demonstration,
So that I can intellectually understand the methodology before committing to the program.

**Acceptance Criteria:**

**Given** Constellation Zones create emotional recognition
**When** I create `/src/components/Bridge/Bridge.html`
**Then** Bridge section exists with:
  - Hook: "You just saw your voice. Here's the thing: The leap isn't tools. It's thinking."
  - Five Whys accordion:
    - Problem: "AI gives me garbage"
    - Why 1: → "I don't know what to ask"
    - Why 2: → "I'm not clear on my goal"
    - Why 3: → "I haven't structured my thinking"
    - Why 4: → "I jump straight to tools"
    - Why 5: → "Nobody taught me a framework"
    - Aha moment: "Aha. There it is."
  - Promise: "We don't teach prompts. We install thinking habits."
  - CTA: "6 weeks. Zone 0 → Zone 4. One habit at a time. [Find Your Zone]"

**Given** I need Bridge styling
**When** I create `/src/components/Bridge/Bridge.css`
**Then** Bridge has:
  - Spotlight reveal effect (radial gradient ocean-mint 0.03 opacity)
  - Ocean-mint gradient text on "thinking" and "habits"
  - Accordion styling (closed: border only, open: reveals answer)
  - Active accordion has ocean-mint left border
  - Responsive design (mobile/desktop)

**Given** I need Bridge animations
**When** I create `/src/components/Bridge/Bridge.js`
**Then** GSAP ScrollTrigger reveals content progressively:
  - Hook text: Staggered line-by-line
  - Five Whys: Accordion opens on scroll (why 1 → 2 → 3 → 4 → 5)
  - Promise: Fades in with scale (emphasis)
  - CTA: Pulse animation
**And** Only one accordion open at a time (exclusive expand)

**Given** Bridge completes the foundation
**When** I integrate Bridge into main.js
**Then** Bridge positions between Constellation Zones and Discord
**And** Scroll flow: Hero → Constellation Zones → Bridge → Discord → CTA
**And** Strategic analysis validates Epic 2 readiness at 9/10

**FRs covered:** (Intellectual understanding - new FR)
**Priority:** P0 (BLOCKING)
**Estimated Time:** 2-3 hours

---

### Story 1.5.4: Add Accessibility & Reduced Motion

As a visitor with motion sensitivities,
I want the page to work without animations,
So that I can still access the content and convert.

**Acceptance Criteria:**

**Given** WCAG AA compliance is required
**When** I add reduced motion support
**Then** `prefers-reduced-motion: reduce` detected in ConstellationZones.js
**And** when reduced motion:
  - Star twinkle animations: `animation: none`
  - Constellation line draws: `stroke-dashoffset: 0` (instant)
  - Star reveals: All `opacity: 1` immediately (no stagger)
  - Lenis smooth scroll: Disabled (use native scroll)

**Given** screen readers need structure
**When** I add ARIA labels
**Then** `.constellation-zone`: `role="region" aria-label="Zone {name}"`
**And** `.thought-star`: `aria-label="{label}"`
**And** `.voice-nebula`: `role="article" aria-label="{zoneName} voice card"`
**And** Test with VoiceOver/NVDA

**Given** accessibility testing is required
**When** I run Lighthouse audit
**Then** Accessibility score is 95+
**And** All interactive elements are keyboard accessible
**And** Color contrast meets WCAG AA

**FRs covered:** NFR8, NFR9 (WCAG AA, reduced motion)
**Priority:** P1
**Estimated Time:** 1-2 hours

---

### Story 1.5.5: Validate Foundation & Epic 2 Readiness

As a product owner,
I want to validate that the foundation (Hero + ConstellationZones + Bridge) achieves 9/10 Epic 2 readiness,
So that we can proceed to Epic 2 with confidence.

**Acceptance Criteria:**

**Given** foundation components are complete
**When** I review strategic analysis checklist
**Then** the following are validated:
  - Emotional Foundation: 8/10 (Hero + ConstellationZones)
  - Intellectual Foundation: 9/10 (Bridge implemented)
  - Practical Foundation: 8/10 (Bridge demonstrates Five Whys)
  - Conversion Foundation: 9/10 (Bridge connects to CTA)

**Given** user testing is required
**When** I test with 5 users
**Then** 4/5 users can:
  - Identify which zone resonates with them (Constellation Zones)
  - Explain WHY "thinking > tools" (Bridge)
  - Express confidence in the methodology (Five Whys)
  - Click the CTA (conversion intent)

**Given** visual quality must be maintained
**When** I run complete visual test suite
**Then** Mobile tests pass for all 5 zones
**And** Desktop tests pass for all 5 zones
**And** Bridge section tests pass (accordion open/close states)
**And** No regression in Hero section

**Given** performance must meet targets
**When** I run Lighthouse audit
**Then** Performance score is 90+
**And** First Contentful Paint < 1.5s
**And** Time to Interactive < 3.5s
**And** 60fps desktop / 45fps mobile

**Given** foundation is validated
**When** I review Epic 2 readiness
**Then** **Overall Epic 2 Readiness: 9/10 (READY)**
**And** All foundations at 8+/10
**And** Proceed to Epic 2 (Habit Installation & 6-Week Journey)

**FRs covered:** (Foundation validation)
**Priority:** P0
**Estimated Time:** 2-3 hours

---

## REDEFINED EPIC 2: Habit Installation & 6-Week Journey

**Purpose:** Preview the 6-week transformation journey, showing how students progress from Zone 0 to Zone 4 through habit installation (not tool training).

**Strategic Position:**
- Act 3: The Transformation
- Builds on Foundation (Epic 1.5)
- Shows practical application of methodology

### Story 2.1: Preview 6-Week Journey (Zone 0 → Zone 4)

As a visitor,
I want to see the 6-week journey from Zone 0 to Zone 4,
So that I understand what I'll experience in the program.

**Acceptance Criteria:**

**Given** Bridge explains the methodology
**When** I create `/src/components/JourneyPreview/JourneyPreview.html`
**Then** journey preview exists with:
  - Week 1: "Recognize Your Voice" (Zone 0 → Zone 1)
  - Week 2: "Structure Your Thinking" (Zone 1 → Zone 2)
  - Week 3: "Collaborate with AI" (Zone 2 → Zone 3)
  - Week 4: "Direct the Outcome" (Zone 3 → Zone 4)
  - Week 5: "Master Your System" (Zone 4 consolidation)
  - Week 6: "Install for Life" (Habit retention)

**And** Each week shows:
  - Habit being installed
  - Thinking pattern (not prompt)
  - Practice exercise
  - Transformation milestone

**FRs covered:** (Journey clarity - new FR)
**Estimated Time:** 3-4 hours

### Story 2.2: Demonstrate Habit Installation Method

As a visitor,
I want to see HOW habits are installed (not just taught),
So that I understand this is different from tool training.

**Acceptance Criteria:**
- Show habit installation framework
- Demonstrate daily practice structure
- Show community accountability
- Preview transformation evidence

**Estimated Time:** 2-3 hours

### Story 2.3: Show Week-by-Week Progression

As a visitor,
I want to see detailed week-by-week breakdown,
So that I know exactly what to expect.

**Acceptance Criteria:**
- Detailed curriculum for each week
- Time commitment per week
- Deliverables and milestones
- Support structure (clusters, feedback)

**Estimated Time:** 2 hours

### Story 2.4: Social Proof: Past Cohort Results

As a visitor,
I want to see evidence that past students succeeded,
So that I feel confident this works.

**Acceptance Criteria:**
- Before/after stories (Zone 0 → Zone 4)
- Transformation quotes
- Metrics (e.g., "85% reached Zone 4")
- Photos of real students (with permission)

**Estimated Time:** 2 hours

---

## FR COVERAGE MAP (UPDATED)

### Functional Requirements

FR1: Epic 1 - Hero text reveals
FR2: Epic 1 - 4-Act structure setup
FR3: ~~Epic 2 - Territory Map with particles~~ → **Epic 1.5 - Constellation Zones with star fields**
FR4: ~~Epic 2 - Chaos to order animation~~ → **Epic 1.5 - Constellation line draw animations**
FR5: ~~Epic 2 - Zone illumination~~ → **Epic 1.5 - Zone activation with star reveals**
FR6: ~~Epic 2 - Magnetic hovers~~ → **REMOVED** (not in current implementation)
FR7: Epic 3 - Discord chat bubbles
FR8: Epic 3 - Emoji animations
FR9: Epic 3 - CTA to Typeform
FR10: Epic 1 - Smooth scroll infrastructure
FR11: Epic 1 - GSAP ScrollTrigger setup
FR12: Epic 1 - All copy content
FR13: Epic 1 - Ocean mint effects
FR14: Epic 1 - Black gradient background
FR15: ~~Epic 2 - Anticipatory pin~~ → **Epic 1.5 - Zone activation ScrollTriggers**
FR16: Epic 3 - Responsive design
FR17: Epic 1 - Typography

**New FRs:**
FR18: **Epic 1.5 - Emotional recognition through voice resonance**
FR19: **Epic 1.5 - Intellectual understanding through Five Whys**
FR20: **Epic 2 - Journey clarity (6-week preview)**

---

## IMPLEMENTATION PLAN

### Phase 1: Fix Current Implementation (Week 1)
- Story 1.5.2: Fix Constellation Zones Mobile Layout (P0)
- Story 1.5.1: Implement Constellation Zones Structure (if incomplete)
- Story 1.5.4: Add Accessibility & Reduced Motion (P1)

### Phase 2: Complete Foundation (Week 1-2)
- Story 1.5.3: Build Bridge Section (P0)
- Story 1.5.5: Validate Foundation & Epic 2 Readiness (P0)

### Phase 3: Epic 2 Development (Week 2-3)
- Story 2.1: Preview 6-Week Journey
- Story 2.2: Demonstrate Habit Installation Method
- Story 2.3: Show Week-by-Week Progression
- Story 2.4: Social Proof: Past Cohort Results

### Phase 4: Epic 3 Integration (Week 3)
- Epic 3: Discord + CTA (already defined)
- Final integration testing

---

## MIGRATION NOTES

### What Changes:
1. **NEW:** Epic 1.5 added (Constellation Zones + Bridge)
2. **REDEFINED:** Epic 2 scope (Territory Map → Habit Installation Journey)
3. **RENUMBERED:** Epic 3, Epic 4 unchanged (just renumbered)
4. **UPDATED:** FR coverage map reflects actual implementation
5. **REMOVED:** Particle coalescence system (never built, not in strategic vision)
6. **REMOVED:** Magnetic hovers (not in ConstellationZones implementation)

### What Stays The Same:
- Epic 0 (Conversion Foundation) - unchanged
- Epic 1 (Hero & Foundation) - unchanged
- Epic 3 (Discord + CTA) - unchanged, just renumbered
- Epic 4 (Graceful Degradation) - unchanged, just renumbered

### Story File Updates Needed:
1. Rename `story-2.1-constellation-zones-fix.md` → `story-1.5.2-constellation-zones-mobile.md`
2. Create `story-1.5.3-bridge-section.md` (extract from Story 2.1)
3. Create `story-1.5.4-accessibility-reduced-motion.md` (extract from Story 2.1)
4. Create `story-1.5.5-validate-foundation.md`
5. Create Epic 2 stories (2.1-2.4) for Journey Preview
6. Update epics.md with new structure

---

## RECOMMENDATION

**Adopt Path B (Strategic Alignment)** for these reasons:

1. **Strategic Integrity:** Aligns with multi-act architecture (Mirror → Method → Transformation)
2. **Clarity:** Foundation clearly separated from Epic 2 transformation
3. **Scalability:** Epic 2 can focus on habit installation without foundation clutter
4. **Maintainability:** Each epic has clear purpose and boundaries
5. **User Experience:** Recognition → Understanding → Transformation (natural flow)

**Cost:** 1-2 hours to restructure epics and split stories
**Benefit:** Strategic clarity for entire project lifecycle

---

**Decision Required:** Approve Path B restructure?

**Next Steps:**
1. User approves Path B
2. Update epics.md with new structure
3. Split Story 2.1 into Stories 1.5.2, 1.5.3, 1.5.4
4. Create Epic 2 stories (2.1-2.4)
5. Begin implementation with Story 1.5.2 (Mobile Fix)
