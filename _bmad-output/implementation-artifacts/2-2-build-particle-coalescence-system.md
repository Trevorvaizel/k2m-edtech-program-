# Story 2.2: Build Particle Coalescence System

Status: in-progress

## Story

As a visitor,
I want to see particles coalesce from chaos into order across the Territory Map,
So that I experience a stunning "WHOA moment" that represents transformation from confusion to clarity.

## Scope Decision

**IMPORTANT**: This story focuses on **Zone 0-1 (Wilderness) particle drift animation** - the foundational WHOA moment.

Zone-specific animation techniques for zones 2-4 are deferred to future stories:
- **Story 2.2b** (deferred): Zone 2 snap transitions (scrub: 0.5, snappy)
- **Story 2.2c** (deferred): Zone 3 fluid morphing (scrub: 1.5, conversational)
- **Story 2.2d** (deferred): Zone 4 mirror pause (scrub: 2.0, contemplative)

This prevents scope creep and ensures each zone's unique emotional signature is properly implemented.

## Acceptance Criteria

**Given** the Territory Map HTML exists (from Story 2.1)

**When** I create `/src/components/TerritoryMap/MapParticles.js`

**Then** a `MapParticleSystem` class is defined with the following architecture:

### Particle System Initialization

**Given** the particle system is initialized
**When** I call the `init()` method
**Then** the following occurs:

1. **Particle count is set based on device capability**:
   ```javascript
   const isMobile = window.innerWidth < 768;
   const particleCount = isMobile ? 105 : 300; // 15 particles per zone × 7 zones
   ```

2. **Particles are created as div elements**:
   - Class: `.map-particle`
   - Initial state: `opacity: 0`, `scale: 0`
   - Random starting positions: `x: Math.random() * 2000 - 1000`, `y: Math.random() * 2000 - 1000`

3. **Target positions are calculated** using zone-based distribution:
   - Zone 0-1 (Wilderness): 40% of particles (120 desktop, 42 mobile)
   - Zone 2-4 (Future zones): 60% of particles distributed across remaining zones
   - Each particle assigned a `targetX`, `targetY` based on its destination zone

### Particle Styling

**Given** particles need to be styled
**When** I create `/src/components/TerritoryMap/Map.css`
**Then** `.map-particle` has:

```css
.map-particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: radial-gradient(circle, var(--ocean-mint-glow) 0%, transparent 70%);
  border-radius: 50%;
  will-change: transform, opacity;
  pointer-events: none;
  opacity: 0; /* Initially hidden */
}

@media (max-width: 768px) {
  .map-particle {
    width: 2px;
    height: 2px;
  }
}
```

### Chaos → Order Animation (Zone 0-1 Wilderness Focus)

**Given** I need the chaos → order animation for Zone 0-1
**When** I implement `animateFormation()` method
**Then** a GSAP timeline is created with ScrollTrigger:

```javascript
const timeline = gsap.timeline({
  scrollTrigger: {
    trigger: ".territory-map",
    start: "top center",
    end: "center center",
    scrub: 0.3, // FAST scrub for mystery → curiosity (Zone 0-1)
    anticipatePin: 1
  }
});
```

**And** the animation follows this emotional arc:

#### Phase 1: Pre-Reveal Anticipation (Disney Principle 1)
```javascript
// 0.3s pre-movement creates tension
timeline.to(".map-particle", {
  scale: 0.02,
  duration: 0.3,
  ease: "sine.inOut"
});
```

#### Phase 2: Sequential Coalescence (Disney Principle 4: STAGING)
```javascript
// Apply 80/20 Emotional Punctuation Rule
const particles = document.querySelectorAll('.map-particle');
const boldParticles = particles.slice(0, Math.floor(particles.length * 0.2)); // 20% bold
const subtleParticles = particles.slice(Math.floor(particles.length * 0.2)); // 80% subtle

// Subtle particles: Gentle coalescence
timeline.to(subtleParticles, {
  opacity: 1,
  scale: 1,
  x: (i, target) => target.targetX,
  y: (i, target) => target.targetY,
  duration: 0.6,
  stagger: {
    amount: 1.0,
    from: "start" // SEQUENTIAL, not random (Disney's Staging)
  },
  ease: "power2.inOut" // Gentle motion
});

// Bold particles: Dramatic arrival (emotional punctuation)
timeline.fromTo(boldParticles, {
  opacity: 0,
  scale: 0,
  x: (i, target) => target.initialX,
  y: (i, target) => target.initialY
}, {
  opacity: 1,
  scale: 1,
  x: (i, target) => target.targetX,
  y: (i, target) => target.targetY,
  duration: 0.4, // Faster than subtle
  stagger: {
    amount: 0.3,
    from: "center" // Explode from center
  },
  ease: "back.out(1.7)", // Overshoot for drama
}, "-=0.5"); // Overlap by 0.5s (The Stitch Pattern)
```

