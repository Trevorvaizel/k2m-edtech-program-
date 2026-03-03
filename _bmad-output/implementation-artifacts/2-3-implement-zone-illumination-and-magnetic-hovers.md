# Story 2.3: Implement Zone Illumination and Magnetic Hovers

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a visitor,
I want to see zones illuminate sequentially and react to my cursor with magnetic hover effects,
So that I can interact with the map and explore each zone to discover my learning journey.

## Acceptance Criteria

### Zone Illumination System

**Given** the particle system is working (Story 2.2 is in-progress with implementation complete, validation pending)
**Note:** Zone illumination can be implemented in parallel; particle animation timing will be coordinated once Story 2.2 validation is unblocked.

**When** I add zone illumination to the timeline

**Then** zones animate in sequence after particle formation:

```javascript
// Zone illumination animation (separate ScrollTrigger from anticipatory pin)
// NOTE: This is a SECOND ScrollTrigger on the same .territory-map section
// ScrollTrigger handles multiple triggers on the same element automatically
const zoneTimeline = gsap.timeline({
  scrollTrigger: {
    trigger: ".territory-map",
    start: "center center", // Zones illuminate when map is centered (after particle coalescence completes)
    end: "bottom center",
    scrub: 1
  }
});

// Sequential zone illumination (Disney's Staging Principle)
zoneTimeline.fromTo(".zone", {
  opacity: 0,
  scale: 0.8
}, {
  opacity: 1,
  scale: 1,
  duration: 1,
  stagger: 0.3, // 300ms between each zone
  ease: "back.out(1.7)" // Elastic feel
});
```

**And** the illumination sequence follows emotional arc:
1. Zone 0 illuminates first (confusion → awareness)
2. Zone 1 illuminates second (curiosity)
3. Zone 2 illuminates third (delegation)
4. Zone 3 illuminates fourth (collaboration)
5. Zone 4 illuminates last (THE GOAL - director zone)

