---
key: story-1.5.4
title: Add Accessibility & Reduced Motion
epic: 1.5
status: ready-for-dev
priority: P1 (HIGH)
estimatedHours: 1-2

## User Story

As a visitor with motion sensitivities,
I want the page to work without animations,
So that I can still access the content and convert without discomfort.

And as a screen reader user,
I want to understand the constellation zones and bridge section through semantic markup,
So that I can navigate the content and identify which voice resonates with me.

## Context

**Accessibility Requirements (NFR8, NFR9):**
- NFR8: Landing page must follow WCAG AA accessibility standards
- NFR9: Landing page must support prefers-reduced-motion for users with motion sensitivities

**Current State:**
- Constellation Zones has no reduced motion support
- No ARIA labels on interactive elements
- Screen reader users cannot understand zone structure
- Animations always play (no motion sensitivity support)

**Impact:**
- Users with vestibular disorders may experience discomfort or nausea
- Screen reader users cannot understand constellation zones
- Fails WCAG AA compliance
- Blocks accessibility certification

## Acceptance Criteria

### Given: WCAG AA compliance is required
**When:** I add reduced motion support
**Then:**
- `prefers-reduced-motion: reduce` detected in ConstellationZones.js
- When reduced motion is active:
  - Star twinkle animations: `animation: none` (static opacity)
  - Constellation line draws: `stroke-dashoffset: 0` (instant appearance)
  - Star reveals: All `opacity: 1` immediately (no stagger)
  - Voice nebula animations: `transform: none` (instant fade-in)
  - Lenis smooth scroll: Disabled (use native scroll)
- The page remains fully functional without animations
- All content is still visible and readable

### Given: Screen readers need semantic structure
**When:** I add ARIA labels
**Then:**
- `.constellation-zone`: `role="region" aria-label="Zone {name}"`
- `.thought-star`: `aria-label="{label}"` (e.g., "I feel so behind")
- `.voice-nebula`: `role="article" aria-label="{zoneName} voice card"`
- Bridge accordion: `aria-expanded="true/false"` on each why-item
- Bridge CTA: `aria-label="Begin your journey to find your zone"`
- Test with VoiceOver (macOS/iOS) and NVDA (Windows)

### Given: Keyboard navigation must work
**When:** I test keyboard accessibility
**Then:**
- Tab key navigates through all interactive elements
- Focus order is logical (Hero → Zone 0 → Zone 1 → Zone 2 → Zone 3 → Zone 4 → Bridge → Discord → CTA)
- Focus indicators are visible (ocean-mint glow on focused element)
- Enter/Space keys activate interactive elements
- Escape key closes open accordions (Bridge)

### Given: Accessibility testing is required
**When:** I run Lighthouse audit
**Then:**
- Accessibility score is 95+
- All interactive elements are keyboard accessible
- Color contrast meets WCAG AA (4.5:1 for normal text, 3:1 for large text)
- No accessibility errors in DevTools Audit

## Tasks

### P1 - Reduced Motion Support (HIGH)
- [ ] **Task 1.5.4.1:** Implement reduced motion detection
  - [ ] Add `prefers-reduced-motion` detection in ConstellationZones.js
  - [ ] Create `reducedMotion` flag: `const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;`
  - [ ] Disable star twinkle animations when reduced motion
  - [ ] Disable constellation line draw animations when reduced motion
  - [ ] Disable star reveal stagger when reduced motion
  - [ ] **Evidence:** Animations disabled gracefully, content still visible

- [ ] **Task 1.5.4.2:** Add Lenis smooth scroll disable
  - [ ] Detect reduced motion in Lenis config
  - [ ] When reduced motion: Set `smooth: false` (use native scroll)
  - [ ] Test scroll experience with reduced motion enabled
  - [ ] **Evidence:** Native scroll works, no jank

- [ ] **Task 1.5.4.3:** Add reduced motion support to Bridge
  - [ ] Disable accordion animations when reduced motion
  - [ ] Accordion opens instantly (no height transition)
  - [ ] Disable CTA pulse animation when reduced motion
  - [ ] **Evidence:** Bridge functional without animations

### P1 - ARIA Labels & Screen Reader Support (HIGH)
- [ ] **Task 1.5.4.4:** Add ARIA labels to ConstellationZones
  - [ ] Add `role="region"` to `.constellation-zone`
  - [ ] Add `aria-label="Zone {name}"` to each zone (e.g., "Zone 0: Orionis Confusio")
  - [ ] Add `aria-label="{label}"` to `.thought-star` (e.g., "I feel so behind")
  - [ ] Add `role="article"` to `.voice-nebula`
  - [ ] Add `aria-label="{zoneName} voice card"` to nebula (e.g., "Orionis Confusio voice: AI isn't for me")
  - [ ] **Evidence:** Screen reader announces all zones correctly

- [ ] **Task 1.5.4.5:** Add ARIA labels to Bridge
  - [ ] Add `role="region"` to Bridge section
  - [ ] Add `aria-label="Five Whys methodology demonstration"`
  - [ ] Add `aria-expanded="false"` to each `.why-item` (initially closed)
  - [ ] Update `aria-expanded` to `true"` when accordion opens
  - [ ] Add `aria-controls="why-{n}-answer"` to each why-item
  - [ ] **Evidence:** Screen reader announces accordion state correctly