### Text Crystallization Effect

**Given** zone text needs to emerge from the mist
**When** particles coalesce
**Then** text crystallizes progressively:

```javascript
// Zone 0-1 text: Heavy blur → sharp
timeline.fromTo(".zone-0-1 .zone-text", {
  filter: "blur(12px)",
  opacity: 0.3
}, {
  filter: "blur(0px)",
  opacity: 1,
  duration: 1.5,
  ease: "power2.inOut",
  stagger: 0.2
}, "-=1.0"); // Overlap with particle animation
```

### Performance Safeguards

**Given** low-end devices may struggle
**When** the particle system initializes
**Then** performance detection occurs:

```javascript
// Detect hardware capability
const hardwareConcurrency = navigator.hardwareConcurrency || 2;
const isLowEnd = hardwareConcurrency < 4 || isMobile;

if (isLowEnd) {
  // Reduce particle count by 50%
  particleCount = Math.floor(particleCount * 0.5);

  // Skip spiral motion, use direct interpolation
  useSpiralMotion = false;
}
```

**And** FPS monitoring is active:
```javascript
let fps = 60;
let frameCount = 0;
let lastTime = performance.now();

function measureFPS() {
  frameCount++;
  const currentTime = performance.now();

  if (currentTime >= lastTime + 1000) {
    fps = frameCount;
    frameCount = 0;
    lastTime = currentTime;

    // If FPS < 30 for 2+ seconds, reduce complexity
    if (fps < 30 && performance.now() - startTime > 2000) {
      simplifyAnimation();
    }
  }

  requestAnimationFrame(measureFPS);
}

function simplifyAnimation() {
  // Kill spiral motion
  gsap.killTweensOf(".map-particle");

  // Simple fade-in fallback
  gsap.to(".map-particle", {
    opacity: 1,
    duration: 0.3,
    ease: "power1.out"
  });
}
```

### Accessibility Support

**Given** users may have motion sensitivities
**When** `prefers-reduced-motion: reduce` is detected
**Then** particles instantaneously appear at final positions:

```javascript
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

if (prefersReducedMotion.matches) {
  // Instant appearance, no animation
  gsap.set(".map-particle", {
    opacity: 1,
    scale: 1,
    x: (i, target) => target.targetX,
    y: (i, target) => target.targetY
  });
} else {
  // Full animation sequence
  animateFormation();
}
```

**And** screen reader announcements are provided:
```html
<div class="territory-map" role="img" aria-label="Territory Map showing learning journey from confusion to confidence. Particles coalesce to form 5 zones representing different stages of AI proficiency.">
```

### Memory Management

**Given** memory management is critical for performance
**When** the particle animation completes
**Then** cleanup occurs:

```javascript
cleanup() {
  // Kill ScrollTrigger
  if (this.scrollTrigger) {
    this.scrollTrigger.kill();
  }

  // Clear will-change to release GPU resources
  gsap.set(".map-particle", {
    willChange: "auto"
  });

  // Clear transform values
  gsap.set(".map-particle", {
    clearProps: "transform, opacity"
  });

  // Remove particles from DOM
  this.particles.forEach(p => p.remove());
}
```

**And** no memory leaks occur over 10-minute continuous scroll sessions:
- All GSAP timelines are properly killed
- Event listeners are removed
- Particles are removed from DOM
- ScrollTrigger instances are cleaned up

### Experiential Acceptance Criteria

**Given** 5 users test this section
**When** the particles coalesce
**Then** 4/5 users should express surprise, wonder, or say "whoa"