**And** Zone 4 stands out with ocean mint accent (#40E0D0)

**And** illumination timing creates rhythmic "countdown to breakthrough" feeling

### Magnetic Hover Effects

**Given** zones need to be interactive

**When** I implement `initZoneHovers()` function in `/src/components/TerritoryMap/TerritoryMap.js`

**Then** each zone has mousemove event listener that creates magnetic effect:

```javascript
// Integration point: Called from TerritoryMap.init() after zone illumination
function initZoneHovers() {
  const zones = document.querySelectorAll('.zone');

  zones.forEach(zone => {
    zone.addEventListener('mousemove', (e) => {
      const rect = zone.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      const mouseX = e.clientX - centerX;
      const mouseY = e.clientY - centerY;

      // Move zone toward cursor (magnetic effect)
      gsap.to(zone, {
        x: mouseX / 5, // Divide for subtlety (not aggressive)
        y: mouseY / 5,
        scale: 1.05,
        duration: 0.5,
        ease: "power2.out"
      });
    });

    zone.addEventListener('mouseleave', () => {
      // Return to original position
      gsap.to(zone, {
        x: 0,
        y: 0,
        scale: 1,
        duration: 0.5,
        ease: "power2.out"
      });
    });
  });
}
```

**And** the magnetic effect is subtle (x/5, y/5), not aggressive

**And** scale increases to 1.05 for emphasis

**And** smooth transitions use `power2.out` easing

**And** performance is maintained using GPU-accelerated transforms only

**And** the initialization sequence is:

```javascript
// In /src/components/TerritoryMap/TerritoryMap.js
class TerritoryMap {
  constructor() {
    this.particleSystem = null; // From Story 2.2
  }

  init() {
    // Step 1: Initialize particle system (Story 2.2)
    this.particleSystem = new MapParticleSystem('.particle-container');
    this.particleSystem.init();

    // Step 2: Initialize zone animations (Story 2.3)
    this.initZoneIllumination();
    this.initZoneHovers();
    this.initTooltips();
    this.initZone4Emphasis();
    this.initBackgroundDimming();
  }

  initZoneIllumination() {
    // From Zone Illumination System AC
    const zoneTimeline = gsap.timeline({
      scrollTrigger: {
        trigger: ".territory-map",
        start: "center center",
        end: "bottom center",
        scrub: 1
      }
    });

    zoneTimeline.fromTo(".zone", {
      opacity: 0,
      scale: 0.8
    }, {
      opacity: 1,
      scale: 1,
      duration: 1,
      stagger: 0.3,
      ease: "back.out(1.7)"
    });
  }

  initZoneHovers() {
    // From Magnetic Hover Effects AC
    // ... (magnetic hover implementation)
  }

  initTooltips() {
    // From Zone Tooltips AC
    // ... (tooltip implementation)
  }

  initZone4Emphasis() {
    // From Zone 4 Emphasis AC
    // ... (Zone 4 glow implementation)
  }

  initBackgroundDimming() {
    // From Anticipatory Pin AC
    // ... (background dimming implementation)
  }

  cleanup() {
    // Kill all ScrollTriggers and tweens
    gsap.killTweensOf(".zone");
    ScrollTrigger.getAll().forEach(trigger => trigger.kill());
  }
}

// Initialize in main.js
window.addEventListener('load', () => {
  const territoryMap = new TerritoryMap();
  territoryMap.init();
});
```

### Zone Tooltips for Personalization

**Given** users need guidance on their current zone

**When** I add zone tooltips

**Then** zones 0 and 1 display tooltips on hover:

```javascript
// Tooltips appear for Zone 0 and 1 (most users start here)
const zonesWithTooltips = [
  { zone: '.zone-0', text: "You might be here" },
  { zone: '.zone-1', text: "You might be here" }
];

zonesWithTooltips.forEach(({ zone, text }) => {
  const tooltip = document.createElement('div');
  tooltip.className = 'zone-tooltip';
  tooltip.textContent = text;
  tooltip.style.opacity = '0';

  document.querySelector(zone).appendChild(tooltip);

  // Fade in tooltip on hover
  document.querySelector(zone).addEventListener('mouseenter', () => {
    gsap.to(tooltip, {
      opacity: 1,
      duration: 0.3,
      ease: "power2.out"
    });
  });

  // Fade out on leave
  document.querySelector(zone).addEventListener('mouseleave', () => {
    gsap.to(tooltip, {
      opacity: 0,
      duration: 0.3,
      ease: "power2.out"
    });
  });
});
```

**And** tooltips use ocean mint accent (#20B2AA) for brand consistency

**And** tooltips position near the zone with `position: absolute`

**And** zones 2, 3, 4 do NOT display tooltips (users rarely start there)

**And** tooltips help users identify their starting point through personalization

### Zone 4 "Breakthrough" Emphasis

**Given** Zone 4 represents the breakthrough moment (Director zone)

**When** Zone 4 illuminates

**Then** it receives special visual emphasis:

```javascript
// Zone 4 gets ocean mint glow (breakthrough moment)
gsap.to(".zone-4", {
  boxShadow: "0 0 30px rgba(64, 224, 208, 0.6)", // Warm ocean mint glow
  duration: 1.5,
  ease: "power2.inOut",
  scrollTrigger: {
    trigger: ".zone-4",
    start: "top 70%",
    toggleActions: "play reverse play reverse"
  }
});
```

**And** the glow pulses subtly (scale: 1.02 → 1, yoyo: true, repeat: -1)

**And** this creates the emotional climax of the Territory Map experience

**And** users understand Zone 4 is the aspirational goal

### Anticipatory Pin with Background Dimming

**Given** the anticipatory pin is needed to create WHOA moment

**When** I configure the ScrollTrigger pin for the Territory Map section

**Then** `anticipatePin: 1` is set:

```javascript
// Anticipatory pin ScrollTrigger (FIRST trigger - handles pinning + background dim)
// This is separate from zone illumination ScrollTrigger
scrollTrigger: {
  trigger: ".territory-map",
  start: "top center", // Pin starts when section enters center
  end: "bottom center",
  scrub: 1,
  anticipatePin: 1, // Pre-calculate pin for smooth transition
  pin: true // Pin during particle → zone animation sequence
}
```

**And** the two ScrollTriggers work together:
1. **Anticipatory Pin Trigger** (`start: "top center"`) - Handles pinning and background dim
2. **Zone Illumination Trigger** (`start: "center center"`) - Handles zone animation sequence
3. **GSAP automatically sequences** multiple ScrollTriggers on the same element

**And** the background gradually dims before the reveal:

```javascript
// Background dimming creates focus (anticipation)
gsap.to(".territory-map-container", {
  backgroundColor: "#000000", // Pure black
  duration: 2,
  ease: "power2.inOut",
  scrollTrigger: {
    trigger: ".territory-map",
    start: "top bottom",
    end: "center center",
    scrub: 1
  }
});
```

**And** the transition feels smooth, not abrupt

**And** Lenis smooth scroll feels luxurious during the slowdown

### Performance Requirements

**Given** performance is critical for 60fps desktop / 45fps mobile

**When** I implement all hover effects

**Then** the following performance targets are met:

**Quantifiable Metrics:**
- Chrome DevTools Performance: 60fps desktop during zone hover (no drops below 55fps)
- Chrome DevTools Performance: 45fps mobile during tap highlights (no drops below 40fps)
- Memory allocation: <50MB total for all zone hover handlers
- Event handler lag: <16ms (1 frame) between mousemove and visual response
- Long task duration: No tasks >50ms during hover animations

**Validation Method:**
```javascript
// Performance test in Chrome DevTools
console.time('hover-performance');
// Trigger 10 simultaneous zone hovers
// Measure: Memory should remain stable (±20MB)
console.timeEnd('hover-performance');

// FPS monitoring during hover
let frameCount = 0;
let lastTime = performance.now();

function measureFPS() {
  frameCount++;
  const currentTime = performance.now();
  if (currentTime >= lastTime + 1000) {
    const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
    console.log(`Hover FPS: ${fps}`);
    if (fps < 55) console.warn('FPS below target!');
    frameCount = 0;
    lastTime = currentTime;
  }
  requestAnimationFrame(measureFPS);
}
```

**And** the following performance optimizations are applied:

1. **GPU acceleration only**:
   - Use `transform: translate3d()` or `x, y` (NOT `left, top`)
   - Animate `scale` and `opacity` (NOT `width, height`)
   - Apply `will-change: transform` during animation
   - Remove `will-change` after animation completes

2. **Throttled mouse events**:
   ```javascript
   let ticking = false;

   zone.addEventListener('mousemove', (e) => {
     if (!ticking) {
       window.requestAnimationFrame(() => {
         // Handle magnetic effect
         updateMagneticEffect(zone, e);
         ticking = false;
       });

       ticking = true;
     }
   });
   ```

3. **Reduced complexity on mobile**:
   ```javascript
   // Use GSAP MatchMedia for mobile detection (consistent with CSS breakpoint)
   ScrollTrigger.matchMedia({
     // Desktop
     "(min-width: 769px)": function() {
       // Magnetic hover only on desktop
       initMagneticHovers();
     },

     // Mobile
     "(max-width: 768px)": function() {
       // Tap-to-highlight on mobile (touch doesn't have "hover")
       initTouchHighlights();
     }
   });
   ```

   **Note:** MatchMedia is preferred over `window.innerWidth` because:
   - Matches CSS media query breakpoint exactly (@media max-width: 768px)
   - Automatically handles resize events
   - Integrates with GSAP ScrollTrigger lifecycle

4. **Memory cleanup**:
   ```javascript
   cleanup() {
     // Remove all event listeners
     zones.forEach(zone => {
       zone.removeEventListener('mousemove', handleMagneticHover);
       zone.removeEventListener('mouseleave', handleMouseLeave);
       if (isMobile) {
         zone.removeEventListener('touchstart', handleTouch);
         zone.removeEventListener('touchend', handleTouchEnd);
       }
     });

     // Kill all GSAP tweens
     gsap.killTweensOf(".zone");

     // Clear will-change
     gsap.set(".zone", { willChange: "auto" });
   }
   ```

### Accessibility Support

**Given** accessibility is required for WCAG AA compliance

**When** screen readers encounter zones

**Then** the following accessibility features are implemented:

1. **Keyboard navigation**:
   ```html
   <div class="zone" tabindex="0" role="button"
        aria-label="Zone 0: The Unaware. AI isn't for me. Where most students start.">
     <!-- Zone content -->
   </div>
   ```

2. **Keyboard hover effects + activation**:
   ```javascript
   zone.addEventListener('focus', () => {
     gsap.to(zone, { scale: 1.05, duration: 0.3 });
   });

   zone.addEventListener('blur', () => {
     gsap.to(zone, { scale: 1, duration: 0.3 });
   });

   // Keyboard activation (Enter/Space keys)
   zone.addEventListener('keydown', (e) => {
     if (e.key === 'Enter' || e.key === ' ') {
       e.preventDefault();
       // Same effect as mouse hover - scale up
       gsap.to(zone, {
         scale: 1.05,
         duration: 0.2,
         yoyo: true,
         repeat: 1
       });

       // If zone has tooltip, show it
       const tooltip = zone.querySelector('.zone-tooltip');
       if (tooltip) {
         gsap.to(tooltip, { opacity: 1, duration: 0.3 });
       }
     }
   });
   ```

3. **Screen reader announcements**:
   ```html
   <div aria-live="polite" aria-atomic="true" class="sr-only">
     Territory Map showing 5 zones of AI proficiency journey.
   </div>
   ```

4. **High contrast mode support**:
   ```css
   @media (prefers-contrast: high) {
     .zone {
       border: 2px solid #FFFFFF;
     }
   }
   ```

5. **Reduced motion fallback**:
   ```javascript
   const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

   if (prefersReducedMotion.matches) {
     // Instant appearance, no animation
     gsap.set(".zone", { opacity: 1, scale: 1 });
   } else {
     // Full animation sequence
     animateZoneIllumination();
   }
   ```

### Experiential Acceptance Criteria

**Given** 5 users test this section

**When** they interact with the Territory Map

**Then**:
- 4/5 users should identify their current zone (0 or 1)
- 4/5 users should hover over multiple zones to explore
- 3/5 users should mention Zone 4 as the "goal" or "where I want to be"
- Users should report feeling "curious" or "motivated" after exploring zones

**Given** analytics tracking is installed (Story 0.2)

**When** users interact with zones

**Then** the following metrics are tracked:
- `zone_hover_count`: Which zones users hover over most
- `zone_time_spent`: Duration spent on each zone
- `zone_4_focus_rate`: How many users hover over Zone 4
- **Target**: 80% of users hover over 3+ zones
- **Target**: 60% of users hover over Zone 4 (aspirational goal)

## Tasks / Subtasks

- [ ] Implement zone illumination system (AC: Zone illumination)
  - [ ] Create sequential zone animation with stagger: 0.3
  - [ ] Apply back.out(1.7) easing for elastic feel
  - [ ] Set duration: 1 for each zone
  - [ ] Test illumination creates emotional arc (mystery → breakthrough)

- [ ] Create magnetic hover effects (AC: Magnetic hovers)
  - [ ] Add mousemove event listeners to all zones
  - [ ] Calculate cursor offset from zone center
  - [ ] Move zones toward cursor (x/5, y/5) for subtlety
  - [ ] Scale zones to 1.05 on hover
  - [ ] Add mouseleave handlers to return to original position
  - [ ] Use power2.out easing for smooth transitions

- [ ] Implement zone tooltips (AC: Zone tooltips)
  - [ ] Create tooltip elements for Zone 0 and Zone 1
  - [ ] Style tooltips with ocean mint accent (#20B2AA)
  - [ ] Add fade-in animation (opacity: 0 → 1 over 0.3s)
  - [ ] Position tooltips near zones with absolute positioning
  - [ ] Verify zones 2, 3, 4 do NOT have tooltips

- [ ] Add Zone 4 breakthrough emphasis (AC: Zone 4 emphasis)
  - [ ] Apply ocean mint glow box-shadow to Zone 4
  - [ ] Create subtle pulse animation (scale: 1.02 → 1, yoyo: true)
  - [ ] Set glow duration: 1.5s for elegance
  - [ ] Test Zone 4 stands out as aspirational goal

- [ ] Configure anticipatory pin (AC: Anticipatory pin)
  - [ ] Set anticipatePin: 1 in ScrollTrigger config
  - [ ] Add background dimming animation (#0A0A0A → #000000)
  - [ ] Pin Territory Map during particle → zone animation sequence
  - [ ] Test smooth scroll with Lenis integration

- [ ] Implement performance optimizations (AC: Performance)
  - [ ] Use GPU-accelerated properties only (transform, scale, opacity)
  - [ ] Apply will-change during animation, remove after
  - [ ] Throttle mouse events with requestAnimationFrame
  - [ ] Disable magnetic hovers on mobile (use tap-to-highlight)
  - [ ] Test 60fps desktop, 45fps mobile

- [ ] Add accessibility support (AC: Accessibility)
  - [ ] Add tabindex="0" and role="button" to zones
  - [ ] Implement keyboard focus/blur handlers
  - [ ] Add aria-labels to each zone
  - [ ] Create screen reader announcements (aria-live)
  - [ ] Add high contrast mode support
  - [ ] Implement prefers-reduced-motion fallback
  - [ ] Test with VoiceOver/NVDA screen readers

- [ ] Implement memory cleanup (AC: Performance)
  - [ ] Remove all event listeners in cleanup()
  - [ ] Kill GSAP tweens on zones
  - [ ] Clear will-change properties
  - [ ] Test no memory leaks (10-minute hover session)
  - Open Chrome DevTools → Performance Monitor
  - Hover over zones continuously for 10 minutes
  - Verify memory remains stable (±20MB)
  - Check for no upward trend indicating leaks

- [ ] Test experiential criteria (AC: Experiential)
  - [ ] Recruit 5 users for testing
  - [ ] Measure zone identification rate (target: 80%)
  - [ ] Measure zone exploration rate (target: 3+ zones)
  - [ ] Measure Zone 4 focus rate (target: 60%)
  - [ ] Track analytics metrics (hover count, time spent)

## Dev Notes

### Critical Architecture Decisions

**From Territory Map Scroll Experience Specification**:
- Zone illumination occurs AFTER particle coalescence (Story 2.2)
- Sequential stagger: 0.3s per zone creates "countdown to breakthrough"
- Magnetic hover uses x/5, y/5 for SUBTLETY (not aggressive)
- Zone 4 gets special ocean mint glow (#40E0D0) as aspirational goal
- Tooltips only on Zones 0-1 (where users actually start)

**Emotional Arc Applied**:
- Zone 0 (Unaware) → Illumination represents awareness
- Zone 1 (Observer) → Illumination represents curiosity
- Zone 2 (Delegator) → Illumination represents first steps
- Zone 3 (Collaborator) → Illumination represents partnership
- Zone 4 (Director) → ILLUMINATION = BREAKTHROUGH MOMENT (glow + pulse)

### Previous Story Intelligence (Story 2.2 Learnings)

**From Story 2.2 Particle System**:

**What Worked:**
- Sequential reveals (`from: "start"`) create better rhythm than random
- 80/20 emotional punctuation (subtle + bold) prevents monotone animation
- Overlapping animations (-=0.5s) create seamless flow (The Stitch Pattern)
- FPS monitoring catches performance issues early
- Hardware detection prevents crashes on low-end devices

**What to Avoid:**
- Don't use `ease: "none"` - always use eased animations
- Don't animate all zones simultaneously (violates Disney's Staging)
- Don't use aggressive magnetic values (x/1, y/1 is too strong - use x/5, y/5)
- Don't skip anticipatory pin - creates jarring transition
- Don't forget `will-change` cleanup - causes memory leaks

**Performance Patterns to Reuse:**
```javascript
// From Story 2.2: Throttled event handlers
let ticking = false;
if (!ticking) {
  window.requestAnimationFrame(() => {
    // Handle event
    ticking = false;
  });
  ticking = true;
}

// From Story 2.2: Memory cleanup pattern
cleanup() {
  this.scrollTrigger.kill();
  gsap.set(element, { willChange: "auto" });
  gsap.set(element, { clearProps: "transform, opacity" });
}
```

### GSAP Emotional Choreography Alignment

**From GSAP Emotional Choreography Research**:

**Copywriting-Choreography Model: Reveal-Emphasize Pattern**
- Zones REVEAL sequentially (anticipation)
- Zone 4 gets EMPHASIS (glow + pulse) as emotional punctuation
- This matches "Reveal-Emphasize" pattern from research

**80/20 Rule Applied:**
- 80% of zones (0-3) have subtle illumination
- 20% of zones (Zone 4) has BOLD emphasis (glow + pulse)
- Creates emotional hierarchy and guides attention

**Staggered Reading Rhythm:**
- Stagger: 0.3s between zones = "conversational" timing
- Not too fast (0.1s) = feels robotic
- Not too slow (0.5s) = feels sluggish
- 0.3s = natural, inviting

**Pacing: The Emotional Rhythm Engine**
- Zone illumination duration: 1s (moderate - trust, curiosity)
- Magnetic hover duration: 0.5s (fast - playful, responsive)
- Zone 4 glow duration: 1.5s (slow - premium, elegant)

### Disney Principles Applied

**From Scroll Choreography Bible**:

1. **Anticipation (Principle 1)**: Background dimming (#0A0A0A → #000000) creates tension before reveal

2. **Staging (Principle 4)**: Sequential zone illumination guides attention ONE zone at a time

3. **Timing (Principle 3)**: Varied durations create rhythm:
   - Zone illumination: 1s (moderate)
   - Magnetic hover: 0.5s (fast)
   - Zone 4 glow: 1.5s (slow)

4. **Follow-Through (Principle 2)**: Overshoot on zone scale (back.out(1.7))

5. **Overlapping Action**: Zone illumination overlaps with magnetic hover readiness

6. **Appeal**: Zone 4 glow creates visual beauty and aspirational quality

### GSAP Technical Patterns

**ScrollTrigger Configuration for Zone Illumination:**
```javascript
const zoneTimeline = gsap.timeline({
  scrollTrigger: {
    trigger: ".territory-map",
    start: "center center", // Zones illuminate when map is centered
    end: "bottom center",
    scrub: 1, // Smooth scroll control
    anticipatePin: 1 // Pre-calculate for smooth pinning
  }
});
```

**Magnetic Hover with Performance:**
```javascript
// Calculate offset from center
const rect = zone.getBoundingClientRect();
const centerX = rect.left + rect.width / 2;
const centerY = rect.top + rect.height / 2;
const mouseX = e.clientX - centerX;
const mouseY = e.clientY - centerY;

// Subtle magnetic effect (divide by 5)
gsap.to(zone, {
  x: mouseX / 5,
  y: mouseY / 5,
  scale: 1.05,
  duration: 0.5,
  ease: "power2.out",
  willChange: "transform" // GPU acceleration during animation
});
```

**Zone 4 Special Emphasis:**
```javascript
// Pulse animation creates "alive" feeling
gsap.to(".zone-4-glow", {
  scale: 1.02,
  opacity: 0.8,
  duration: 1.5,
  yoyo: true, // Pulse back and forth
  repeat: -1, // Infinite loop
  ease: "sine.inOut" // Gentle pulse
});
```

### Mobile Adaptation

**Critical Mobile Considerations:**

1. **Use GSAP MatchMedia for responsive behavior** (consistent with CSS):
   ```javascript
   // Mobile breakpoint matches CSS: @media (max-width: 768px)
   ScrollTrigger.matchMedia({
     // Desktop (769px+)
     "(min-width: 769px)": function() {
       // Magnetic hover with x/5, y/5 subtlety
       initMagneticHovers();

       // Slower, elegant zone illumination
       initZoneIllumination({
         stagger: 0.3,
         duration: 1.0
       });
     },

     // Mobile (≤768px)
     "(max-width: 768px)": function() {
       // Tap-to-highlight instead of magnetic hover
       initTouchHighlights();

       // Faster, snappier zone illumination
       initZoneIllumination({
         stagger: 0.15, // 50% faster
         duration: 0.6  // 40% shorter
       });
     }
   });
   ```

2. **Reduce glow intensity on mobile** (save battery):
   ```javascript
   // Inside Zone 4 emphasis, use MatchMedia for glow values
   ScrollTrigger.matchMedia({
     "(min-width: 769px)": function() {
       gsap.to(".zone-4", {
         boxShadow: "0 0 30px rgba(64, 224, 208, 0.6)", // Full glow
         duration: 1.5
       });
     },

     "(max-width: 768px)": function() {
       gsap.to(".zone-4", {
         boxShadow: "0 0 20px rgba(64, 224, 208, 0.4)", // Reduced glow
         duration: 1.0
       });
     }
   });
   ```

### Testing Strategy

**Performance testing:**
1. Chrome DevTools Performance tab - record 60fps desktop / 45fps mobile
2. Monitor memory usage during 10-minute hover session
3. Test throttled mouse events (no jank)
4. Validate `will-change` cleanup (no memory leaks)

**Experiential testing:**
1. 5 users from target demographic (Kenyan students)
2. Ask: "Which zone are you in?" (target: 80% identify zone 0-1)
3. Ask: "Where do you want to be?" (target: 60% say Zone 4)
4. Measure zone hover count (target: 3+ zones explored)
5. Track time spent in Territory Map section (target: >30s)

**Accessibility testing:**
1. VoiceOver (iOS) and NVDA (Windows) - announce zones correctly
2. Keyboard navigation - tab through zones, focus effects work
3. High contrast mode - zones remain visible
4. Reduced motion - zones appear instantly, no animation

**Cross-browser testing:**
1. Chrome (desktop + Android)
2. Safari (macOS + iOS)
3. Firefox (desktop)
4. Edge (desktop)

### Project Structure Notes

**File locations:**
```
/src/components/TerritoryMap/
├── TerritoryMap.html (from Story 2.1)
├── TerritoryMap.css (from Story 2.1)
├── TerritoryMap.js (THIS STORY - zone interactions)
├── MapParticles.js (from Story 2.2)
└── Map.css (from Story 2.2 - particle styles)
```

**Files to modify in this story:**
- `/src/components/TerritoryMap/TerritoryMap.js` - Add `initZoneIllumination()`, `initZoneHovers()`, `initTooltips()`
- `/src/components/TerritoryMap/TerritoryMap.css` - Add zone hover styles, tooltip styles, Zone 4 glow

**Dependencies:**
- GSAP v3.12+ (already installed via Story 1.2)
- ScrollTrigger plugin (already installed via Story 1.2)
- CSS variables from `/src/styles/token.css` (already created via Story 1.1)
- Performance utilities from `/src/utils/performance-optimizations.js` (already created via Story 1.2)

### References

**Primary sources:**
- [Territory Map Documentation](/docs/ai_proficiency_territory_map/01-the-territory.md) - Zone definitions and characteristics (lines 29-378)
- [GSAP Emotional Choreography Research](/_bmad-output/implementation-artifacts/gsap-emotional-choreography-research.md) - Reveal-Emphasize pattern, 80/20 rule (lines 122-145, 507-534)
- [Scroll Choreography Bible](/_bmad-output/scroll-choreography-bible.md) - Disney's 12 principles (lines 52-106, 361-397)
- [GSAP Scroll Choreography Synthesis](/_bmad-output/implementation-artifacts/gsap-scroll-choreography-synthesis.md) - Unified framework (lines 460-510)

**Epic story foundation:**
- [Epic 2](/_bmad-output/planning-artifacts/epics.md#epic-2) - Territory Map WHOA Moment (lines 551-653)
- [Story 2.3](/_bmad-output/planning-artifacts/epics.md#story-23) - Original story requirements (lines 741-803)

**Previous stories:**
- [Story 2.1](/_bmad-output/implementation-artifacts/2-1-create-territory-map-svg-structure.md) - Map HTML structure
- [Story 2.2](/_bmad-output/implementation-artifacts/2-2-build-particle-coalescence-system.md) - Particle system (learnings applied here)

**Story sequence context:**
- Story 2.0: Pre-map anticipation framing (sets up darkness)
- Story 2.1: Territory Map SVG structure (creates zones)
- Story 2.2: Particle coalescence (WHOA moment)
- **Story 2.3 (THIS STORY)**: Zone illumination + magnetic hovers (interaction + exploration)
- Story 2.4: Zone 5-7 "Coming Soon" placeholders (future roadmap)

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

### Completion Notes List

**Story Generation Method:**
Generated via create-story workflow in YOLO mode with comprehensive analysis of:
- Territory Map documentation (7 zones, characteristics, emotional journey)
- GSAP Emotional Choreography Research (award-winning site patterns)
- Scroll Choreography Bible (Disney principles + technical implementation)
- Story 2.2 learnings (particle system performance patterns)
- Epic requirements (zone illumination, magnetic hovers, tooltips)

**Key Design Decisions:**
1. Sequential zone illumination (stagger: 0.3s) creates emotional arc from confusion to breakthrough
2. Magnetic hover uses x/5, y/5 for subtlety (not aggressive)
3. Zone 4 gets special ocean mint glow as aspirational "breakthrough moment"
4. Tooltips only on Zones 0-1 (where users actually start)
5. Performance safeguards from Story 2.2 applied (throttled events, will-change cleanup)
6. Mobile adaptation: tap-to-highlight instead of magnetic hover
7. Full accessibility support (keyboard nav, screen readers, reduced motion)

**Disney Principles Applied:**
- Anticipation: Background dimming creates tension
- Staging: Sequential reveals guide attention
- Timing: Varied durations create rhythm
- Follow-Through: Overshoot on zone scale (back.out(1.7))
- Overlapping Action: Seamless flow between animations
- Appeal: Zone 4 glow creates beauty

**File List**

**To be created:**
- `/src/components/TerritoryMap/TerritoryMap.js` - Zone interaction logic

**To be modified:**
- `/src/components/TerritoryMap/TerritoryMap.css` - Zone hover styles, tooltip styles, Zone 4 glow

**Dependencies:**
- GSAP v3.12+ (already installed via Story 1.2)
- ScrollTrigger plugin (already installed via Story 1.2)
- CSS variables from `/src/styles/token.css` (already created via Story 1.1)
- Performance utilities from `/src/utils/performance-optimizations.js` (already created via Story 1.2)
