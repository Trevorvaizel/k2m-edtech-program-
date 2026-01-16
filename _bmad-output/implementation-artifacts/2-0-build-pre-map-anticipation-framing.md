# Story 2.0: Build Pre-Map Anticipation Framing

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a visitor,
I want to feel anticipation building as I scroll toward the Territory Map,
So that I experience emotional buildup that makes the WHOA moment feel earned.

## Acceptance Criteria

**Given** the Hero section animations are complete
**When** I create `/src/components/TerritoryMap/MapFraming.html`
**Then** a framing section exists before the Territory Map with:
  - Primary transition text: "Something is about to shift..."
  - Secondary reinforcement text: "We don't teach tools. We guide you through territory."
  - Subtle hint text: "Most students are in Zone 0 or 1 when they start."
**And** text reveals progressively as user scrolls (not all at once)
**And** the background gradually dims from soft black to pure black
**And** scroll naturally slows using `anticipatePin: 1`
**And** the section spans 30-40% of the scroll journey
**And** users feel anticipation, not shock

**Given** I need smooth transition
**When** I create `/src/components/TerritoryMap/MapFraming.js`
**Then** GSAP ScrollTrigger pins the section with `anticipatePin: 1`
**And** background animates from `#0A0A0A` to `#000000` based on scroll progress
**And** text fades in with staggered timing:
  - "Something is about to shift..." at 30% scroll
  - "We don't teach tools..." at 50% scroll
  - "Most students..." at 70% scroll
**And** the transition feels smooth, not abrupt
**And** Lenis smooth scroll feels luxurious during the slowdown

**Given** the framing reinforces the "You're not alone" message
**When** I add the hint text
**Then** "Most students are in Zone 0 or 1 when they start" connects Hero to Map
**And** users understand they're about to see their position
**And** this bridges validation (Hero) → revelation (Map)

**Given** the framing creates anticipation
**When** I scroll through this section
**Then** I feel something significant is coming
**And** the darkness creates focus and anticipation
**And** I'm prepared for the WHOA moment, not startled by it
**And** performance maintains 60fps desktop / 45fps mobile

**Experiential Acceptance Criteria:**
**Given** 5 users test this section
**When** asked "What do you expect to see next?"
**Then** 4/5 users should mention "a map" or "my position" or "where I am"

## Tasks / Subtasks

- [ ] 1. Create MapFraming HTML structure with progressive text reveals (AC: 1)
  - [ ] 1.1 Create `/src/components/TerritoryMap/MapFraming.html` file
  - [ ] 1.2 Add section container with class `map-framing` and appropriate ID
  - [ ] 1.3 Add primary text: "Something is about to shift..." with reveal class
  - [ ] 1.4 Add secondary text: "We don't teach tools. We guide you through territory." with reveal class
  - [ ] 1.5 Add hint text: "Most students are in Zone 0 or 1 when they start." with reveal class
  - [ ] 1.6 Use semantic HTML (section, h2, p elements)
  - [ ] 1.7 Add aria-label for accessibility
  - [ ] 1.8 Ensure text is readable on black background (WCAG AA contrast)

- [ ] 2. Create MapFraming CSS with background gradient (AC: 1, 3)
  - [ ] 2.1 Create `/src/components/TerritoryMap/MapFraming.css` file
  - [ ] 2.2 Set background gradient: `linear-gradient(180deg, #0A0A0A 0%, #000000 100%)`
  - [ ] 2.3 Set section dimensions: `min-height: 80vh` (30-40% of scroll journey)
  - [ ] 2.4 Center content with flexbox: `display: flex`, `align-items: center`, `justify-content: center`
  - [ ] 2.5 Add padding: `4rem` on desktop, `2rem` on mobile
  - [ ] 2.6 Style text with Space Grotesk (headings) and Inter (body)
  - [ ] 2.7 Add `text-align: center` for focused, anticipatory feel
  - [ ] 2.8 Set `position: relative` for ScrollTrigger pinning
  - [ ] 2.9 Add responsive font sizes with `clamp()`

- [ ] 3. Implement ScrollTrigger with anticipatory pin (AC: 2, 4)
  - [ ] 3.1 Create `/src/components/TerritoryMap/MapFraming.js` file
  - [ ] 3.2 Import GSAP and ScrollTrigger from utils
  - [ ] 3.3 Create `initMapFramingAnimations()` function
  - [ ] 3.4 Configure ScrollTrigger with `anticipatePin: 1`
  - [ ] 3.5 Set pin duration: `"+=1000"` (scroll distance for pinned section)
  - [ ] 3.6 Set `scrub: 1` for smooth scroll-controlled animation
  - [ ] 3.7 Configure start: `"top top"` (pin when section reaches top)
  - [ ] 3.8 Configure end: `"+=80vh"` (section spans 30-40% of scroll)
  - [ ] 3.9 Test scroll feels luxurious, not sluggish