**Given** analytics tracking is installed (Story 0.2)
**When** users scroll through the Territory Map
**Then** the following metrics are tracked:
- `map_formation_start`: When particle animation begins
- `map_formation_complete`: When all particles reach targets
- `map_time_spent`: Duration in Territory Map section
- **Target**: 70% of users scroll to map completion
- **Target**: Average time in section > 30 seconds

## Tasks / Subtasks

- [x] Create MapParticleSystem class architecture (AC: Particle system initialization)
  - [x] Implement init() method with device detection
  - [x] Calculate target positions for all particles
  - [x] Create particle DOM elements with initial state
  - [x] Store target coordinates on each particle

- [x] Style particles with CSS (AC: Particle styling)
  - [x] Create .map-particle class with radial gradient
  - [x] Add mobile responsive styles (2px particles)
  - [x] Apply will-change for GPU acceleration
  - [ ] Test particle visibility on black background (BLOCKED: HTML loading issue)

- [x] Implement chaos → order animation (AC: Chaos → Order animation)
  - [x] Create ScrollTrigger configuration with scrub: 0.3
  - [x] Add pre-reveal anticipation (0.3s scale pulse)
  - [x] Implement sequential coalescence (from: "start", not random)
  - [x] Apply 80/20 emotional punctuation (subtle + bold particles)
  - [x] Add overlap timing (-=0.5s for "The Stitch Pattern")
  - [ ] Test animation feels smooth and organic (BLOCKED: HTML loading issue)

- [x] Add text crystallization effects (AC: Text crystallization)
  - [x] Animate blur: 12px → 0px for Zone 0-1 text
  - [x] Stagger text reveals by zone
  - [x] Overlap text animation with particle coalescence

- [x] Implement performance safeguards (AC: Performance safeguards)
  - [x] Add hardware capability detection
  - [x] Implement FPS monitoring
  - [x] Create fallback animation for low-end devices
  - [ ] Test on mobile devices (45fps+ target) (BLOCKED: HTML loading issue)
  - [ ] Test on desktop (60fps target) (BLOCKED: HTML loading issue)

- [x] Add accessibility support (AC: Accessibility support)
  - [x] Detect prefers-reduced-motion
  - [x] Implement instant-appear fallback
  - [x] Add ARIA labels for screen readers
  - [ ] Test with screen reader (VoiceOver/NVDA) (BLOCKED: HTML loading issue)
  - [ ] Test keyboard navigation through zones (BLOCKED: HTML loading issue)

- [x] Implement memory management (AC: Memory management)
  - [x] Create cleanup() method
  - [x] Kill ScrollTrigger instances
  - [x] Clear will-change properties
  - [x] Remove particles from DOM
  - [ ] Test for memory leaks (10-minute scroll session) (BLOCKED: HTML loading issue)

## Dev Notes

### Critical Architecture Decisions

**From Territory Map Scroll Experience Specification**:
- This story implements **Zone 0-1 (Wilderness)** particle drift animation ONLY
- Zone-specific techniques (snap, morph, mirror) are deferred to Stories 2.2b, 2.2c, 2.2d
- Scrub value: 0.3 (fast, light) for mystery → curiosity emotion
- Animation duration: 0.6s (subtle), 0.4s (bold) - NOT 2s as in original story

**Why This Scope?**
The Territory Map specification defines a "7-Zone Technique Palette" where each zone has unique choreography. Implementing all zones in Story 2.2 would violate Disney's Staging principle and create a monotone, robotic animation. By focusing on Zone 0-1 first, we establish the particle system infrastructure while maintaining emotional differentiation.

### Zone-Specific Animation Reference

**Future stories will implement:**

| Story | Zone | Scrub | Animation | Emotion |
|-------|------|-------|-----------|---------|
| **2.2** | 0-1 | 0.3 | Particle Drift + Heavy Blur | Mystery → Curiosity |
| 2.2b | 2 | 0.5 | Snap Transitions | Transactional efficiency |
| 2.2c | 3 | 1.5 | Fluid Morphing | Dialogue and flow |
| 2.2d | 4 | 2.0 + pin | Mirror Pause + Hold | Contemplative breakthrough |

### GSAP Plugin Requirements

**Required plugins:**
- `gsap` (core, v3.12+)
- `ScrollTrigger` (scroll-based animation)
- **Optional but recommended**: `MotionPath` (for spiral motion, can be skipped for performance)

### Particle Distribution Algorithm

