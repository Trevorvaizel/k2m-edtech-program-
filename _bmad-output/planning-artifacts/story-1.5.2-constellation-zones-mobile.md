---
key: story-1.5.2
title: Fix Constellation Zones Mobile Layout
epic: 1.5
status: ready-for-dev
priority: P0 (BLOCKING)
estimatedHours: 3-4

## User Story

As a visitor on mobile,
I want to see the constellation zones with stars positioned clearly above and below the central nebula card,
So that I can experience the same emotional impact as desktop users and identify which voice resonates with me.

## Context

**Current Issue:** Mobile layout is completely broken
- Stars render with `position: relative` instead of `absolute`
- Stars overlap with nebula card instead of positioning above/below
- Media query `@media (max-width: 768px)` not applying correctly
- 150 stars on mobile causing performance issues (should be 50)

**Evidence:** Mobile CSS check test (tests/screenshots/mobile-css-check.spec.ts) shows:
- Computed `position: relative` (desktop) instead of `absolute` (mobile)
- Computed `max-width: 520px` (desktop) instead of `85%` (mobile)
- Stars hidden behind nebula card

**Strategic Impact:**
- Without mobile fix: Foundation is incomplete (4/10)
- With mobile fix: Foundation progresses to 6/10
- Required for Story 1.5.5 (Foundation Validation)

## Adversarial Code Review Findings

### Critical Issues (P0)

1. **Mobile CSS Media Query Not Applying**
   - **File:** ConstellationZones.css:241
   - **Expected:** `.thought-star` with `position: absolute`
   - **Actual:** `position: relative` (desktop default)
   - **Root Cause:** Media query specificity conflict or not matching viewport
   - **Impact:** ALL mobile styles ignored

2. **Mobile Stars Overlapping Nebula**
   - **File:** ConstellationZones.css:282-294
   - **Expected:** Stars at 10-30% (above) and 70-90% (below)
   - **Actual:** Stars render in horizontal scroll, hidden behind card
   - **Impact:** Users can't see stars, emotional recognition lost

3. **Mobile Performance Issue - 150 Stars**
   - **File:** ConstellationZones.js:138
   - **Current:** `for (let i = 0; i < 150; i++)`
   - **Required:** 50 stars on mobile (per FR NFR2: 45fps mobile)
   - **Impact:** Performance < 45fps, fails Lighthouse 90+ score

## Acceptance Criteria

### Given: Mobile CSS media query is broken
**When:** I fix the media query application issue
**Then:**
- Media query `@media (max-width: 768px)` applies correctly on mobile devices
- Computed styles show `.thought-star` with `position: absolute`
- Stars position at 10-30% (above nebula) and 70-90% (below nebula)
- Nebula card has `max-width: 85%` and `padding: 1.25rem 0.75rem`
- No horizontal scrolling occurs on mobile devices
- Visual test shows constellation pattern squeezed (25-75% width) but recognizable

### Given: Mobile performance is critical for conversion
**When:** I optimize the star field for mobile
**Then:**
- Star count reduced from 150 to 50 on mobile devices
- Desktop maintains 150 stars for visual richness
- Performance test shows 45fps+ on mobile (iPhone 12+, Samsung Galaxy S21+)
- Lighthouse Performance Score ≥ 90 on mobile
- First Contentful Paint < 1.5s on mobile
- Time to Interactive < 3.5s on mobile

### Given: Visual quality must match desktop
**When:** I run Playwright visual tests
**Then:**
- Mobile tests pass for all 5 zones (375×812 viewport)
- Desktop tests pass for all 5 zones (1920×1080 viewport)
- No regression in Hero section visuals
- Screenshots match baseline:
  - story-1.5.2-mobile-zone-0.png
  - story-1.5.2-mobile-zone-4.png
  - story-1.5.2-desktop-zone-0.png