- [ ] 4. Implement progressive text reveal animations (AC: 2, 3)
  - [ ] 4.1 Create GSAP timeline for text reveals
  - [ ] 4.2 Animate "Something is about to shift..." at 30% scroll progress
  - [ ] 4.3 Animate "We don't teach tools..." at 50% scroll progress
  - [ ] 4.4 Animate "Most students..." at 70% scroll progress
  - [ ] 4.5 Use `stagger: 0.5` between text elements for progressive reveal
  - [ ] 4.6 Set `duration: 1.5` for each text reveal (slow, anticipatory)
  - [ ] 4.7 Use `ease: "power3.out"` for smooth, gentle motion
  - [ ] 4.8 Animate from: `y: 30, opacity: 0` (fade in from below)
  - [ ] 4.9 Animate to: `y: 0, opacity: 1` (final visible state)

- [ ] 5. Implement background dimming animation (AC: 2, 4)
  - [ ] 5.1 Create background animation in timeline
  - [ ] 5.2 Animate gradient from soft black to pure black based on scroll progress
  - [ ] 5.3 Use GSAP to animate background color or opacity
  - [ ] 5.4 Start: `#0A0A0A` (soft black from Hero section)
  - [ ] 5.5 End: `#000000` (pure black for WHOA moment)
  - [ ] 5.6 Sync background dimming with text reveals
  - [ ] 5.7 Ensure transition is gradual, not abrupt (monitor scroll progress)
  - [ ] 5.8 Test darkness creates anticipation, not confusion

- [ ] 6. Implement mobile-specific optimizations (AC: 4)
  - [ ] 6.1 Add ScrollTrigger `matchMedia()` for mobile breakpoint
  - [ ] 6.2 Set mobile breakpoint: `(max-width: 768px)`
  - [ ] 6.3 Reduce pin duration on mobile (shorter scroll distance)
  - [ ] 6.4 Reduce text animation durations: `1s` vs `1.5s` desktop
  - [ ] 6.5 Reduce stagger values: `0.3s` vs `0.5s` desktop
  - [ ] 6.6 Simplify background animation on mobile (fewer gradients)
  - [ ] 6.7 Test on iPhone 12+ (iOS Safari)
  - [ ] 6.8 Test on Samsung Galaxy S21+ (Android Chrome)
  - [ ] 6.9 Verify mobile performance: 45fps+ maintained

- [ ] 7. Integrate with Lenis smooth scroll (AC: 2)
  - [ ] 7.1 Verify Lenis is initialized in main.js
  - [ ] 7.2 Ensure ScrollTrigger updates Lenis on scroll
  - [ ] 7.3 Test smooth scroll feels luxurious during slowdown
  - [ ] 7.4 Verify no jank or stutter when pin activates
  - [ ] 7.5 Test `anticipatePin: 1` creates smooth slowdown
  - [ ] 7.6 Verify no "hitting a wall" feeling
  - [ ] 7.7 Test on Safari (macOS and iOS) for conflicts
  - [ ] 7.8 Ensure document.hidden detection works (pause/resume)

- [ ] 8. Connect Hero validation to Map revelation (AC: 3, 4)
  - [ ] 8.1 Ensure "Most students..." text references Hero's "You're not alone" message
  - [ ] 8.2 Test framing creates bridge between validation and revelation
  - [ ] 8.3 Verify user understands they're about to see their position
  - [ ] 8.4 Check emotional flow: relief → anticipation → WHOA moment
  - [ ] 8.5 Test with users: ask "What do you expect to see next?"
  - [ ] 8.6 Verify 4/5 users mention map, position, or territory
  - [ ] 8.7 Adjust copy if users are confused about what's coming

- [ ] 9. Add performance monitoring and GPU acceleration (AC: 4)
  - [ ] 9.1 Import `enableGPU`, `disableGPU` from performance-optimizations.js
  - [ ] 9.2 Apply `will-change: transform, opacity` before animations
  - [ ] 9.3 Remove `will-change: auto` after animations complete
  - [ ] 9.4 Call `monitorPerformance()` to track FPS
  - [ ] 9.5 Verify desktop performance: 60fps consistent
  - [ ] 9.6 Verify mobile performance: 45fps+ maintained
  - [ ] 9.7 Check for memory leaks (no increasing node counts)
  - [ ] 9.8 Cleanup ScrollTrigger on page unload

- [ ] 10. Test experiential acceptance criteria (AC: 5)
  - [ ] 10.1 Recruit 5 users for testing
  - [ ] 10.2 Ask users to scroll through framing section naturally
  - [ ] 10.3 Ask: "What do you expect to see next?"
  - [ ] 10.4 Record responses: map, position, territory, or other
  - [ ] 10.5 Verify 4/5 users mention "a map" or "my position" or "where I am"
  - [ ] 10.6 If < 4/5, adjust copy or animations for clarity
  - [ ] 10.7 Test emotional response: anticipation vs shock
  - [ ] 10.8 Verify users feel prepared for WHOA moment, not startled