**Target position calculation:**
```javascript
// Assign particles to zones
const particlesPerZone = Math.floor(particleCount / 7); // 7 zones total
const zones = [
  { id: 0, centerX: -200, centerY: -100, radius: 150 },
  { id: 1, centerX: -50, centerY: -150, radius: 120 },
  { id: 2, centerX: 100, centerY: -100, radius: 130 },
  { id: 3, centerX: 150, centerY: 50, radius: 140 },
  { id: 4, centerX: 0, centerY: 100, radius: 160 },
  { id: 5, centerX: -150, centerY: 50, radius: 110 }, // Future zone
  { id: 6, centerX: -250, centerY: 0, radius: 100 }  // Future zone
];

particles.forEach((particle, index) => {
  const zoneIndex = Math.floor(index / particlesPerZone) % 7;
  const zone = zones[zoneIndex];

  // Random position within zone radius
  const angle = Math.random() * Math.PI * 2;
  const distance = Math.random() * zone.radius;

  particle.targetX = zone.centerX + Math.cos(angle) * distance;
  particle.targetY = zone.centerY + Math.sin(angle) * distance;

  // Initial chaos position
  particle.initialX = Math.random() * 2000 - 1000;
  particle.initialY = Math.random() * 2000 - 1000;
});
```

### Disney Principles Applied

**From Scroll Choreography Bible:**

1. **Anticipation (Principle 1)**: 0.3s pre-reveal scale pulse creates tension
2. **Staging (Principle 4)**: Sequential reveals (`from: "start"`), not random chaos
3. **Timing (Principle 3)**: Varied durations (0.6s subtle, 0.4s bold) create rhythm
4. **Follow-Through (Principle 2)**: Overshoot on bold particles (`back.out(1.7)`)
5. **Overlapping Action**: Text animation overlaps particle animation by 1.0s

### GSAP Emotional Choreography Alignment

**From GSAP Emotional Choreography Research:**

- **Motion = Narrative**: Particles tell the story of transformation from chaos to order
- **80/20 Rule**: 80% subtle particles (supporting), 20% bold particles (emotional punctuation)
- **Staggered Reading Rhythm**: Sequential particle arrival creates "conversational" timing
- **The Stitch Pattern**: Overlapping animations create flow, not hard cuts

### Testing Strategy

**Performance testing:**
1. Use Chrome DevTools Performance tab to record 60fps target
2. Test on physical devices (iPhone 12+, Samsung Galaxy S21+)
3. Monitor memory usage in Task Manager during 10-minute scroll session
4. Validate no memory leaks (heap snapshot before/after)

**Experiential testing:**
1. Recruit 5 users from target demographic
2. Ask: "What did this animation make you feel?"
3. Measure time spent in Territory Map section
4. Track scroll depth to map completion

**Accessibility testing:**
1. Test with VoiceOver (iOS) and NVDA (Windows)
2. Verify screen reader announces zone information
3. Test keyboard navigation through zones
4. Validate `prefers-reduced-motion` fallback works correctly

### Project Structure Notes

**File locations:**
```
/src/components/TerritoryMap/
├── TerritoryMap.html (from Story 2.1)
├── TerritoryMap.css (from Story 2.1)
├── TerritoryMap.js (zone interactions, Story 2.3)
├── MapParticles.js (THIS STORY)
└── Map.css (THIS STORY - particle styles)
```

**Alignment with unified project structure:**
- Follows component-based architecture defined in Story 1.1
- Uses CSS variables from `/src/styles/token.css` (Story 1.1)
- Integrates with GSAP config from `/src/utils/gsap-config.js` (Story 1.2)
- Uses performance utilities from `/src/utils/performance-optimizations.js` (Story 1.2)

### References

**Primary sources:**
- [Territory Map Scroll Experience Specification](/_bmad-output/implementation-artifacts/territory-map-scroll-experience-specification.md) - Complete 7-zone technique palette (lines 67-76, 81-133)
- [Scroll Choreography Bible](/_bmad-output/scroll-choreography-bible.md) - Disney's 12 principles (lines 52-106, 361-397)
- [GSAP Emotional Choreography Research](/_bmad-output/implementation-artifacts/gsap-emotional-choreography-research.md) - 80/20 rule, stagger patterns (lines 528-534, 147-166)
- [GSAP Scroll Choreography Synthesis](/_bmad-output/implementation-artifacts/gsap-scroll-choreography-synthesis.md) - Unified framework (lines 460-510)

