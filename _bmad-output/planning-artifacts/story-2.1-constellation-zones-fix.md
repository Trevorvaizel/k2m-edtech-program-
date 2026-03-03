---
key: story-2.1-constellation-zones-fix
title: Fix Constellation Zones Mobile Layout & Implement Bridge
epic: 2
status: ready-for-dev
priority: P0 (BLOCKING Epic 2 completion)
estimatedHours: 6-8

## User Story

As a visitor on mobile,
I want to see the constellation zones with stars positioned clearly above and below the central nebula card,
So that I can experience the same emotional impact as desktop users and understand my learning journey.

And as a product owner,
I want the Bridge section implemented to connect emotional resonance to intellectual understanding,
So that Epic 2 achieves 9/10 readiness (currently 4/10) and visitors experience the complete narrative arc.

## Context

**Strategic Analysis Findings** (from mirror-zones-strategic-analysis.md):
- Emotional Foundation: 8/10 (EXCELLENT) - Hero + Constellation Zones validate confusion
- **Intellectual Foundation: 2/10 → 9/10 with Bridge** - Missing the "Why thinking matters" explanation
- **Conversion Foundation: 4/10 → 9/10 with Bridge** - Bridge demonstrates Five Whys methodology
- **Current Epic 2 Readiness: NOT READY (4/10)**
- **With Bridge: READY (9/10)**

**Implementation Gap:**
- Epic 2 planned: Territory Map with particle coalescence (200 desktop, 50 mobile)
- Actual implementation: Constellation Zones (hybrid of deep-mirror-v2 Hero + constellation mirror zones)
- **Critical difference:** ConstellationZones is emotion-focused (zones as "voices"), Territory Map was intellectual (zones as positions)
- **Bridge requirement:** Connect emotional resonance (Constellation Zones) to intellectual understanding (Five Whys demonstration)

## Adversarial Code Review Findings

### Critical Issues (BLOCKING)

1. **Mobile Layout Completely Broken** (P0)
   - **Evidence:** Mobile CSS check test showed `position: relative` and `max-width: 520px` (desktop values)
   - **Expected:** `position: absolute` with stars at 10-30% (above nebula) and 70-90% (below nebula)
   - **Root Cause:** Media query `@media (max-width: 768px)` not applying correctly
   - **Impact:** Stars render in horizontal scroll layout, hidden behind nebula card
   - **File:** ConstellationZones.css:241-318
   - **Test Evidence:** tests/screenshots/mobile-css-check.spec.ts shows computed styles not matching mobile CSS

2. **Bridge Section Not Implemented** (P0)
   - **Evidence:** Bridge.html, Bridge.css, Bridge.js do not exist
   - **Impact:** Epic 2 readiness only 4/10, missing critical "Why thinking matters" explanation
   - **User Impact:** Visitors experience emotional resonance but no intellectual bridge to conversion
   - **Strategic Analysis:** "PRIORITY 1: Implement Bridge Section immediately"
   - **Requirement:** Five Whys methodology demonstration connecting zones to thinking habits

3. **Mobile Performance Issue - 150 Animated Stars** (P0)
   - **Evidence:** `for (let i = 0; i < 150; i++)` creates 150 stars regardless of device
   - **File:** ConstellationZones.js:138
   - **Expected:** 50 stars maximum on mobile (per Epic 2 Story 2.2 requirements)
   - **Impact:** 60fps desktop / 45fps mobile performance targets not met on mobile
   - **Lighthouse Impact:** Performance score < 90 on mobile devices

4. **Mobile Media Query Not Applying** (P0)
   - **Evidence:** Debug test shows stars with `position: relative` (desktop) instead of `absolute` (mobile)
   - **File:** ConstellationZones.css:241
   - **Root Cause:** Possible CSS specificity conflict or media query not matching viewport
   - **Impact:** ALL mobile-specific styles ignored (nebula max-width, star positions, labels)

### High Priority Issues

5. **MirrorZones Dead Code Not Cleaned Up** (P1)
   - **Evidence:** MirrorZones directory exists alongside ConstellationZones
   - **Impact:** Codebase confusion, potential merge conflicts
   - **Action:** Remove MirrorZones/ directory (abandoned implementation)