## Dev Notes

### Epic Context
This is the **first story** in Epic 2: Territory Map WHOA Moment. This story creates the emotional buildup before the particle coalescence animation. It bridges the validation from Hero (Epic 1) to the revelation in Territory Map (Epic 2, stories 2.1-2.3).

**Critical Dependencies:**
- Story 1.1 MUST be completed (design tokens, Vite build)
- Story 1.2 MUST be completed (GSAP + Lenis infrastructure, performance utilities)
- Story 1.3 MUST be completed (Hero HTML structure)
- Story 1.4 MUST be completed (Hero animations)
- Story 1.5 MUST be completed (Hero performance optimization)

**Why This Story Matters:**
Without anticipation, the WHOA moment feels abrupt or shocking. This story creates emotional buildup by:
1. Gradually darkening the background (creates focus)
2. Revealing text progressively (builds curiosity)
3. Slowing scroll naturally (signals something significant coming)
4. Connecting Hero's validation ("You're not alone") to Map's revelation ("Here's where you are")

The result: When particles coalesce in Story 2.2, users feel "revelation" not "surprise."

### Technical Requirements

#### Anticipatory Pin Pattern (Core of this story):

**ScrollTrigger Configuration:**
```javascript
// In MapFraming.js
import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';

export function initMapFramingAnimations() {
  // Pin section and slow scroll
  ScrollTrigger.create({
    trigger: '.map-framing',
    pin: true,
    start: 'top top',  // Pin when section reaches top of viewport
    end: '+=80vh',     // Section spans 30-40% of scroll journey (80vh ≈ 40%)
    scrub: 1,          // Smooth scroll-controlled animation
    anticipatePin: 1,  // Gradual slowdown, not "hitting a wall"
    onUpdate: (self) => {
      // Sync background dimming with scroll progress
      const darkness = self.progress; // 0 to 1
      gsap.set('.map-framing', {
        backgroundColor: `rgb(${10 * (1-darkness)}, ${10 * (1-darkness)}, ${10 * (1-darkness)})`
      });
    }
  });

  // Text reveal animations
  const timeline = gsap.timeline({
    scrollTrigger: {
      trigger: '.map-framing',
      start: 'top top',
      end: 'bottom bottom',
      scrub: 1
    }
  });

  // Progressive text reveals
  timeline.from('.framing-text-1', {  // "Something is about to shift..."
    y: 30,
    opacity: 0,
    duration: 1.5,
    scrollTrigger: {
      trigger: '.framing-text-1',
      start: 'top 70%',  // 30% scroll (approximate)
      toggleActions: 'play none none reverse'
    }
  })
  .from('.framing-text-2', {  // "We don't teach tools..."
    y: 30,
    opacity: 0,
    duration: 1.5,
    scrollTrigger: {
      trigger: '.framing-text-2',
      start: 'top 50%',  // 50% scroll
      toggleActions: 'play none none reverse'
    }
  }, '-=0.5')  // Overlap slightly with previous animation
  .from('.framing-text-3', {  // "Most students..."
    y: 30,
    opacity: 0,
    duration: 1.5,
    scrollTrigger: {
      trigger: '.framing-text-3',
      start: 'top 30%',  // 70% scroll
      toggleActions: 'play none none reverse'
    }
  }, '-=0.5');
}
```

**Why anticipatePin: 1:**
- `anticipatePin: 1` tells ScrollTrigger to gradually slow down scroll BEFORE pinning
- Without it: User hits section at full speed, then abruptly stops ("hitting a wall")
- With it: Scroll smoothly decelerates, user anticipates something significant
- Creates luxurious, premium feel (Awwwards-level detail)

**Background Dimming Technique:**
```javascript
// Option 1: Animate backgroundColor directly (simpler)
gsap.to('.map-framing', {
  backgroundColor: '#000000',  // From #0A0A0A (soft black)
  scrollTrigger: {
    trigger: '.map-framing',
    start: 'top center',
    end: 'bottom center',
    scrub: 1
  }
});

// Option 2: Animate overlay opacity (more control)
// HTML: <div class="darkness-overlay"></div>
gsap.to('.darkness-overlay', {
  opacity: 1,  // Gradually darken
  scrollTrigger: {
    trigger: '.map-framing',
    start: 'top center',
    end: 'bottom center',
    scrub: 1
  }
});
```

#### HTML Structure:
```html
<!-- MapFraming.html -->
<section class="map-framing" id="map-framing" aria-label="Territory Map Introduction">
  <div class="darkness-overlay"></div> <!-- Optional overlay for dimming -->

  <div class="framing-content">
    <h2 class="framing-text framing-text-1">
      Something is about to shift...
    </h2>

    <p class="framing-text framing-text-2">
      We don't teach tools. We guide you through territory.
    </p>

    <p class="framing-text framing-text-3">
      Most students are in Zone 0 or 1 when they start.
    </p>
  </div>
</section>
```