**Epic story foundation:**
- [Epic 2](/_bmad-output/planning-artifacts/epics.md#epic-2) - Territory Map WHOA Moment (lines 551-653)
- [Story 2.2](/_bmad-output/planning-artifacts/epics.md#story-22) - Original story requirements (lines 652-738)

**Previous story:**
- [Story 2.1](/_bmad-output/implementation-artifacts/2-1-create-territory-map-svg-structure.md) - Map HTML structure and zone definitions

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

**BLOCKING ISSUE - HTML Loading Failure:**
- **Error:** `SyntaxError: Unexpected identifier 'as'` prevents main.js from executing
- **Impact:** TerritoryMap HTML never inserted into DOM, all tests fail
- **Root Cause:** TypeScript syntax in Playwright test files inside `page.evaluate()` calls
- **Attempts:**
  1. Fixed MapParticles.js import (changed from `gsap` to `gsap-config.js`)
  2. Removed most `as any` type assertions from story-2-2-visual.spec.ts
  3. Created debug-html-loading.spec.ts to isolate issue
  4. Confirmed TerritoryMap section not loading (`.territory-map` selector returns null)
  5. Manual HTML insertion test SUCCESSFUL - HTML files are valid
- **Status:** Implementation complete, tests written, but cannot validate due to HTML loading blocker

### Completion Notes List

**Implementation Complete (2026-01-17):**

✅ **Code Implementation: ALL TASKS COMPLETE**
1. Created MapParticles.js with full particle system:
   - Device detection (desktop: 300, mobile: 105 particles)
   - 80/20 emotional punctuation (subtle/bold particle split)
   - Disney principles: Anticipation, Staging, Follow-Through, Overlapping Action
   - ScrollTrigger with scrub: 0.3 for mystery→curiosity arc
   - Text crystallization (blur: 12px → 0px)
   - Performance safeguards (hardware detection, FPS monitoring, low-end fallback)
   - Accessibility (prefers-reduced-motion, ARIA labels)
   - Memory management (cleanup method with ScrollTrigger killing)

2. Created Map.css with particle styling:
   - Radial gradient backgrounds
   - Mobile responsive (2px particles on mobile)
   - will-change for GPU acceleration

3. Updated TerritoryMap.html:
   - Added zone-text classes for text crystallization
   - Updated ARIA labels with particle description

4. Updated TerritoryMap.css:
   - Imported Map.css for particle styles

5. Updated main.js:
   - Imported MapParticleSystem
   - Initialized particle system on window.load

6. Created comprehensive test suite (story-2-2-visual.spec.ts):
   - 17 tests covering all AC
   - Desktop/mobile particle counts
   - Styling validation
   - Animation behavior
   - Performance checks
   - Accessibility validation
   - Memory management tests

7. Created debug test (debug-html-loading.spec.ts):
   - Isolated HTML loading issue
   - Confirmed manual insertion works

**Known Issues:**
❌ **BLOCKING:** TypeScript syntax error in test files prevents main.js execution
   - Error: `SyntaxError: Unexpected identifier 'as'`
   - Files affected: Playwright test files with `page.evaluate()` containing TypeScript syntax
   - Impact: Cannot validate implementation until tests run
   - Next steps: Remove all remaining TypeScript syntax from test files

**File List**

**Created:**
- `/src/components/TerritoryMap/MapParticles.js` - Full particle system implementation (341 lines)
- `/src/components/TerritoryMap/Map.css` - Particle styling (15 lines)
- `/tests/screenshots/story-2-2-visual.spec.ts` - Comprehensive test suite (543 lines, 17 tests)
- `/tests/debug-html-loading.spec.ts` - Debug test for HTML loading issue (155 lines, 7 tests)

**Modified:**
- `/src/components/TerritoryMap/TerritoryMap.html` - Added zone-text classes, updated ARIA labels
- `/src/components/TerritoryMap/TerritoryMap.css` - Imported Map.css
- `/src/main.js` - Imported and initialized MapParticleSystem

**Debug Files (for investigation):**
- `/check-particles.js` - Debug script to verify particle container
- `/diagnose-hero.js` - Existing debug file
- `/check-console.js` - Existing debug file