6. **No Reduced Motion Support** (P1)
   - **Evidence:** No `prefers-reduced-motion` checks in animation code
   - **Requirement:** NFR9 - "Landing page must support prefers-reduced-motion"
   - **Impact:** Accessibility violation, WCAG AA non-compliance
   - **File:** ConstellationZones.js - entire animation system

7. **Silent Failures in Star Field Creation** (P1)
   - **Evidence:** `if (!starfield) return;` with no error logging (line 135)
   - **Impact:** Stars silently fail to appear, no debugging information
   - **Best Practice:** Should log warning when starfield container missing

### Medium Priority Issues

8. **Missing ARIA Labels** (P2)
   - **Evidence:** Interactive elements lack accessibility attributes
   - **Impact:** Screen reader users cannot understand zone structure
   - **Files:** ConstellationZones.html - all zones, stars, nebula cards

9. **Magic Numbers Not Documented** (P2)
   - **Examples:**
     - `150` star count (line 138)
     - `10 + (y / 50) * 20` mobile positioning formula (line 56)
     - `2 + Math.random() * 4` twinkle duration (line 145)
   - **Impact:** Maintenance difficulty, unclear intent

10. **Cleanup Function Never Called** (P2)
    - **Evidence:** `cleanupConstellationZonesAnimations()` exists but never invoked
    - **Impact:** Memory leaks on route changes, ScrollTrigger never killed
    - **Requirement:** NFR13 - "Landing page must implement code splitting for GSAP plugins"

## Acceptance Criteria

### Given: Constellation Zones mobile layout is broken
**When:** I fix the mobile CSS media query issue
**Then:**
- Media query `@media (max-width: 768px)` applies correctly on mobile devices
- Stars position at 10-30% (above nebula) and 70-90% (below nebula) on mobile
- Nebula card has `max-width: 85%` and `padding: 1.25rem 0.75rem` on mobile
- Mobile visual test shows constellation pattern squeezed (25-75% width) but recognizable
- No horizontal scrolling occurs on mobile devices
- All 5 zones render correctly on iPhone X (375×812) viewport

### Given: Mobile performance is critical for conversion
**When:** I optimize the star field for mobile
**Then:**
- Star count reduced from 150 to 50 on mobile devices (`isMobile()` check)
- Desktop maintains 150 stars for visual richness
- Performance test shows 45fps+ on mobile (iPhone 12+, Samsung Galaxy S21+)
- Lighthouse Performance Score ≥ 90 on mobile
- First Contentful Paint < 1.5s on mobile
- Time to Interactive < 3.5s on mobile

### Given: Bridge section is required for Epic 2 readiness
**When:** I implement the Bridge section
**Then:**
- Bridge.html exists with Five Whys methodology accordion
- Bridge.css has styling matching Constellation Zones visual theme
- Bridge.js implements accordion interactions with GSAP
- Bridge section positioned between Hero and Constellation Zones
- Bridge explains: "Why thinking > tools" using Five Whys framework
- Each Why level is expandable/collapsible
- Bridge connects emotional resonance (Hero) to practical application (Constellation Zones)
- Strategic analysis validates Epic 2 readiness at 9/10

### Given: Accessibility is required for WCAG AA compliance
**When:** I add reduced motion support
**Then:**
- `prefers-reduced-motion: reduce` detected in ConstellationZones.js
- When reduced motion: star twinkle animations disabled (static opacity)
- When reduced motion: constellation line draw animations simplified (instant)
- When reduced motion: star reveal stagger disabled (all appear simultaneously)
- Lenis smooth scroll disabled, uses native scroll
- Page remains fully functional without animations

### Given: Code quality standards must be maintained
**When:** I address medium priority issues
**Then:**
- MirrorZones directory removed from codebase
- ARIA labels added to all interactive elements:
  - `.constellation-zone`: `role="region"`, `aria-label="Zone {name}"`
  - `.thought-star`: `aria-label="{label}"`
  - `.voice-nebula`: `role="article"`, `aria-label="{zoneName} voice"`
- Magic numbers documented with constants:
  - `const STAR_COUNT_DESKTOP = 150`
  - `const STAR_COUNT_MOBILE = 50`
  - `const MOBILE_TOP_ZONE_MIN = 10` // Above nebula
  - `const MOBILE_TOP_ZONE_MAX = 30`
  - `const MOBILE_BOTTOM_ZONE_MIN = 70` // Below nebula
  - `const MOBILE_BOTTOM_ZONE_MAX = 90`
