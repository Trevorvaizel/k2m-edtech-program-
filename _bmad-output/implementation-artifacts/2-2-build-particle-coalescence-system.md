# Story 2.2: Build Particle Coalescence System

Status: ready-for-dev

<!-- Note: Party Mode decision 2026-01-16: Absolute positioning for zones along diagonal journey path. Particle system targets SVG zone marker coordinates (viewBox 1200x800). -->

## Story

As a visitor,
I want to see 200 particles (desktop) or 50 particles (mobile) coalesce from chaos into the Territory Map shape,
So that I experience a stunning "WHOA moment" that represents transformation.

## Acceptance Criteria

**Given** the Territory Map HTML exists with zones positioned (Story 2.1)
**When** I create `/src/components/TerritoryMap/MapParticles.js`
**Then** a `MapParticleSystem` class is defined
**And** the class accepts a container element
**And** `particleCount` is set based on `isMobile()`:
  - Desktop: 200 particles
  - Mobile: 50 particles
**And** particles are created as div elements with class `.map-particle`

**Given** particles need to be styled
**When** I create `/src/components/TerritoryMap/MapParticles.css`
**Then** `.map-particle` has:
  - `position: absolute`
  - `width: 4px` and `height: 4px` (desktop)
  - `width: 2px` and `height: 2px` (mobile via media query)
  - `background: radial-gradient(circle, var(--ocean-mint-glow) 0%, transparent 70%)`
  - `border-radius: 50%`
  - `will-change: transform, opacity`
  - `pointer-events: none`
**And** particles use GPU acceleration

**Given** the particle system is initialized
**When** I call the `init()` method
**Then** particles are created and added to container
**And** each particle has random initial position (`Math.random() * 100%`)
**And** all particles are initially hidden (`opacity: 0`)
**And** `animateFormation()` is called automatically

**Given** I need the chaos → order animation
**When** I implement `animateFormation()` method
**Then** a GSAP timeline is created with ScrollTrigger
**And** ScrollTrigger config includes:
  - `trigger: ".territory-map"`
  - `start: "top center"`
  - `end: "center center"`
  - `scrub: 2`
  - `anticipatePin: 1`
**And** background gradually dims to pure black before reveal
**And** particles spiral from chaos to their positions

**Given** the animation timeline
**When** I animate particle formation
**Then** Phase 1 (Chaos):
  - Particles start at `opacity: 0`, `scale: 0`
  - Particles have random x/y positions (-500 to 500px from center)
**And** Phase 2 (Coalesce):
  - Particles animate to `opacity: 1`, `scale: 1`
  - Particles move to zone positions using GSAP motionPath
  - Duration is 2s
  - Stagger is `amount: 1.5, from: "random"`
  - Ease is `"power2.inOut"` for gentle motion
**And** the spiral motion path is visible (particles follow Bezier curve)

**Given** particles must coalesce to SVG zone marker coordinates
**When** I define particle target positions
**Then** particles distribute among 5 zones using SVG coordinates (viewBox 1200x800):
  - Zone 0: cx="100" cy="700" (20 particles desktop / 5 mobile)
  - Zone 1: cx="400" cy="550" (40 particles desktop / 10 mobile)
  - Zone 2: cx="650" cy="430" (50 particles desktop / 12 mobile)
  - Zone 3: cx="900" cy="320" (50 particles desktop / 12 mobile)
  - Zone 4: cx="1100" cy="180" (40 particles desktop / 11 mobile)
**And** particles cluster around zone centers with random offset (±40px)
**And** particles use GSAP motionPath to follow SVG journey path

**Given** the particle animation is complete
**When** I scroll to the map section
**Then** particles coalesce from chaos into the Territory Map shape
**And** the animation takes 2 seconds to complete
**And** the motion feels smooth and organic
**And** the WHOA moment creates a sense of wonder
**And** performance maintains 60fps desktop / 45fps mobile

**Given** memory management is critical for performance
**When** the particle animation completes
**Then** `will-change: auto` is set on all particles after animation
**And** particles that are no longer animating have transforms cleared
**And** ScrollTrigger cleanup is called if user navigates away
**And** no memory leaks occur over 10-minute continuous scroll sessions

**Given** low-end devices may struggle
**When** the particle system detects poor performance (FPS < 30)
**Then** particle count is dynamically reduced by 50%
**And** animation complexity is simplified (no spiral, just fade-in)
**And** a graceful fallback ensures the map still reveals