#### CSS Styling:
```css
/* MapFraming.css */
.map-framing {
  position: relative;
  min-height: 80vh; /* 30-40% of scroll journey */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  background: linear-gradient(180deg, #0A0A0A 0%, #000000 100%);
  text-align: center;
  z-index: 2; /* Above Hero, below Territory Map */
}

.darkness-overlay {
  position: absolute;
  inset: 0;
  background: #000000;
  opacity: 0; /* Animated by GSAP */
  pointer-events: none;
  z-index: 1;
}

.framing-content {
  position: relative;
  z-index: 2;
  max-width: 800px;
}

.framing-text {
  opacity: 0; /* Animated in by GSAP */
  color: var(--text-primary);
  margin-bottom: 2rem;
}

.framing-text-1 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 700;
  line-height: 1.2;
  color: var(--ocean-mint-primary); /* Ocean mint accent */
}

.framing-text-2,
.framing-text-3 {
  font-family: 'Inter', sans-serif;
  font-size: clamp(1rem, 2vw, 1.5rem);
  font-weight: 400;
  line-height: 1.6;
  color: var(--text-secondary);
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .map-framing {
    min-height: 60vh; /* Shorter on mobile */
    padding: 2rem 1rem;
  }

  .framing-text-1 {
    font-size: clamp(1.5rem, 6vw, 2.5rem);
  }

  .framing-text-2,
  .framing-text-3 {
    font-size: clamp(0.875rem, 4vw, 1.25rem);
  }
}
```

### Architecture Compliance

#### File Structure:
```
k2m-landing/
├── src/
│   ├── main.js                    # Entry point
│   ├── components/
│   │   ├── Hero/                  # Epic 1 (Foundation)
│   │   │   ├── Hero.html
│   │   │   ├── Hero.css
│   │   │   └── Hero.js
│   │   └── TerritoryMap/          # Epic 2 (Territory Map) - NEW for this story
│   │       ├── MapFraming.html    # THIS STORY - Pre-map anticipation
│   │       ├── MapFraming.css     # THIS STORY - Framing styles
│   │       ├── MapFraming.js      # THIS STORY - Anticipatory pin animations
│   │       ├── TerritoryMap.html  # Story 2.1 - Map structure
│   │       ├── TerritoryMap.css   # Story 2.1 - Map styles
│   │       ├── TerritoryMap.js    # Story 2.1 - Map interactions
│   │       ├── MapParticles.js    # Story 2.2 - Particle system
│   │       └── Map.css            # Story 2.1-2.3 - Shared map styles
│   ├── utils/
│   │   ├── gsap-config.js         # Story 1.2 - GSAP + ScrollTrigger
│   │   ├── lenis-config.js        # Story 1.2 - Lenis smooth scroll
│   │   └── performance-optimizations.js  # Story 1.2 - GPU, FPS helpers
│   └── styles/
│       └── token.css              # Story 1.1 - Design tokens
```

**New Files for This Story:**
- `/src/components/TerritoryMap/MapFraming.html` - Framing HTML structure
- `/src/components/TerritoryMap/MapFraming.css` - Framing styles
- `/src/components/TerritoryMap/MapFraming.js` - Anticipatory pin animations

**New Directory:**
- `/src/components/TerritoryMap/` - First file in TerritoryMap component directory

#### Import Patterns:
```javascript
// In main.js (add this after Hero initialization)
import { initMapFramingAnimations } from './components/TerritoryMap/MapFraming.js';

// Initialize after Hero section
window.addEventListener('load', () => {
  initHeroAnimations();     // From Epic 1
  initMapFramingAnimations(); // THIS STORY - New
});

// In MapFraming.js
import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';
import { enableGPU, disableGPU, monitorPerformance } from '../../utils/performance-optimizations.js';
```

#### Component Pattern:
- **Hero (Epic 1):** Self-contained component with HTML, CSS, JS
- **MapFraming (This Story):** Self-contained component with HTML, CSS, JS
- **TerritoryMap (Story 2.1):** Will share Map.css with MapFraming
- **MapParticles (Story 2.2):** Separate JS module for particle system

This modular approach allows:
- Independent development of each section
- Easy testing and debugging
- Code reusability (shared Map.css)
- Clear separation of concerns

### Library/Framework Requirements

#### GSAP ScrollTrigger anticipatePin (Core feature of this story):
**API Documentation:**
```javascript
ScrollTrigger.create({
  trigger: '.map-framing',
  pin: true,
  anticipatePin: 1,  // Smooth slowdown before pin
  start: 'top top',
  end: '+=80vh',
  scrub: 1
});
```

**How anticipatePin Works:**
1. User scrolls toward section
2. ScrollTrigger detects pin is coming up
3. Scroll gradually slows down over 1 second (`anticipatePin: 1`)
4. Section pins at top of viewport
5. User continues scrolling (section stays pinned)
6. End of pin reached, section unpins
7. Scroll resumes normal speed