- Error logging added to star field creation
- Cleanup function called on component unmount/route change

### Given: Complete visual testing validates implementation
**When:** I run Playwright visual tests
**Then:**
- Mobile tests pass for all 5 zones (375×812 viewport)
- Desktop tests pass for all 5 zones (1920×1080 viewport)
- No regression in Hero section visuals
- Bridge section tests pass (accordion open/close states)
- Screenshots match baseline for:
  - story-2.1-constellation-zones-mobile.png
  - story-2.1-constellation-zones-desktop.png
  - story-2.1-bridge-section.png

### Given: Strategic requirements must be validated
**When:** I review the implementation against strategic analysis
**Then:**
- Emotional Foundation: 8/10 maintained (Hero + Constellation Zones)
- Intellectual Foundation: 9/10 achieved (Bridge added)
- Practical Foundation: 8/10 achieved (Bridge demonstrates Five Whys)
- Conversion Foundation: 9/10 achieved (Bridge explains value)
- **Overall Epic 2 Readiness: 9/10 (READY)**
- User testing shows 4/5 users can identify their zone after Bridge

## Tasks

### P0 - Fix Mobile Layout (BLOCKING)
- [ ] **Task 2.1.1:** Debug and fix CSS media query application issue
  - [ ] Investigate why `@media (max-width: 768px)` not matching viewport
  - [ ] Check for CSS specificity conflicts (`.thought-star` vs mobile override)
  - [ ] Test on actual mobile device (iPhone X, Samsung Galaxy)
  - [ ] Verify computed styles match mobile CSS expectations
  - [ ] **Evidence:** Mobile debug test shows `position: absolute`, correct top/left values

- [ ] **Task 2.1.2:** Fix mobile star positioning logic
  - [ ] Review ConstellationZones.js:42-70 mobile positioning code
  - [ ] Ensure stars position at 10-30% (above nebula) and 70-90% (below nebula)
  - [ ] Test constellation line connections on mobile (should still connect stars)
  - [ ] Validate no overlap with nebula card
  - [ ] **Evidence:** Visual test shows clear separation, no hidden stars

- [ ] **Task 2.1.3:** Optimize mobile star count
  - [ ] Add `isMobile()` check to star field creation (line 138)
  - [ ] Desktop: 150 stars (maintain visual richness)
  - [ ] Mobile: 50 stars (per Epic 2 Story 2.2 requirements)
  - [ ] Update star field creation logic:
    ```javascript
    const starCount = isMobile() ? 50 : 150;
    for (let i = 0; i < starCount; i++) {
      // ... create star
    }
    ```
  - [ ] **Evidence:** Performance test shows 45fps+ on mobile

### P0 - Implement Bridge Section (BLOCKING)
- [ ] **Task 2.1.4:** Create Bridge.html structure
  - [ ] Create `/src/components/Bridge/Bridge.html`
  - [ ] Add section with Five Whys accordion
  - [ ] Each Why level expands/collapses to show explanation
  - [ ] Content structure:
    - "Why thinking matters more than tools"
    - Why 1: "Why do we focus on thinking?"
    - Why 2: "Why is thinking better than prompts?"
    - Why 3: "Why install habits instead of learning tricks?"
    - Why 4: "Why does this lead to confidence?"
    - Why 5: "Why is this the foundation of AI mastery?"
  - [ ] **Evidence:** HTML exists, semantic structure, accessible markup

- [ ] **Task 2.1.5:** Create Bridge.css styling
  - [ ] Create `/src/components/Bridge/Bridge.css`
  - [ ] Match Constellation Zones visual theme (ocean mint accents)
  - [ ] Accordion styling:
    - Closed: Shows question only, subtle border
    - Open: Reveals answer with smooth height transition
    - Active state: Ocean mint left border accent
  - [ ] Responsive design (mobile/desktop)
  - [ ] **Evidence:** Styles match Constellation Zones, accordion animations smooth

- [ ] **Task 2.1.6:** Create Bridge.js interactions
  - [ ] Create `/src/components/Bridge/Bridge.js`
  - [ ] Implement accordion open/close with GSAP
  - [ ] Only one accordion open at a time (exclusive expand)
  - [ ] Smooth height animation: `height: 0 → height: auto`
  - [ ] Ocean mint accent on active accordion
  - [ ] ScrollTrigger for accordion animations (as user scrolls through Bridge)
  - [ ] **Evidence:** Accordion opens/closes smoothly, no layout shift