### Given: Star positioning algorithm is complex
**When:** I review mobile positioning logic
**Then:**
- Top stars (y < 50): position at 10-30% from top (above nebula at 50%)
- Bottom stars (y > 50): position at 70-90% from top (below nebula at 50%)
- Horizontal compression: 25-75% width (center 50%)
- Constellation lines still connect stars correctly after mobile adjustment
- No overlap with nebula card (bounding boxes don't intersect)

## Tasks

### P0 - Fix Mobile CSS (BLOCKING)
- [ ] **Task 1.5.2.1:** Debug and fix CSS media query application
  - [ ] Investigate why `@media (max-width: 768px)` not matching viewport
  - [ ] Check for CSS specificity conflicts (`.thought-star` vs mobile override)
  - [ ] Test on actual mobile device (iPhone X, Samsung Galaxy)
  - [ ] Verify computed styles match mobile CSS expectations
  - [ ] **Evidence:** Mobile debug test shows `position: absolute`, correct top/left values

- [ ] **Task 1.5.2.2:** Fix mobile star positioning logic
  - [ ] Review ConstellationZones.js:42-70 mobile positioning code
  - [ ] Ensure stars position at 10-30% (above nebula) and 70-90% (below nebula)
  - [ ] Test constellation line connections on mobile (should still connect stars)
  - [ ] Validate no overlap with nebula card
  - [ ] **Evidence:** Visual test shows clear separation, no hidden stars

- [ ] **Task 1.5.2.3:** Optimize mobile star count
  - [ ] Add `isMobile()` check to star field creation (line 138)
  - [ ] Desktop: 150 stars (maintain visual richness)
  - [ ] Mobile: 50 stars (per FR NFR2 requirement)
  - [ ] Update star field creation logic:
    ```javascript
    const starCount = isMobile() ? 50 : 150;
    for (let i = 0; i < starCount; i++) {
      // ... create star
    }
    ```
  - [ ] **Evidence:** Performance test shows 45fps+ on mobile

### Validation
- [ ] **Task 1.5.2.4:** Run mobile visual tests
  - [ ] Test all 5 zones on iPhone X (375×812)
  - [ ] Test all 5 zones on desktop (1920×1080)
  - [ ] Verify no regression in Hero section
  - [ ] **Evidence:** All visual tests pass, screenshots match baseline

- [ ] **Task 1.5.2.5:** Validate mobile performance
  - [ ] Run Lighthouse audit on mobile device
  - [ ] Verify Performance Score ≥ 90
  - [ ] Verify First Contentful Paint < 1.5s
  - [ ] Verify Time to Interactive < 3.5s
  - [ ] **Evidence:** Performance metrics meet FR NFR1-NFR5

## Dev Agent Record

### Mobile Layout Bug Root Cause
The mobile CSS media query `@media (max-width: 768px)` is not applying correctly. Debug test evidence:
- Expected: `.thought-star` with `position: absolute`
- Actual: `.thought-star` with `position: relative` (desktop default)
- Hypothesis: CSS specificity conflict - desktop styles may have higher specificity
- Investigation: Check for duplicate selectors, `!important` usage, or inline styles overriding media query

### Mobile Positioning Algorithm
Current mobile positioning logic (ConstellationZones.js:42-70):
- Input: Original star position `dataset.x`, `dataset.y` (0-100%)
- Logic: Compress horizontal spread to 25-75% width, separate vertical into top/bottom zones
- Output: `mobileX`, `mobileY` in percentages
- **Issue:** CSS `position: relative` ignores these percentage positions

### Performance Optimization Strategy
- Desktop: 150 stars (visual richness, acceptable performance)
- Mobile: 50 stars (per FR NFR2: 45fps mobile requirement)
- GPU acceleration: `will-change: transform, opacity` during animation
- Cleanup: Set `will-change: auto` after animation completes
- Fallback: If FPS < 30 for 2s, reduce star count by 50%

## Definition of Done

- [x] Story reviewed and accepted by product owner
- [x] Adversarial code review completed with 3 issues documented
- [ ] All P0 (Critical) issues resolved:
  - [ ] Mobile CSS media query applying correctly
  - [ ] Stars positioned clearly on mobile (no overlap)
  - [ ] Mobile performance: 50 stars, 45fps+
- [ ] Visual tests pass (mobile + desktop)
- [ ] Performance metrics meet FR NFR1-NFR5
- [ ] Code committed to git with clear commit message
- [ ] Story marked as completed in sprint status

## Related Stories
- **Story 1.5.1:** "Implement Constellation Zones Structure" - Base implementation
- **Story 1.5.3:** "Build Bridge Section" - Next priority after mobile fix
- **Story 1.5.4:** "Add Accessibility & Reduced Motion" - Follow-up task

## References
- Mobile Debug Test: `/k2m-landing/tests/screenshots/mobile-css-check.spec.ts`
- Mobile Constellation Debug: `/k2m-landing/tests/screenshots/mobile-constellation-debug.spec.ts`
- Implementation: `/k2m-landing/src/components/ConstellationZones/`
- Strategic Analysis: `/_bmad-output/implementation-artifacts/mirror-zones-strategic-analysis.md`