**Given** anticipatory pin is needed for emotional buildup
**When** user scrolls toward map section
**Then** scroll gradually slows using `anticipatePin: 1`
**And** background dims from soft black (#0A0A0A) to pure black (#000000)
**And** particles fade in from blackness (not abrupt appearance)
**And** the WHOA moment feels earned, not startling

**Experiential Acceptance Criteria:**
**Given** 5 users test this section
**When** the particles coalesce
**Then** 4/5 users should express surprise, wonder, or say "whoa"

## Tasks / Subtasks

- [ ] 0. Project setup and dependency verification (AC: 1, 2)
  - [ ] 0.1 Verify Story 2.1 complete (TerritoryMap.html with zones, particle-container div)
  - [ ] 0.2 Review Story 2.1 zone coordinates (SVG viewBox 1200x800)
  - [ ] 0.3 Verify GSAP and MotionPath plugin installed (Story 1.2)
  - [ ] 0.4 Confirm performance utilities available (isMobile, monitorPerformance)
  - [ ] 0.5 Verify Zone 0-4 coordinates from Story 2.1:
    - Zone 0: cx="100" cy="700" (20 particles / 5 mobile)
    - Zone 1: cx="400" cy="550" (40 particles / 10 mobile)
    - Zone 2: cx="650" cy="430" (50 particles / 12 mobile)
    - Zone 3: cx="900" cy="320" (50 particles / 12 mobile)
    - Zone 4: cx="1100" cy="180" (40 particles / 11 mobile)

- [ ] 1. Create MapParticles class with particle generation (AC: 1, 3)
  - [ ] 1.1 Create `/src/components/TerritoryMap/MapParticles.js` file
  - [ ] 1.2 Define `MapParticleSystem` class with constructor
  - [ ] 1.3 Accept container element and particle count parameters
  - [ ] 1.4 Detect mobile: `particleCount = isMobile() ? 50 : 200`
  - [ ] 1.5 Create `createParticles()` method to generate DOM elements
  - [ ] 1.6 Create particles as div elements with class `map-particle`
  - [ ] 1.7 Set random initial positions: `x: Math.random() * 100%, y: Math.random() * 100%`
  - [ ] 1.8 Add particles to container with `appendChild`
  - [ ] 1.9 Store particle references in array for animation

- [ ] 2. Create particle CSS styling (AC: 2)
  - [ ] 2.1 Create `/src/components/TerritoryMap/MapParticles.css` file
  - [ ] 2.2 Style `.map-particle` with:
    - `position: absolute`
    - `width: 4px; height: 4px` (desktop)
    - `background: radial-gradient(circle, var(--ocean-mint-glow) 0%, transparent 70%)`
    - `border-radius: 50%`
    - `will-change: transform, opacity`
    - `pointer-events: none`
  - [ ] 2.3 Add mobile media query (max-width: 768px):
    - `width: 2px; height: 2px` (smaller on mobile)
  - [ ] 2.4 Ensure GPU acceleration with `transform: translate3d(0,0,0)`
  - [ ] 2.5 Import CSS in main.js: `import './components/TerritoryMap/MapParticles.css'`

- [ ] 3. Define particle target positions (zone clusters) (AC: 6)
  - [ ] 3.1 Create `ZONE_COORDINATES` constant object with SVG viewBox coordinates
  - [ ] 3.2 Define zone centers (from Story 2.1 SVG):
    ```javascript
    const ZONE_COORDINATES = {
      zone0: { x: 100, y: 700, particleCount: { desktop: 20, mobile: 5 } },
      zone1: { x: 400, y: 550, particleCount: { desktop: 40, mobile: 10 } },
      zone2: { x: 650, y: 430, particleCount: { desktop: 50, mobile: 12 } },
      zone3: { x: 900, y: 320, particleCount: { desktop: 50, mobile: 12 } },
      zone4: { x: 1100, y: 180, particleCount: { desktop: 40, mobile: 11 } }
    };
    ```
  - [ ] 3.3 Create `assignParticleTargets()` method to distribute particles to zones
  - [ ] 3.4 Add random offset (±40px) to zone centers for organic clustering
  - [ ] 3.5 Store target positions in particle objects for animation

- [ ] 4. Implement chaos → order formation animation (AC: 4, 5, 7)
  - [ ] 4.1 Create `animateFormation()` method
  - [ ] 4.2 Create GSAP timeline with ScrollTrigger
  - [ ] 4.3 Configure ScrollTrigger:
    - `trigger: ".territory-map"`
    - `start: "top center"`
    - `end: "center center"`
    - `scrub: 2`
    - `anticipatePin: 1`
  - [ ] 4.4 Add background dimming animation (soft black → pure black)
  - [ ] 4.5 Phase 1 - Chaos state: Set particles to `opacity: 0, scale: 0`
  - [ ] 4.6 Phase 1 - Random positions: `x: -500 to 500, y: -500 to 500` (from center)
  - [ ] 4.7 Phase 2 - Coalesce: Animate to `opacity: 1, scale: 1`
  - [ ] 4.8 Phase 2 - Move particles to zone target positions
  - [ ] 4.9 Set animation duration: `2s`
  - [ ] 4.10 Set stagger: `amount: 1.5, from: "random"` (organic feel)
  - [ ] 4.11 Set easing: `"power2.inOut"` (gentle motion)
  - [ ] 4.12 Test animation timing and adjust for smooth WHOA moment

- [ ] 5. Implement spiral motion path (optional enhancement) (AC: 7)
  - [ ] 5.1 Import GSAP MotionPath plugin (if installed)
  - [ ] 5.2 Define SVG path coordinates matching Story 2.1 journey path
  - [ ] 5.3 Create Bezier curve path: Zone 0 → 1 → 2 → 3 → 4 (diagonal ascent)
  - [ ] 5.4 Apply `motionPath` to particles with `path: bezierCurve, align: false`
  - [ ] 5.5 If MotionPath not available, use simple `x, y` translation fallback
  - [ ] 5.6 Test spiral visibility and particle clustering at zone endpoints

- [ ] 6. Add performance monitoring and optimization (AC: 8, 9)
  - [ ] 6.1 Wrap particle animation in `requestAnimationFrame` check
  - [ ] 6.2 Monitor FPS using `monitorPerformance()` from Story 1.2
  - [ ] 6.3 If FPS < 30 for 2+ seconds, trigger `reduceComplexity()`
  - [ ] 6.4 Create `reduceComplexity()` method:
    - Reduce particle count by 50% (remove excess DOM elements)
    - Remove spiral motion path (use direct fade-in)
    - Simplify stagger (faster animation)
  - [ ] 6.5 After animation completes, set `will-change: auto` on all particles
  - [ ] 6.6 Clear transform values after animation (memory cleanup)
  - [ ] 6.7 Add ScrollTrigger cleanup on page navigation
  - [ ] 6.8 Test memory usage over 10-minute scroll session

- [ ] 7. Implement anticipatory pin and background dimming (AC: 4, 10)
  - [ ] 7.1 Add `anticipatePin: 1` to ScrollTrigger configuration
  - [ ] 7.2 Create background dimming timeline in `animateFormation()`
  - [ ] 7.3 Animate `.territory-map` background from `#0A0A0A` to `#000000`
  - [ ] 7.4 Sync dimming with particle appearance (particles emerge from darkness)
  - [ ] 7.5 Test scroll slowdown (anticipatory pin should feel luxurious, not sluggish)
  - [ ] 7.6 Verify transition from MapFraming (Story 2.0) to TerritoryMap is smooth

- [ ] 8. Integrate MapParticles into main application (AC: 1)
  - [ ] 8.1 Open `/src/main.js` and locate TerritoryMap integration (Story 2.1)
  - [ ] 8.2 Import MapParticles.js: `import { MapParticleSystem } from './components/TerritoryMap/MapParticles.js'`
  - [ ] 8.3 Import MapParticles.css (already done in task 2.5)
  - [ ] 8.4 After TerritoryMap HTML append, initialize particle system:
    ```javascript
    const particleContainer = document.querySelector('.particle-container');
    const particleSystem = new MapParticleSystem(particleContainer);
    particleSystem.init();
    ```
  - [ ] 8.5 Verify particles exist in DOM (check browser DevTools)
  - [ ] 8.6 Test particle system initialization on page load

- [ ] 9. Test particle animation on desktop and mobile (AC: 7, 8)
  - [ ] 9.1 Test on desktop (1920x1080):
    - Verify 200 particles created
    - Check particles coalesce smoothly from chaos to order
    - Confirm WHOA moment feels stunning (not chaotic)
    - Verify particles cluster at zone positions
    - Check animation timing (2s duration feels right)
  - [ ] 9.2 Test on mobile (375x667):
    - Verify 50 particles created (performance optimization)
    - Check particles are 2px size (not too large)
    - Verify animation maintains 45fps+ performance
    - Confirm mobile WHOA moment still impactful
  - [ ] 9.3 Test on low-end devices:
    - Simulate poor performance (devtools throttling)
    - Verify `reduceComplexity()` triggers when FPS < 30
    - Confirm fallback animation still reveals map
  - [ ] 9.4 Test anticipatory pin:
    - Scroll toward map section
    - Verify gradual slowdown (anticipatePin: 1)
    - Check background dimming (soft black → pure black)
    - Confirm WHOA moment feels earned

- [ ] 10. Create Playwright visual regression tests (AC: 1, 7)
  - [ ] 10.1 Create `/tests/screenshots/story-2-2-visual.spec.ts` test file
  - [ ] 10.2 Test desktop initial state:
    - Screenshot before scroll (chaos state)
    - Verify particles visible but scattered
  - [ ] 10.3 Test desktop scrolled state:
    - Scroll to `center center` (formation complete)
    - Screenshot after particles coalesced
    - Verify particles clustered at zone positions
  - [ ] 10.4 Test mobile viewport (375x667):
    - Test particle formation on mobile
    - Verify particle count reduced (50 vs 200)
    - Check particle size smaller (2px vs 4px)
  - [ ] 10.5 Test performance:
    - Measure FPS during particle animation
    - Verify 60fps desktop / 45fps mobile baseline
    - Check no frame drops below threshold
  - [ ] 10.6 Run tests and verify all pass

- [ ] 11. Document particle system for future stories (AC: 1)
  - [ ] 11.1 Add inline comments in MapParticles.js explaining chaos → order animation
  - [ ] 11.2 Document zone coordinate system for Story 2.3 (zone hovers)
  - [ ] 11.3 Note particle cleanup strategies (will-change: auto)
  - [ ] 11.4 Document performance fallback triggers (FPS < 30)

## Dev Notes

### Epic Context
This is the **third story** in Epic 2: Territory Map WHOA Moment. Story 2.2 creates the particle coalescence animation that transforms from chaos to order, creating the stunning visual WHOA moment.

**Critical Dependencies:**
- Story 2.0 MUST be completed (MapFraming anticipatory pin)
- Story 2.1 MUST be completed (TerritoryMap.html with zones, SVG coordinates)
- Story 1.2 MUST be completed (GSAP infrastructure, performance utilities)

**Story Sequence:**
- Story 2.0: Pre-Map anticipation framing (COMPLETED)
- Story 2.1: Territory Map structure (COMPLETED)
- **Story 2.2: Particle coalescence system** (THIS STORY)
- Story 2.3: Zone illumination and magnetic hovers (NEXT)

**Why This Story Matters:**
Without the particle coalescence, the Territory Map is just static HTML. This story:
1. Creates the emotional WHOA moment (chaos → order = transformation)
2. Uses particles as visual metaphor for learning journey
3. Reveals the map in a cinematic, memorable way
4. Sets up zone targeting for Story 2.3 (interactive hovers)

### Technical Requirements

#### Particle System Architecture:

**MapParticles.js Class Structure:**
```javascript
// MapParticles.js
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { isMobile, monitorPerformance } from '../../utils/performance-optimizations.js';

gsap.registerPlugin(ScrollTrigger);

export class MapParticleSystem {
  constructor(container) {
    this.container = container;
    this.particleCount = isMobile() ? 50 : 200;
    this.particles = [];
    this.timeline = null;
  }

  init() {
    this.createParticles();
    this.assignParticleTargets();
    this.animateFormation();
  }

  createParticles() {
    for (let i = 0; i < this.particleCount; i++) {
      const particle = document.createElement('div');
      particle.classList.add('map-particle');
      particle.style.left = `${Math.random() * 100}%`;
      particle.style.top = `${Math.random() * 100}%`;
      this.container.appendChild(particle);
      this.particles.push(particle);
    }
  }

  assignParticleTargets() {
    // Zone coordinates from Story 2.1 SVG (viewBox 1200x800)
    const ZONE_COORDINATES = {
      zone0: { x: 100, y: 700, count: isMobile() ? 5 : 20 },
      zone1: { x: 400, y: 550, count: isMobile() ? 10 : 40 },
      zone2: { x: 650, y: 430, count: isMobile() ? 12 : 50 },
      zone3: { x: 900, y: 320, count: isMobile() ? 12 : 50 },
      zone4: { x: 1100, y: 180, count: isMobile() ? 11 : 40 }
    };

    let particleIndex = 0;

    // Distribute particles to zones
    Object.entries(ZONE_COORDINATES).forEach(([zone, data]) => {
      for (let i = 0; i < data.count && particleIndex < this.particles.length; i++) {
        const particle = this.particles[particleIndex];
        const offsetX = (Math.random() - 0.5) * 80; // ±40px offset
        const offsetY = (Math.random() - 0.5) * 80;

        particle.dataset.targetX = data.x + offsetX;
        particle.dataset.targetY = data.y + offsetY;
        particleIndex++;
      }
    });
  }

  animateFormation() {
    // ScrollTrigger setup
    ScrollTrigger.create({
      trigger: '.territory-map',
      start: 'top center',
      end: 'center center',
      scrub: 2,
      anticipatePin: 1,
      onUpdate: (self) => {
        // Monitor performance
        if (performance.now() % 1000 < 20) { // Every ~1 second
          const fps = monitorPerformance();
          if (fps < 30) {
            this.reduceComplexity();
          }
        }
      }
    });

    // Background dimming animation
    gsap.to('.territory-map', {
      backgroundColor: '#000000',
      scrollTrigger: {
        trigger: '.territory-map',
        start: 'top center',
        end: 'center center',
        scrub: 2
      }
    });

    // Particle chaos → order animation
    this.timeline = gsap.timeline();

    // Phase 1: Chaos (random positions)
    this.timeline.set(this.particles, {
      opacity: 0,
      scale: 0,
      x: (i) => (Math.random() - 0.5) * 1000, // -500 to 500px
      y: (i) => (Math.random() - 0.5) * 1000
    });

    // Phase 2: Coalesce to zone positions
    this.timeline.to(this.particles, {
      opacity: 1,
      scale: 1,
      x: (i, p) => parseFloat(p.dataset.targetX) - window.innerWidth / 2,
      y: (i, p) => parseFloat(p.dataset.targetY) - window.innerHeight / 2,
      duration: 2,
      stagger: {
        amount: 1.5,
        from: 'random'
      },
      ease: 'power2.inOut',
      scrollTrigger: {
        trigger: '.territory-map',
        start: 'top center',
        end: 'center center',
        scrub: 2
      },
      onComplete: () => {
        // Memory cleanup
        this.particles.forEach(p => p.style.willChange = 'auto');
      }
    });
  }

  reduceComplexity() {
    // Reduce particle count by 50%
    const particlesToRemove = this.particles.splice(Math.floor(this.particles.length / 2));
    particlesToRemove.forEach(p => p.remove());

    // Simplify animation (remove chaos phase)
    if (this.timeline) {
      this.timeline.seek(1); // Skip to coalesce phase
    }
  }

  destroy() {
    if (this.timeline) {
      this.timeline.kill();
    }
    this.particles.forEach(p => p.remove());
    ScrollTrigger.getAll().forEach(trigger => trigger.kill());
  }
}
```

**Integration into main.js:**
```javascript
// In main.js (after TerritoryMap integration)
import { MapParticleSystem } from './components/TerritoryMap/MapParticles.js';
import './components/TerritoryMap/MapParticles.css';

// After TerritoryMap HTML append
const particleContainer = document.querySelector('.particle-container');
if (particleContainer) {
  const particleSystem = new MapParticleSystem(particleContainer);
  particleSystem.init();
}
```

#### CSS Styling:

**MapParticles.css:**
```css
/* MapParticles.css */
.map-particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: radial-gradient(circle, var(--ocean-mint-glow) 0%, transparent 70%);
  border-radius: 50%;
  will-change: transform, opacity;
  pointer-events: none;
  transform: translate3d(0, 0, 0); /* GPU acceleration */
}

/* Mobile optimization - smaller particles */
@media (max-width: 768px) {
  .map-particle {
    width: 2px;
    height: 2px;
  }
}
```

#### Zone Coordinate System (Story 2.1 Integration):

**Particle Distribution Strategy:**
- **Zone 0 (20/5 particles):** Sparse clustering - ghost state, beginning
- **Zone 1 (40/10 particles):** Emerging curiosity
- **Zone 2 (50/12 particles):** Forming understanding - most populated
- **Zone 3 (50/12 particles):** Solid collaboration - most populated
- **Zone 4 (40/11 particles):** Fully present - destination with glow

**Target Position Calculation:**
```javascript
// Convert SVG viewBox coordinates to viewport
const targetX = zoneData.x * (window.innerWidth / 1200);
const targetY = zoneData.y * (window.innerHeight / 800);
```

### Architecture Compliance

#### File Structure:
```
k2m-landing/
├── src/
│   ├── main.js                         # Entry point
│   ├── components/
│   │   └── TerritoryMap/               # Epic 2 (Territory Map)
│   │       ├── MapFraming.html         # Story 2.0 - Pre-map anticipation
│   │       ├── MapFraming.css          # Story 2.0 - Framing styles
│   │       ├── MapFraming.js           # Story 2.0 - Anticipatory pin
│   │       ├── TerritoryMap.html       # Story 2.1 - Map structure
│   │       ├── TerritoryMap.css        # Story 2.1 - Map styles
│   │       ├── MapParticles.js         # THIS STORY - Particle system
│   │       └── MapParticles.css        # THIS STORY - Particle styles
│   ├── utils/
│   │   ├── gsap-config.js              # Story 1.2 - GSAP infrastructure
│   │   ├── lenis-config.js             # Story 1.2 - Smooth scroll
│   │   └── performance-optimizations.js # Story 1.2 - GPU, FPS helpers
│   └── styles/
│       └── token.css                   # Story 1.1 - Design tokens
```

**New Files for This Story:**
- `/src/components/TerritoryMap/MapParticles.js` - Particle system class
- `/src/components/TerritoryMap/MapParticles.css` - Particle styles

**Files Modified:**
- `/src/main.js` - Import and initialize MapParticles

#### Import Pattern (Follow Story 2.1):
```javascript
// In main.js
import { MapParticleSystem } from './components/TerritoryMap/MapParticles.js';
import './components/TerritoryMap/MapParticles.css';

// After TerritoryMap integration
const particleContainer = document.querySelector('.particle-container');
const particleSystem = new MapParticleSystem(particleContainer);
particleSystem.init();
```

### Library/Framework Requirements

#### GSAP MotionPath Plugin (Optional Enhancement):
**For Spiral Motion Path (Optional):**
- Install: `npm install @gsap/motionpath-plugin`
- Import: `import { MotionPathPlugin } from '@gsap/motionpath-plugin'`
- Register: `gsap.registerPlugin(MotionPathPlugin)`
- Use: Apply `motionPath: { path: bezierCurve, align: false }` to particles

**Fallback Without MotionPath:**
- Use standard `x, y` translation to target positions
- Still creates organic WHOA moment (particles cluster at zones)
- More performance-friendly for mobile

#### No Additional Dependencies Required:
- **GSAP Core** (already installed in Story 1.2)
- **ScrollTrigger** (already installed in Story 1.2)
- **Performance utilities** (already created in Story 1.2)
- **Design tokens** (already defined in Story 1.1)

### Testing Requirements

#### Visual Testing Checklist:

1. **Particle System Initialization (Desktop):**
   - [ ] 200 particles created on desktop
   - [ ] Particles are 4px size (ocean mint gradient)
   - [ ] Particles initially scattered (chaos state)
   - [ ] Particles have `will-change: transform, opacity`
   - [ ] Particles use GPU acceleration (translate3d)

2. **Particle System Initialization (Mobile):**
   - [ ] 50 particles created on mobile (performance optimization)
   - [ ] Particles are 2px size (smaller on mobile)
   - [ ] Animation maintains 45fps+ performance
   - [ ] No frame drops during coalescence

3. **Chaos → Order Animation:**
   - [ ] Scroll triggers animation at `top center`
   - [ ] Animation completes at `center center`
   - [ ] Duration: 2 seconds (scrub: 2)
   - [ ] Stagger: 1.5s random feel (organic)
   - [ ] Easing: power2.inOut (gentle motion)
   - [ ] Particles coalesce smoothly, not abruptly

4. **Zone Clustering (Desktop):**
   - [ ] Particles cluster at Zone 0 (20 particles around cx=100, cy=700)
   - [ ] Particles cluster at Zone 1 (40 particles around cx=400, cy=550)
   - [ ] Particles cluster at Zone 2 (50 particles around cx=650, cy=430)
   - [ ] Particles cluster at Zone 3 (50 particles around cx=900, cy=320)
   - [ ] Particles cluster at Zone 4 (40 particles around cx=1100, cy=180)
   - [ ] Particles have random offset (±40px) from zone centers
   - [ ] Clustering looks organic, not grid-like

5. **Zone Clustering (Mobile):**
   - [ ] Particles cluster at Zone 0 (5 particles)
   - [ ] Particles cluster at Zone 1 (10 particles)
   - [ ] Particles cluster at Zone 2 (12 particles)
   - [ ] Particles cluster at Zone 3 (12 particles)
   - [ ] Particles cluster at Zone 4 (11 particles)
   - [ ] Mobile clusters visible on vertical stack layout

6. **Anticipatory Pin and Background Dimming:**
   - [ ] Scroll slows down approaching map (anticipatePin: 1)
   - [ ] Background dims from #0A0A0A to #000000
   - [ ] Particles emerge from darkness (opacity 0 → 1)
   - [ ] WHOA moment feels earned, not abrupt
   - [ ] Transition from MapFraming is smooth

7. **Performance and Memory Management:**
   - [ ] Animation maintains 60fps desktop baseline
   - [ ] Animation maintains 45fps mobile baseline
   - [ ] `will-change: auto` set after animation completes
   - [ ] Transforms cleared after animation (memory cleanup)
   - [ ] ScrollTrigger cleanup on navigation
   - [ ] No memory leaks over 10-minute scroll session

8. **Performance Fallback (Low-End Devices):**
   - [ ] FPS monitoring active during animation
   - [ ] When FPS < 30 for 2+ seconds, `reduceComplexity()` triggers
   - [ ] Particle count reduced by 50%
   - [ ] Animation simplified (no spiral, just fade-in)
   - [ ] Map still reveals clearly despite fallback
   - [ ] WHOA moment preserved (just simpler)

9. **Spiral Motion Path (Optional Enhancement):**
   - [ ] If MotionPath plugin installed, particles follow Bezier curve
   - [ ] Spiral path visible (particles curve toward zones)
   - [ ] Motion path matches Story 2.1 SVG journey path
   - [ ] If MotionPath not available, x/y translation fallback works
   - [ ] Both approaches create organic WHOA moment

10. **Experiential Testing:**
    - [ ] 5 users test particle coalescence
    - [ ] 4/5 users express surprise, wonder, or say "whoa"
    - [ ] Users understand chaos → order = transformation metaphor
    - [ ] WHOA moment creates emotional impact
    - [ ] Animation feels cinematic, not chaotic

### Previous Story Intelligence

**Story 2.1 Territory Map Structure (Foundation):**
Story 2.1 created the HTML, CSS, and SVG structure for the Territory Map:
- 5 zones positioned along diagonal journey path (absolute positioning)
- SVG viewBox coordinates for zone markers (1200x800)
- Particle container div with class `particle-container`
- Zone coordinates: Zone 0 (100, 700) → Zone 4 (1100, 180)

**Integration for Story 2.2:**
1. Use `particle-container` div for particle injection
2. Target SVG zone marker coordinates for particle clustering
3. Respect absolute positioning layout (desktop) / vertical stack (mobile)
4. Follow Vite import pattern (CSS + JS class instantiation)

**Story 2.0 MapFraming (Anticipatory Pin Pattern):**
Story 2.0 established the anticipatory pin pattern:
- `anticipatePin: 1` for gradual scroll slowdown
- Background dimming (soft black → pure black)
- Emotional buildup before WHOA moment

**Apply Same Pattern to Story 2.2:**
1. Add `anticipatePin: 1` to ScrollTrigger configuration
2. Animate background dimming synced with particle coalescence
3. Ensure WHOA moment feels earned (not abrupt start)

**Story 1.5 Performance (Mobile Optimization):**
Story 1.5 taught us to always optimize for mobile:
- Reduce particle count on mobile (50 vs 200 desktop)
- Smaller particle size on mobile (2px vs 4px desktop)
- Monitor FPS and trigger fallback when performance drops
- Ensure 45fps+ mobile baseline

**Story 1.2 Infrastructure (GSAP and Performance Utilities):**
Story 1.2 created the GSAP infrastructure and performance utilities:
- `isMobile()` detection function
- `monitorPerformance()` FPS counter
- GPU acceleration helpers (`enableGPU`, `disableGPU`)
- ScrollTrigger configuration patterns

**Apply to Story 2.2:**
1. Use `isMobile()` to determine particle count (50 vs 200)
2. Use `monitorPerformance()` to detect FPS drops
3. Use GPU acceleration (`translate3d`, `will-change`)
4. Follow ScrollTrigger patterns (scrub, anticipatePin)

### Latest Tech Information

#### GSAP ScrollTrigger Best Practices (2025):
**Anticipatory Pin for Emotional Buildup:**
```javascript
ScrollTrigger.create({
  trigger: '.territory-map',
  start: 'top center',
  end: 'center center',
  scrub: 2,
  anticipatePin: 1  // Gradual slowdown before pin
});
```

**Benefits:**
- Creates emotional anticipation (not abrupt)
- Luxurious scroll feel (Lenis smooth scroll)
- User feels something significant coming
- WHOA moment feels earned

#### Particle System Performance (2025):
**Memory Management Strategies:**
```javascript
// During animation - optimize for GPU
particle.style.willChange = 'transform, opacity';

// After animation - cleanup memory
particle.style.willChange = 'auto';
particle.style.transform = 'none'; // Clear transforms
```

**Benefits:**
- No memory leaks during extended scrolling
- GPU acceleration during animation (smooth)
- Memory cleanup after animation (efficient)
- 60fps performance maintained

#### Performance Fallback Patterns (2025):
**Dynamic Complexity Reduction:**
```javascript
if (monitorPerformance() < 30) {
  reduceComplexity();
}

reduceComplexity() {
  // Remove excess particles
  const toRemove = particles.splice(particles.length / 2);
  toRemove.forEach(p => p.remove());

  // Simplify animation
  timeline.seek(1); // Skip chaos phase
}
```

**Benefits:**
- Works on low-end devices
- Graceful degradation (map still reveals)
- WHOA moment preserved (just simpler)
- No broken animations

### Project Context Reference

**Project Name:** k2m-edtech-program-
**Epic:** Epic 2: Territory Map WHOA Moment
**Story:** 2.2 - Build Particle Coalescence System
**Target Audience:** Kenyan students interested in AI education

**Emotional Journey (from animation strategy):**
- **Act I (Hero):** Validation - "You're not alone"
- **Act II (Territory Map):** Revelation - "Oh, THIS is where I am"
  - **Pre-scene (Story 2.0):** Anticipation - "Something is about to shift..."
  - **Map Structure (Story 2.1):** Foundation - 5 zones, learning journey visual
  - **WHOA moment (This Story):** Particle coalescence - Chaos → order = transformation
  - **Zone Interaction (Story 2.3):** Illumination and hovers
- **Act III (Discord):** Belonging - "This is alive"
- **Act IV (CTA):** Relief - "No pressure, just clarity"

**Particle System Metaphor:**
- **Chaos:** Where students start (confused, scattered)
- **Order:** Where students arrive (clear, directed)
- **Transformation:** Learning journey visual metaphor
- **Coalescence:** Finding your place in the Territory Map

**Color Palette:**
- Ocean mint (#20B2AA, #40E0D0, #008B8B) - Particle glow
- Pure black (#000000) - WHOA moment background
- Radial gradient for particle depth effect

**Performance Goals:**
- Desktop: 60fps consistent
- Mobile: 45fps+ acceptable
- Lighthouse Performance: 90+
- Memory efficient (no leaks over 10-minute session)

**Critical Success Factors for This Story:**
1. Stunning WHOA moment (4/5 users say "whoa")
2. Smooth particle coalescence (not chaotic)
3. Performance optimized (200 desktop, 50 mobile particles)
4. Graceful fallback on low-end devices
5. Anticipatory pin creates emotional buildup
6. Memory cleanup prevents leaks

**Next Stories After This One:**
1. Story 2.3: Implement zone illumination and magnetic hovers (builds on particle positions)

**Technical Dependencies:**
- Story 1.1: Design tokens (ocean mint colors)
- Story 1.2: GSAP infrastructure, performance utilities
- Story 2.0: MapFraming anticipatory pin pattern
- Story 2.1: TerritoryMap structure, zone coordinates, particle container

## Dev Agent Record

### Agent Model Used

_Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)_

### Debug Log References

### Completion Notes List

**Story Recreated: 2026-01-17 (Fresh Generation with Enhanced Context)**

**Comprehensive Analysis Completed:**
- ✅ Extracted requirements from Epic 2 (epics.md lines 652-738)
- ✅ Applied integration patterns from Story 2.1 (Vite imports, zone coordinates)
- ✅ Used anticipatory pin pattern from Story 2.0 (emotional buildup)
- ✅ Incorporated performance patterns from Story 1.5 (mobile optimization)
- ✅ Used design tokens from Story 1.1 (ocean mint particle glow)
- ✅ Leveraged GSAP infrastructure from Story 1.2 (ScrollTrigger, performance utilities)
- ✅ Confirmed Epic 2 scope: Zones 0-4 only (per git commit 28da64)
- ✅ Created foundation for Story 2.3 (particle positions for zone hovers)

**Technical Approach:**
1. **Particle System Class:** MapParticleSystem with init(), createParticles(), animateFormation()
2. **Particle Generation:** 200 desktop / 50 mobile particles as div elements
3. **Zone Targeting:** Particles cluster at SVG coordinates (viewBox 1200x800)
4. **Animation Timeline:** Chaos (random positions) → Order (zone clustering) over 2s
5. **Performance:** GPU acceleration, memory cleanup, fallback on low-end devices
6. **Anticipatory Pin:** Gradual scroll slowdown + background dimming for emotional buildup

**Key Design Decisions:**
- **Particle Count:** 200 desktop / 50 mobile (performance optimization)
- **Particle Size:** 4px desktop / 2px mobile (visibility vs performance)
- **Zone Distribution:** Proportional to zone "weight" (Zone 2,3 most populated)
- **Animation Timing:** 2s duration, 1.5s stagger random feel (organic)
- **Easing:** power2.inOut (gentle motion, not jarring)
- **Background Dimming:** Soft black → pure black (WHOA moment isolation)
- **Memory Cleanup:** will-change: auto after animation (prevent leaks)

**Performance Considerations:**
- GPU acceleration (translate3d, will-change)
- Monitor FPS during animation
- Reduce complexity when FPS < 30
- Remove 50% of particles on low-end devices
- Memory cleanup after animation (will-change: auto)
- ScrollTrigger cleanup on navigation

**Animation Flow:**
1. **Phase 1 (Chaos):** Particles scattered randomly (opacity 0, scale 0)
2. **Background Dimming:** Soft black → pure black
3. **Phase 2 (Coalesce):** Particles move to zone positions (opacity 1, scale 1)
4. **Memory Cleanup:** will-change: auto after animation completes

**Testing Strategy:**
- Playwright visual regression tests (before/after scroll)
- Desktop and mobile viewport testing
- Performance monitoring (60fps desktop / 45fps mobile)
- Memory leak testing (10-minute scroll session)
- Experiential testing (4/5 users say "whoa")

**Story Context:**
- Third story in Epic 2
- Creates the emotional WHOA moment (chaos → order)
- Uses particles as transformation metaphor
- Bridges MapFraming anticipation to zone interaction
- Critical for user emotional engagement

### File List

**New Files to Create:**
- `k2m-landing/src/components/TerritoryMap/MapParticles.js` - Particle system class
- `k2m-landing/src/components/TerritoryMap/MapParticles.css` - Particle styles
- `k2m-landing/tests/screenshots/story-2-2-visual.spec.ts` - Playwright visual tests
- `_bmad-output/implementation-artifacts/2-2-build-particle-coalescence-system.md` - This story file

**Files to Modify:**
- `k2m-landing/src/main.js` - Import and initialize MapParticles

### Change Log

**2026-01-17 - Story Recreation (Bob - Scrum Master):**
- Regenerated story file from Epic 2 requirements with comprehensive context
- Requirements extracted from Epic 2 (epics.md lines 652-738)
- Integration patterns from Story 2.1 (zone coordinates, particle container)
- Anticipatory pin pattern from Story 2.0 (emotional buildup)
- Performance patterns from Story 1.5 (mobile optimization)
- Design tokens from Story 1.1 (ocean mint particle glow)
- GSAP infrastructure from Story 1.2 (ScrollTrigger, performance utilities)
- Confirmed Epic 2 scope: Zones 0-4 only (per git commit 28da64)
- Technical approach: Chaos → order animation with zone clustering
- Particle distribution: 200 desktop / 50 mobile (proportional to zone weight)
- Animation: 2s duration, 1.5s stagger, power2.inOut easing (organic feel)
- Performance: GPU acceleration, memory cleanup, fallback on low-end devices
- Memory management: will-change: auto after animation, transform cleanup
- Experiential goal: 4/5 users say "whoa" (WHOA moment validation)
- YOLO mode execution (no user elicitation)
- Status: ready-for-dev