- [ ] **Task 2.1.7:** Integrate Bridge into main.js
  - [ ] Import Bridge HTML/CSS/JS in main.js
  - [ ] Position Bridge between Hero and Constellation Zones
  - [ ] Verify scroll flow: Hero → Bridge → Constellation Zones → Discord → CTA
  - [ ] **Evidence:** Bridge renders in correct position, scroll transitions smooth

### P1 - Accessibility & Performance
- [ ] **Task 2.1.8:** Implement reduced motion support
  - [ ] Add `prefers-reduced-motion` detection in ConstellationZones.js
  - [ ] When detected:
    - Star twinkle animations: `animation: none`
    - Constellation line draws: `stroke-dashoffset: 0` (instant)
    - Star reveals: Remove stagger, all `opacity: 1` immediately
    - Lenis smooth scroll: Disable, use native scroll
  - [ ] Test with macOS System Preferences → Accessibility → Display → Reduce motion
  - [ ] **Evidence:** Reduced motion test passes, animations disabled gracefully

- [ ] **Task 2.1.9:** Add ARIA labels for accessibility
  - [ ] Add ARIA labels to ConstellationZones.html:
    - `.constellation-zone`: `role="region" aria-label="Zone {name}"`
    - `.thought-star`: `aria-label="{label}"`
    - `.voice-nebula`: `role="article" aria-label="{zoneName} voice card"`
  - [ ] Test with screen reader (VoiceOver/NVDA)
  - [ ] **Evidence:** Screen reader announces all zones correctly

### P2 - Code Quality
- [ ] **Task 2.1.10:** Clean up dead code
  - [ ] Remove MirrorZones directory from codebase
  - [ ] Verify no imports/references to MirrorZones remain
  - [ ] **Evidence:** `find . -name "*MirrorZone*"` returns empty

- [ ] **Task 2.1.11:** Document magic numbers
  - [ ] Add constants to ConstellationZones.js:
    ```javascript
    // Star field configuration
    const STAR_COUNT_DESKTOP = 150;
    const STAR_COUNT_MOBILE = 50;
    const TWINKLE_DURATION_MIN = 2; // seconds
    const TWINKLE_DURATION_MAX = 4;

    // Mobile positioning (percentages)
    const MOBILE_TOP_ZONE_MIN = 10; // Above nebula
    const MOBILE_TOP_ZONE_MAX = 30;
    const MOBILE_BOTTOM_ZONE_MIN = 70; // Below nebula
    const MOBILE_BOTTOM_ZONE_MAX = 90;
    const MOBILE_WIDTH_COMPRESSION = 50; // Compress to 25-75% (center 50%)
    const MOBILE_WIDTH_OFFSET = 25;
    ```
  - [ ] Replace hardcoded numbers with constants
  - [ ] **Evidence:** No magic numbers in code, all documented

- [ ] **Task 2.1.12:** Improve error handling
  - [ ] Add logging to star field creation (line 135):
    ```javascript
    if (!starfield) {
      console.warn('Star field container not found - skipping background stars');
      return;
    }
    ```
  - [ ] Add error handling for missing constellation zones
  - [ ] Add cleanup call in main.js before component unmount
  - [ ] **Evidence:** Console warnings appear when elements missing, cleanup called

### Validation
- [ ] **Task 2.1.13:** Run complete visual test suite
  - [ ] Mobile tests: All 5 zones on iPhone X (375×812)
  - [ ] Desktop tests: All 5 zones on 1920×1080
  - [ ] Bridge section tests: Accordion open/close states
  - [ ] Hero regression test: Ensure no visual changes to Hero
  - [ ] **Evidence:** All visual tests pass, no regression

- [ ] **Task 2.1.14:** Validate Epic 2 readiness
  - [ ] Review strategic analysis checklist:
    - [x] Emotional Foundation: 8/10 (Hero + Constellation Zones)
    - [ ] Intellectual Foundation: 9/10 (Bridge implemented)
    - [ ] Practical Foundation: 8/10 (Bridge demonstrates Five Whys)
    - [ ] Conversion Foundation: 9/10 (Bridge connects to CTA)
  - [ ] Overall Epic 2 Readiness: 9/10 (READY)
  - [ ] **Evidence:** Strategic analysis validates all foundations at 8+/10