**Benefits:**
- No "hitting a wall" feeling
- Luxurious, premium experience
- User anticipates something significant
- Awwwards-level polish

**Common Pitfalls:**
- Forgetting `scrub: 1` (animation jerky, not smooth)
- Pin duration too short (`end: '+=200'`) or too long (`end: '+=3000'`)
- Not testing on mobile (pin can cause layout issues)
- Safari conflicts (ensure Lenis and ScrollTrigger play nice)

#### GSAP Timeline for Progressive Reveals:
```javascript
const timeline = gsap.timeline({
  scrollTrigger: {
    trigger: '.map-framing',
    start: 'top top',
    end: 'bottom bottom',
    scrub: 1  // Frame-by-frame control
  }
});

// Progressive text reveals
timeline
  .from('.framing-text-1', {
    y: 30,
    opacity: 0,
    duration: 1.5,
    ease: 'power3.out'
  })
  .from('.framing-text-2', {
    y: 30,
    opacity: 0,
    duration: 1.5,
    ease: 'power3.out'
  }, '-=0.5')  // Overlap by 0.5s
  .from('.framing-text-3', {
    y: 30,
    opacity: 0,
    duration: 1.5,
    ease: 'power3.out'
  }, '-=0.5');
```

**Why Negative Delay (`-=0.5`):**
- Overlap animations slightly
- Creates smoother, more organic feel
- Text doesn't feel "step-by-step"
- Maintains anticipation without waiting too long

**Animation Timing Strategy:**
- 30% scroll: First text appears
- 50% scroll: Second text appears (overlapping with first)
- 70% scroll: Third text appears (overlapping with second)
- By 100% scroll: All text visible, background fully dark

### Testing Requirements

#### Performance Testing Checklist:

1. **Desktop Performance (60fps target):**
   - [ ] Open Chrome DevTools > Performance tab
   - [ ] Start recording and scroll through MapFraming section
   - [ ] Stop recording and check FPS graph
   - [ ] Verify 60fps maintained during anticipatory pin
   - [ ] Check for long tasks (>50ms) during background dimming
   - [ ] Verify no jank when ScrollTrigger pin activates
   - [ ] Test Lenis smooth scroll feels luxurious, not sluggish

2. **Mobile Performance (45fps+ target):**
   - [ ] Test on iPhone 12+ (iOS Safari)
   - [ ] Test on Samsung Galaxy S21+ (Android Chrome)
   - [ ] Enable FPS monitoring (Safari Web Inspector, Chrome Remote Debugging)
   - [ ] Verify 45fps+ during all animations
   - [ ] Test anticipatory pin on mobile (no layout issues)
   - [ ] Verify mobile text is readable (font sizes, contrast)
   - [ ] Check background dimming doesn't cause performance drop

3. **Cross-Browser Testing:**
   - [ ] Chrome (primary development browser): Pin works smoothly
   - [ ] Safari (macOS): Test for GSAP/Lenis conflicts during pin
   - [ ] Safari (iOS): Test mobile responsiveness and pin behavior
   - [ ] Firefox: Pin and animations work correctly
   - [ ] Edge: All features functional

4. **Animation Timing Validation:**
   - [ ] Scroll through section slowly (scrub effect)
   - [ ] Verify text reveals at correct scroll positions (30%, 50%, 70%)
   - [ ] Check background dims gradually, not abruptly
   - [ ] Test scroll slowdown feels smooth, not jerky
   - [ ] Verify no "hitting a wall" when pin activates
   - [ ] Check no animation desync after fast scrolling

5. **Mobile Optimization Validation:**
   - [ ] Verify `matchMedia()` is active on mobile
   - [ ] Check pin duration is shorter on mobile (if configured)
   - [ ] Verify text animations are faster on mobile (1s vs 1.5s)
   - [ ] Test background animation is simplified on mobile
   - [ ] Check no horizontal scrolling occurs
   - [ ] Verify touch interactions work smoothly

6. **Experiential User Testing (Critical for this story):**
   - [ ] Recruit 5 users from target demographic
   - [ ] Ask users to scroll through framing section naturally
   - [ ] Ask: "What do you expect to see next?"
   - [ ] Record responses (map, position, territory, or confused)
   - [ ] Verify 4/5 users mention "a map" or "my position" or "where I am"
   - [ ] Ask: "How did this section make you feel?" (target: anticipation, curiosity)
   - [ ] If < 4/5 understand what's coming, adjust copy or animations

7. **Accessibility Testing:**
   - [ ] Test with screen reader (VoiceOver, TalkBack)
   - [ ] Verify aria-label is announced correctly
   - [ ] Check text is readable with high contrast (WCAG AA)
   - [ ] Test keyboard navigation (Tab through section)
   - [ ] Verify `prefers-reduced-motion` is respected (future enhancement)