### P1 - Keyboard Navigation (HIGH)
- [ ] **Task 1.5.4.6:** Ensure keyboard navigation works
  - [ ] Test Tab key navigation through all zones
  - [ ] Verify focus order is logical
  - [ ] Add `:focus-visible` styling with ocean-mint glow
  - [ ] Ensure Enter/Space keys activate interactive elements
  - [ ] Add Escape key to close Bridge accordions
  - [ ] **Evidence:** Keyboard navigation works smoothly

### Validation
- [ ] **Task 1.5.4.7:** Run accessibility audit
  - [ ] Test with VoiceOver (macOS/iOS)
  - [ ] Test with NVDA (Windows)
  - [ ] Run Lighthouse Accessibility audit
  - [ ] Verify Accessibility score ≥ 95
  - [ ] Verify color contrast meets WCAG AA
  - [ ] **Evidence:** All accessibility tests pass

- [ ] **Task 1.5.4.8:** Test reduced motion experience
  - [ ] Enable reduced motion in macOS System Preferences → Accessibility → Display
  - [ ] Enable reduced motion in Windows Settings → Ease of Access → Display
  - [ ] Test page experience with reduced motion enabled
  - [ ] Verify no animations play
  - [ ] Verify all content is still accessible
  - [ ] **Evidence:** Reduced motion experience is functional

## Dev Agent Record

### Reduced Motion Implementation
GSAP provides built-in reduced motion support:
```javascript
// Check for reduced motion preference
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Disable animations when reduced motion
if (prefersReducedMotion) {
  // Set all animation durations to 0
  gsap.globalTimeline.timeScale(0);

  // Or skip animations entirely
  return;
}
```

For ConstellationZones:
- Star twinkle: CSS `animation: none` when `prefers-reduced-motion`
- Constellation lines: Set `stroke-dashoffset: 0` immediately
- Star reveals: Set all `opacity: 1` immediately, skip stagger
- Lenis: Set `smooth: false` to use native scroll

### ARIA Label Strategy
ConstellationZones structure:
```html
<section class="constellation-zone" data-zone="0" role="region" aria-label="Zone 0: Orionis Confusio">
  <svg class="constellation-canvas"></svg>

  <div class="star-pool-mobile">
    <div class="thought-star" aria-label="I feel so behind">
      <div class="star-point"></div>
      <span class="star-label">"I feel so behind"</span>
    </div>
    <!-- 3 more stars -->
  </div>

  <div class="voice-nebula" role="article" aria-label="Orionis Confusio voice: AI isn't for me">
    <p class="zone-constellation-name">Orionis Confusio</p>
    <h2 class="voice-quote">"AI isn't for me."</h2>
    <p class="voice-inner">...</p>
  </div>
</section>
```

Bridge accordion structure:
```html
<div class="why-item" data-why="1">
  <button aria-expanded="false" aria-controls="why-1-answer">
    <span class="why-label">Why?</span>
  </button>
  <div id="why-1-answer" class="why-answer" role="region" aria-hidden="true">
    <span class="why-answer">"I don't know what to ask"</span>
  </div>
</div>
```

### Keyboard Navigation Flow
Logical tab order:
1. Hero (no interactive elements, skip to next)
2. Zone 0 (first thought-star)
3. Zone 0 (second thought-star)
4. Zone 0 (third thought-star)
5. Zone 0 (fourth thought-star)
6. Zone 1 (first thought-star)
7. ... continue through all zones
8. Bridge (Why 1 accordion button)
9. Bridge (Why 2 accordion button)
10. ... continue through all Why buttons
11. Bridge CTA button
12. Discord section (if any interactive elements)
13. Final CTA button

Focus indicator:
- `:focus-visible` pseudo-class
- Ocean-mint glow: `box-shadow: 0 0 0 3px rgba(64, 224, 208, 0.5)`
- Outline removal for mouse users: `:focus:not(:focus-visible) { outline: none; }`

## Definition of Done

- [x] Story reviewed and accepted by product owner
- [ ] All P1 tasks completed:
  - [ ] Reduced motion support implemented
  - [ ] ARIA labels added to ConstellationZones and Bridge
  - [ ] Keyboard navigation works
  - [ ] Accessibility audit passed
- [ ] Lighthouse Accessibility score ≥ 95
- [ ] Screen reader testing passed (VoiceOver + NVDA)
- [ ] Reduced motion testing passed (macOS + Windows)
- [ ] WCAG AA compliance validated
- [ ] Code committed to git with clear commit message
- [ ] Story marked as completed in sprint status

## Related Stories
- **Story 1.5.2:** "Fix Constellation Zones Mobile Layout" - Prerequisite
- **Story 1.5.3:** "Build Bridge Section" - Prerequisite
- **Story 1.5.5:** "Validate Foundation & Epic 2 Readiness" - Next step

## References
- WCAG 2.1 AA Standards: https://www.w3.org/WAI/WCAG21/quickref/
- prefers-reduced-motion: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- GSAP Reduced Motion: https://greensock.com/docs/v3/PluginMatchMedia
- ARIA Authoring Practices: https://www.w3.org/WAI/ARIA/apg/
- Implementation: `/k2m-landing/src/components/ConstellationZones/`