- [ ] **Task 2.1.15:** User testing validation (optional but recommended)
  - [ ] Test with 3 users on mobile device
  - [ ] Ask: "Can you identify which zone you're in?"
  - [ ] Ask: "Does the Bridge section explain why thinking matters?"
  - [ ] Ask: "Do you feel confident clicking the CTA?"
  - [ ] **Evidence:** 4/5 users identify zone, understand Bridge, express CTA intent

## Dev Agent Record

### Implementation Notes
- **ConstellationZones vs TerritoryMap:** The actual implementation (ConstellationZones) differs from Epic 2 spec (TerritoryMap with particle coalescence). ConstellationZones is emotion-focused ("voices"), Territory Map was intellectual ("positions"). The Bridge section is critical to connect emotional resonance to intellectual understanding.

### Mobile Layout Bug Root Cause Analysis
The mobile CSS media query `@media (max-width: 768px)` is not applying correctly. Debug test evidence:
- Expected: `.thought-star` with `position: absolute`
- Actual: `.thought-star` with `position: relative` (desktop default)
- Hypothesis: CSS specificity conflict - desktop styles may have higher specificity
- Investigation: Check for duplicate selectors, `!important` usage, or inline styles overriding media query

### Bridge Section Content Strategy
The Bridge explains "Why thinking > tools" using Five Whys:
1. Why thinking matters: "Tools expire, habits last"
2. Why is thinking better: "Prompts solve today's problems, thinking solves tomorrow's"
3. Why install habits: "AI changes monthly, thinking patterns adapt to any AI"
4. Why confidence: "You control the quality, not the AI"
5. Why foundation: "This is how you democratize intelligence"

This connects Hero's emotional validation ("You're not alone") to Constellation Zones' practical application ("Here's your zone") to CTA's conversion ("Begin your journey").

### Performance Optimization Strategy
- Desktop: 150 stars (visual richness, acceptable performance)
- Mobile: 50 stars (per Epic 2 Story 2.2 requirement: "50 particles mobile")
- GPU acceleration: `will-change: transform, opacity` during animation
- Cleanup: Set `will-change: auto` after animation completes
- Fallback: If FPS < 30 for 2s, reduce star count by 50%

### Testing Evidence Files
- `tests/screenshots/mobile-css-check.spec.ts` - Shows computed styles not matching mobile CSS
- `tests/screenshots/mobile-constellation-debug.spec.ts` - Shows star positioning issues
- `../_bmad-output/implementation-artifacts/mirror-zones-strategic-analysis.md` - Strategic analysis showing Bridge requirement

## Definition of Done

- [x] Story reviewed and accepted by product owner
- [x] Adversarial code review completed with 10 issues documented
- [ ] All P0 (Critical) issues resolved:
  - [ ] Mobile CSS media query applying correctly
  - [ ] Stars positioned clearly on mobile (no overlap)
  - [ ] Bridge section implemented and integrated
  - [ ] Mobile performance: 50 stars, 45fps+
- [ ] All P1 (High) issues resolved:
  - [ ] MirrorZones dead code removed
  - [ ] Reduced motion support implemented
  - [ ] Error logging added
- [ ] All P2 (Medium) issues addressed:
  - [ ] ARIA labels added
  - [ ] Magic numbers documented
  - [ ] Cleanup function integrated
- [ ] Visual tests pass (mobile + desktop)
- [ ] Strategic analysis validates Epic 2 readiness at 9/10
- [ ] Code committed to git with clear commit message
- [ ] Story marked as completed in sprint status

## Related Stories
- **Epic 1 Story 1.5:** "Optimize Hero Performance" - Performance optimization patterns
- **Epic 2 Story 2.2:** "Build Particle Coalescence System" - Particle count requirements (50 mobile)
- **Epic 2 Story 2.3:** "Implement Zone Illumination" - Zone interaction patterns
- **Epic 3 Story 3.4:** "Implement CTA Animations and Responsive Design" - Reduced motion support patterns

## References
- Strategic Analysis: `/_bmad-output/implementation-artifacts/mirror-zones-strategic-analysis.md`
- ConstellationZones Implementation: `/k2m-landing/src/components/ConstellationZones/`
- Mobile Debug Test: `/k2m-landing/tests/screenshots/mobile-css-check.spec.ts`
- Epic Breakdown: `/_bmad-output/planning-artifacts/epics.md` (lines 551-883)