8. **Integration Testing:**
   - [ ] Test Hero section → MapFraming transition is smooth
   - [ ] Verify no layout shift when Hero ends and MapFraming begins
   - [ ] Check background gradient connects Hero (#0A0A0A) to MapFraming (#000000)
   - [ ] Test Lenis smooth scroll works across both sections
   - [ ] Verify FPS maintained across section boundary

9. **Memory Leak Testing:**
   - [ ] Open Chrome DevTools > Memory tab
   - [ ] Take heap snapshot before scrolling
   - [ ] Scroll through MapFraming section 10 times
   - [ ] Take heap snapshot after scrolling
   - [ ] Compare snapshots (look for increasing node counts)
   - [ ] Check for detached DOM nodes
   - [ ] Verify ScrollTrigger cleanup on page unload

10. **Safari-Specific Testing:**
    - [ ] macOS Safari: Anticipatory pin works smoothly
    - [ ] iOS Safari: No "snap back" behavior during pin
    - [ ] Test document.hidden detection (tab switch pause/resume)
    - [ ] Verify Lenis smooth scroll doesn't conflict with pin
    - [ ] Check no animation desync after tab switch

### Previous Story Intelligence

**Story 1.5 Performance Optimization (Critical patterns to apply):**
Story 1.5 established performance optimization patterns that MUST be applied to this story:

**Mobile Optimization Pattern:**
```javascript
// From Story 1.5 - Apply to MapFraming.js
ScrollTrigger.matchMedia({
  // Desktop
  '(min-width: 769px)': function() {
    // Full anticipatory pin effect
    ScrollTrigger.create({
      trigger: '.map-framing',
      pin: true,
      end: '+=80vh',  // Full pin duration
      anticipatePin: 1,
      scrub: 1
    });

    // Full text animations (1.5s duration)
    gsap.from('.framing-text', {
      y: 30,
      opacity: 0,
      duration: 1.5,
      stagger: 0.5
    });
  },

  // Mobile
  '(max-width: 768px)': function() {
    // Shorter pin duration
    ScrollTrigger.create({
      trigger: '.map-framing',
      pin: true,
      end: '+=50vh',  // Shorter on mobile
      anticipatePin: 1,
      scrub: 1
    });

    // Faster text animations (1s duration)
    gsap.from('.framing-text', {
      y: 20,
      opacity: 0,
      duration: 1,  // Shorter on mobile
      stagger: 0.3  // Smaller stagger
    });
  }
});
```

**Performance Monitoring Pattern:**
```javascript
// From Story 1.5 - Apply to MapFraming.js
import { monitorPerformance, enableGPU, disableGPU } from '../../utils/performance-optimizations.js';

export function initMapFramingAnimations() {
  // Start FPS monitoring
  monitorPerformance(); // Logs FPS every second

  // Enable GPU acceleration before animations
  const framingElements = document.querySelectorAll('.framing-text');
  enableGPU(); // Applies will-change: transform, opacity

  // Run animations
  // ... animation code here

  // Cleanup function
  function cleanup() {
    disableGPU(); // Removes will-change
    ScrollTrigger.getAll().forEach(trigger => trigger.kill());
  }

  // Cleanup on page unload
  window.addEventListener('beforeunload', cleanup);
}
```

**Safari Compatibility Pattern:**
```javascript
// From Story 1.5 - Ensure Safari compatibility
// Already configured in Story 1.2's gsap-config.js:
ScrollTrigger.config({
  ignoreMobileResize: true,
  autoRefreshEvents: "visibilitychange,DOMContentLoaded,load"
});

// Document hidden detection (already in Story 1.4)
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    // Pause animations
  } else {
    // Resume animations
  }
});
```

**What Story 1.5 Taught Us:**
1. Mobile animations must be 50% simpler than desktop
2. Performance monitoring (FPS counter) is essential for validation
3. GPU acceleration (enableGPU/disableGPU) prevents memory leaks
4. Safari compatibility requires specific ScrollTrigger config
5. Lighthouse audit validates optimization success

**Apply These Patterns to This Story:**
- Use `matchMedia()` for mobile/desktop split
- Call `monitorPerformance()` to track FPS
- Use `enableGPU()`/`disableGPU()` for clean memory management
- Test thoroughly on Safari (macOS and iOS)
- Target: 60fps desktop, 45fps mobile, Lighthouse 90+

**Story 1.4 Hero Animations (Text reveal patterns):**
Story 1.4 implemented text reveal animations with:
- GSAP timeline with ScrollTrigger (scrub: 1, start: "top 80%")
- Text reveal animations (y: 50, opacity: 0, stagger: 0.2, duration: 1)
- Ocean mint glow animation (text shadow 0 to 0.8 opacity)
- Living typography with 3-layer parallax (y: -30, -15, 0)

**Apply Similar Patterns to MapFraming:**
- Use GSAP timeline with ScrollTrigger for text reveals
- Animate from: `y: 30, opacity: 0` (smaller y than Hero)
- Use stagger: 0.5 between text elements (progressive reveal)
- Duration: 1.5s (slower than Hero for anticipatory feel)
- Ease: `power3.out` (smooth, gentle)

**Story 1.2 Infrastructure (Critical dependencies):**
- `/src/utils/gsap-config.js` - GSAP and ScrollTrigger configured
- `/src/utils/lenis-config.js` - Lenis smooth scroll active
- `/src/utils/performance-optimizations.js` - GPU, FPS, mobile detection helpers

**Story 1.1 Design Tokens (Visual consistency):**
- `/src/styles/token.css` - Color palette (pure black, soft black, ocean mint)
- Typography (Space Grotesk for headings, Inter for body)
- Use same CSS variables for consistency

### Latest Tech Information

#### GSAP ScrollTrigger anticipatePin (2025):
**Official Documentation:**
- [ScrollTrigger anticipatePin](https://greensock.com/docs/v3/Plugins/ScrollTrigger)
- Reduces "jerk" when pinning happens
- Values: 0 (no anticipation) to 1 (1 second anticipation)
- Recommended: `anticipatePin: 1` for luxurious feel

**Best Practices:**
1. Always use with `scrub: 1` for smooth animation
2. Test pin duration (too short = rushed, too long = boring)
3. Mobile devices: Consider shorter pin duration
4. Safari: Test for conflicts with Lenis smooth scroll

**Common Issues:**
- **Issue:** Pin causes layout shift
  - **Fix:** Set `position: fixed` on pinned element
- **Issue:** Pin doesn't release
  - **Fix:** Check `end` value is correct (use `+=` for scroll distance)
- **Issue:** Mobile scroll jank during pin
  - **Fix:** Reduce pin duration on mobile, use `matchMedia()`

#### GSAP Timeline Progressive Reveals (2025):
**Pattern for Staggered Text Reveals:**
```javascript
const timeline = gsap.timeline({
  scrollTrigger: {
    trigger: '.map-framing',
    start: 'top top',
    end: 'bottom bottom',
    scrub: 1
  }
});

// Progressive reveals with overlap
timeline
  .from('.text-1', {
    y: 30,
    opacity: 0,
    duration: 1.5,
    ease: 'power3.out'
  })
  .from('.text-2', {
    y: 30,
    opacity: 0,
    duration: 1.5,
    ease: 'power3.out'
  }, '-=0.5')  // Overlap by 0.5s
  .from('.text-3', {
    y: 30,
    opacity: 0,
    duration: 1.5,
    ease: 'power3.out'
  }, '-=0.5');
```

**Why Negative Delays Work:**
- `-=0.5` means "start 0.5s before previous animation ends"
- Creates organic, overlapping feel
- Text doesn't feel mechanical or step-by-step
- Maintains user anticipation without waiting too long

#### Background Dimming Techniques (2025):
**Option 1: Animate backgroundColor (Simpler)**
```javascript
gsap.to('.map-framing', {
  backgroundColor: '#000000',
  scrollTrigger: {
    trigger: '.map-framing',
    start: 'top center',
    end: 'bottom center',
    scrub: 1
  }
});
```

**Option 2: Animate overlay opacity (More control)**
```javascript
// HTML
<div class="map-framing">
  <div class="darkness-overlay"></div>
  <div class="content">...</div>
</div>

// CSS
.darkness-overlay {
  position: absolute;
  inset: 0;
  background: #000000;
  opacity: 0;
  pointer-events: none;
}

// JS
gsap.to('.darkness-overlay', {
  opacity: 1,
  scrollTrigger: {
    trigger: '.map-framing',
    start: 'top center',
    end: 'bottom center',
    scrub: 1
  }
});
```

**Performance Considerations:**
- `backgroundColor` animation: GPU-accelerated in modern browsers
- Overlay opacity: Also GPU-accelerated, more control over gradient
- Recommendation: Use overlay if you need gradient control, backgroundColor for simple dimming

#### Mobile Optimization for Pinning (2025):
**matchMedia Pattern for Pin Duration:**
```javascript
ScrollTrigger.matchMedia({
  // Desktop - Full pin duration
  '(min-width: 769px)': function() {
    ScrollTrigger.create({
      trigger: '.map-framing',
      pin: true,
      end: '+=80vh',  // 30-40% of scroll journey
      anticipatePin: 1,
      scrub: 1
    });
  },

  // Mobile - Shorter pin duration
  '(max-width: 768px)': function() {
    ScrollTrigger.create({
      trigger: '.map-framing',
      pin: true,
      end: '+=50vh',  // Shorter on mobile (user less patient)
      anticipatePin: 1,
      scrub: 1
    });
  }
});
```

**Why Mobile Pin Duration Should Be Shorter:**
- Mobile users have less patience
- Smaller screens = shorter scroll distances
- Battery concerns (longer pin = more CPU usage)
- Touch interactions different from mouse
- Mobile users prefer "get to the point"

### Project Context Reference

**Project Name:** k2m-edtech-program-
**Epic:** Epic 2: Territory Map WHOA Moment
**Story:** 2.0 - Build Pre-Map Anticipation Framing
**Target Audience:** Kenyan students interested in AI education

**Emotional Journey (from animation strategy):**
- **Act I (Hero):** Validation - "You're not alone"
- **Act II (Territory Map):** Revelation - "Oh, THIS is where I am"
  - **Pre-scene (This Story):** Anticipation - "Something is about to shift..."
  - **WHOA moment (Story 2.2):** Particle coalescence - Chaos → order
- **Act III (Discord):** Belonging - "This is alive"
- **Act IV (CTA):** Relief - "No pressure, just clarity"

**Design Philosophy:**
- "Disruption with emotional safety"
- Competitors sell: FOMO (fear of missing out)
- K2M sells: Relief (of being found)

**Color Palette:**
- Pure black (#000000) - Main background
- Soft black (#0A0A0A) - Hero section background
- Ocean mint (#20B2AA, #40E0D0, #008B8B) - Accent color

**Performance Goals:**
- Desktop: 60fps consistent
- Mobile: 45fps+ acceptable
- Lighthouse Performance: 90+
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s

**Animation Principles (Awwwards Level):**
- Cinematic: Slow, smooth, deliberate
- Luxurious: Generous timing, no rush
- Emotional: Reveals create anticipation
- Performance: GPU-accelerated only
- Accessibility: Respect prefers-reduced-motion (future)

**Critical Success Factors for This Story:**
1. Anticipatory pin creates smooth slowdown, not "hitting a wall"
2. Progressive text reveals build curiosity (not all at once)
3. Background dimming creates focus and anticipation
4. Bridge between Hero validation and Map revelation
5. Mobile-optimized (shorter pin, faster animations)
6. 4/5 users understand what's coming next

**Next Stories After This One:**
1. Story 2.1: Create Territory Map SVG structure (zones, labels)
2. Story 2.2: Build particle coalescence system (WHOA moment)
3. Story 2.3: Implement zone illumination and magnetic hovers

**Technical Dependencies:**
- Story 1.1 MUST be completed (design tokens, Vite build)
- Story 1.2 MUST be completed (GSAP, ScrollTrigger, Lenis, performance utilities)
- Story 1.3 MUST be completed (Hero HTML structure)
- Story 1.4 MUST be completed (Hero animations - precedes this section)
- Story 1.5 MUST be completed (Hero performance optimization - patterns to apply)

## Dev Agent Record

### Agent Model Used

_Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)_

### Debug Log References

### Completion Notes List

**Story Context:**
- First story in Epic 2 (Territory Map WHOA Moment)
- Creates emotional anticipation before particle coalescence
- Bridges Hero validation (Epic 1) to Map revelation (Epic 2)
- Critical for WHOA moment to feel "earned" not "abrupt"

**Key Technical Features:**
1. GSAP ScrollTrigger with `anticipatePin: 1` for smooth slowdown
2. Progressive text reveals at 30%, 50%, 70% scroll
3. Background dimming: soft black → pure black
4. Mobile-first optimization with `matchMedia()`
5. Performance monitoring (60fps desktop, 45fps mobile)

**Emotional Design Goals:**
- Users feel anticipation, not shock
- Understand something significant is coming
- Bridge from "You're not alone" (Hero) to "Here's where you are" (Map)
- Prepare for WHOA moment (Story 2.2 particle coalescence)

**File Structure:**
- New directory: `/src/components/TerritoryMap/`
- New files: MapFraming.html, MapFraming.css, MapFraming.js
- Component pattern: Self-contained HTML, CSS, JS per section

**Performance Patterns Applied:**
- From Story 1.5: `matchMedia()` for mobile/desktop split
- From Story 1.5: `monitorPerformance()` for FPS tracking
- From Story 1.5: GPU acceleration (`enableGPU`/`disableGPU`)
- From Story 1.5: Safari compatibility (document.hidden detection)

**Experiential Validation:**
- Test with 5 users
- Ask: "What do you expect to see next?"
- Target: 4/5 mention "map", "position", or "territory"
- If < 4/5, adjust copy or animations for clarity

### File List

**New Files to Create:**
- `k2m-landing/src/components/TerritoryMap/MapFraming.html` - Framing HTML structure
- `k2m-landing/src/components/TerritoryMap/MapFraming.css` - Framing styles
- `k2m-landing/src/components/TerritoryMap/MapFraming.js` - Anticipatory pin animations
- `_bmad-output/implementation-artifacts/2-0-build-pre-map-anticipation-framing.md` - This story file

**Files to Modify:**
- `k2m-landing/src/main.js` - Import and initialize MapFraming animations

### Change Log

**2026-01-16 - Story 2.0 Created:**
- Comprehensive story file created for Pre-Map Anticipation Framing
- Technical requirements extracted from epics, implementation plan, animation strategy
- Performance patterns from Story 1.5 applied (matchMedia, FPS monitoring, GPU acceleration)
- Experiential acceptance criteria defined (4/5 users understand what's coming)
- Ready for development workflow
