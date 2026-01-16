# Story 2.1: Create Territory Map SVG Structure

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->
<!-- Party Mode Validation: 2026-01-16 - Design philosophy and specs validated by creative team -->

## Story

As a visitor,
I want to see the Territory Map with 5 distinct zones (0-4),
So that I can understand the learning journey and identify my current position.

## Design Philosophy: "The Discovered Map"

> **Core Insight:** The map should feel DISCOVERED, not designed. Like it was always there, waiting to be seen.

### The Meta-Emotion: Pre-Recognition

The Territory Map creates **pre-recognition** - the feeling of "something is about to name where I am" before the student reads any words. The design must trigger self-recognition without telling.

**Emotional Sequence:**
1. **Ambient confusion** → "I don't know where I am"
2. **Pre-recognition** → "Wait... is this about to describe me?"
3. **The naming** → Zone taglines appear
4. **Recognition shock** → "That's EXACTLY my experience"
5. **Legibility** → "I can see myself now"
6. **Orientation** → "And I can see where I could go"

### Master Cartographer Principles

| Principle | Design Application |
|-----------|-------------------|
| Map = feeling, not information | Prioritize emotional temperature over layout precision |
| Mirror first, window second | Student sees themselves (Zone 0-2), then destination (Zone 4) |
| Degrees of becoming | Opacity gradient: ghost → fully present (0.3 → 1.0) |
| Temperature progression | Cold/distant → warm/radiant |
| Scroll as cartography (mobile) | Vertical journey, minimal SVG, scroll = movement |
| Zones as gravity wells | Particle attractors where journeys naturally collect |
| Zone 4 as strongest attractor | Maximum glow, maximum presence, maximum gravity |

### Visual Concept: Topographical Ascent

The SVG represents a **journey upward** - from the valley (Zone 0) to the summit (Zone 4). The path feels worn, like many have walked it before. Zone 4 glows because that's where people END UP - not because we made it glow arbitrarily.

## Acceptance Criteria

**Given** the Hero section and MapFraming section are complete
**When** I create `/src/components/TerritoryMap/TerritoryMap.html`
**Then** a map section exists with:
  - Container for particle system (prepared for Story 2.2)
  - Inline SVG with 5 zone groups (0, 1, 2, 3, 4) for visual representation
  - Each zone has semantic HTML heading and description text
  - Zone 4 has ocean mint accent styling to highlight destination
  - Zones are positioned visually to represent progression (0 → 4)
**And** the map is centered on the page with appropriate spacing
**And** zones are visually distinct with clear hierarchy

**Given** the zones need accurate copy
**When** I add zone text content
**Then** each zone displays the following approved copy:
  - Zone 0: Heading "AI isn't for me" with description "Where most students start. Feeling overwhelmed."
  - Zone 1: Heading "I could try this" with description "First sparks of curiosity."
  - Zone 2: Heading "AI does tasks for me" with description "Using it for real work. But inconsistent."
  - Zone 3: Heading "AI understands my intent" with description "True collaboration begins."
  - Zone 4: Heading "I control the quality" with description "You direct. You refine. You own the outcome. This is where confidence lives."
**And** all copy matches the final approved document (Source: k2m-landing-page-copy-final.md)
**And** text is readable on pure black background

**Given** I need interactive elements for future animations
**When** I structure the HTML
**Then** each zone has:
  - `data-zone` attribute for JavaScript targeting (e.g., data-zone="0")
  - Semantic class names for styling and animation targeting
  - Semantic HTML structure (h3 for zone heading, p for description)
  - ARIA labels for accessibility
  - Keyboard navigable structure
**And** zones are accessible via Tab key navigation
**And** screen readers can announce zone information

**Given** the map needs visual consistency
**When** I view the page
**Then** all 5 zones are visible on the page
**And** text is readable on pure black background (WCAG AA: 4.5:1 contrast ratio)
**And** Zone 4 stands out with ocean mint accent color (#40E0D0)
**And** the layout is responsive and mobile-friendly (no horizontal scroll)
**And** zones have proper spacing between them
**And** the visual hierarchy is clear (Zone 0 → 4 progression)

**Given** this is foundation for particle system
**When** I prepare for Story 2.2
**Then** a particle container div exists with class `particle-container`
**And** the container is positioned correctly for particle animation
**And** zones are positioned to receive particles (for coalescence animation)
**And** the structure supports 200 desktop particles / 50 mobile particles

## Tasks / Subtasks

- [ ] 0. Project setup and dependency verification (AC: 1, 2)
  - [ ] 0.1 Verify `/src/components/TerritoryMap/` directory exists (created in Story 2.0)
  - [ ] 0.2 Review Story 2.0 implementation for integration patterns (MapFraming integration)
  - [ ] 0.3 Verify design tokens in token.css (ocean mint colors, typography)
  - [ ] 0.4 Review Territory Map copy from `_bmad-output/k2m-landing-page-copy-final.md` (SINGLE SOURCE OF TRUTH - lines 54-78)
  - [ ] 0.5 Verify Zone 4 accent color: --ocean-mint-glow (#40E0D0)

- [ ] 1. Create TerritoryMap HTML structure with zones (AC: 1, 2, 4)
  - [ ] 1.1 Create `/src/components/TerritoryMap/TerritoryMap.html` file
  - [ ] 1.2 Add section container with class `territory-map` and id `territory-map`
  - [ ] 1.3 Add particle container div with class `particle-container` (for Story 2.2)
  - [ ] 1.4 Add SVG container for visual map representation (inline SVG structure)
  - [ ] 1.5 Create 5 zone groups using semantic HTML:
    - Zone 0: `div.zone.zone-0` with data-zone="0"
    - Zone 1: `div.zone.zone-1` with data-zone="1"
    - Zone 2: `div.zone.zone-2` with data-zone="2"
    - Zone 3: `div.zone.zone-3` with data-zone="3"
    - Zone 4: `div.zone.zone-4` with data-zone="4"
  - [ ] 1.6 Add heading (h3) and description (p) to each zone with approved copy
  - [ ] 1.7 Add `aria-label` to main section for accessibility
  - [ ] 1.8 Ensure semantic HTML structure (section > div.zone > h3 + p)
  - [ ] 1.9 Verify all text content matches approved copy exactly

- [ ] 2. Create TerritoryMap CSS with visual styling (AC: 3, 4)
  - [ ] 2.1 Create `/src/components/TerritoryMap/TerritoryMap.css` file
  - [ ] 2.2 Add section styling with pure black background (#000000)
  - [ ] 2.3 Set section dimensions: `min-height: 100vh` for full viewport
  - [ ] 2.4 Center content with flexbox or grid layout
  - [ ] 2.5 Add generous padding: `4rem` on desktop, `2rem` on mobile
  - [ ] 2.6 Style zone containers with:
    - `position: relative` for absolute positioning of particles
    - `border-radius` for soft edges
    - `padding` for text spacing
    - `transition` properties for future hover animations
  - [ ] 2.7 Apply typography: Space Grotesk for headings, Inter for descriptions
  - [ ] 2.8 Style Zone 4 with ocean mint accent:
    - `border: 2px solid var(--ocean-mint-glow)`
    - `box-shadow: 0 0 20px rgba(64, 224, 208, 0.3)`
    - Accent color on heading text
  - [ ] 2.9 Ensure text contrast meets WCAG AA (4.5:1 for body text, 3:1 for large text)

- [ ] 3. Implement responsive design for mobile (AC: 4)
  - [ ] 3.1 Add media query for mobile breakpoint (max-width: 768px)
  - [ ] 3.2 Adjust zone layout for mobile (vertical stack instead of horizontal)
  - [ ] 3.3 Reduce padding on mobile: `2rem` instead of `4rem`
  - [ ] 3.4 Scale font sizes appropriately with `clamp()` or media queries
  - [ ] 3.5 Ensure no horizontal scrolling on mobile devices
  - [ ] 3.6 Test on iPhone 12+ viewport (375x667)
  - [ ] 3.7 Test on Samsung Galaxy S21+ viewport (360x800)

- [ ] 4. Create "The Discovered Map" SVG structure (AC: 1) - SEE DESIGN SPEC BELOW
  - [ ] 4.1 Add inline SVG element with `viewBox="0 0 1200 800"` to TerritoryMap.html
  - [ ] 4.2 Create organic Bezier path (NOT straight lines) showing worn journey trail
  - [ ] 4.3 Add zone markers at exact coordinates (see Zone Coordinates section):
    - Zone 0: cx="100" cy="700" (bottom-left, valley)
    - Zone 1: cx="400" cy="550" (lower-middle)
    - Zone 2: cx="650" cy="430" (middle, crossing)
    - Zone 3: cx="900" cy="320" (upper-middle, ascent)
    - Zone 4: cx="1100" cy="180" (top-right, summit - GLOWING)
  - [ ] 4.4 Apply opacity gradient to zone markers (degrees of becoming):
    - Zone 0: opacity 0.3, stroke-opacity 0.1
    - Zone 1: opacity 0.45, stroke-opacity 0.15
    - Zone 2: opacity 0.6, stroke-opacity 0.2
    - Zone 3: opacity 0.8, stroke-opacity 0.3
    - Zone 4: opacity 1.0, stroke-opacity 0.8 + GLOW
  - [ ] 4.5 Add radial gradient for Zone 4 "presence glow" (ocean mint, 180px radius)
  - [ ] 4.6 Style path as "worn trail": stroke-dasharray="12 6", opacity 0.15
  - [ ] 4.7 Position SVG behind zone text (z-index: 0)
  - [ ] 4.8 Add `aria-label="Journey path from Zone 0 to Zone 4"` to SVG

- [ ] 5. Add particle container for Story 2.2 preparation (AC: 1, 4)
  - [ ] 5.1 Create `<div class="particle-container">` in HTML
  - [ ] 5.2 Position container: `position: absolute; inset: 0;`
  - [ ] 5.3 Set `pointer-events: none` (particles shouldn't block interactions)
  - [ ] 5.4 Set `z-index: 1` (above background, below zone text)
  - [ ] 5.5 Ensure container spans full section for particle movement
  - [ ] 5.6 Add CSS: `will-change: transform, opacity` for future animations

- [ ] 6. Integrate TerritoryMap into main application (AC: 1)
  - [ ] 6.1 Open `/src/main.js` and locate MapFraming integration (Story 2.0)
  - [ ] 6.2 Import TerritoryMap.css at top of main.js:
    - Add: `import './components/TerritoryMap/TerritoryMap.css'`
  - [ ] 6.3 Import TerritoryMap.html using Vite ?raw pattern:
    - Add: `import territoryMapHtml from './components/TerritoryMap/TerritoryMap.html?raw'`
  - [ ] 6.4 Append TerritoryMap HTML after MapFraming:
    - Add: `app.innerHTML += territoryMapHtml`
  - [ ] 6.5 Verify TerritoryMap section appears after MapFraming in DOM
  - [ ] 6.6 Test smooth scroll from MapFraming to TerritoryMap
  - [ ] 6.7 Verify no layout shift between sections

- [ ] 7. Add accessibility features (AC: 3, 4)
  - [ ] 7.1 Add `aria-label="Territory Map showing learning journey from Zone 0 to 4"` to section
  - [ ] 7.2 Add `role="img"` to SVG container
  - [ ] 7.3 Add `aria-describedby` to zones if needed
  - [ ] 7.4 Ensure all headings (h3) are in logical order
  - [ ] 7.5 Test keyboard navigation: Tab through zones
  - [ ] 7.6 Verify screen reader announces zone headings and descriptions
  - [ ] 7.7 Test with VoiceOver (macOS) or TalkBack (Android)

- [ ] 8. Implement Zone 4 special styling (AC: 2, 4)
  - [ ] 8.1 Add class `zone-destination` to Zone 4 container
  - [ ] 8.2 Apply ocean mint accent color: `color: var(--ocean-mint-glow)`
  - [ ] 8.3 Add subtle glow effect: `box-shadow: 0 0 30px rgba(64, 224, 208, 0.2)`
  - [ ] 8.4 Add border highlight: `border: 1px solid var(--ocean-mint-glow)`
  - [ ] 8.5 Ensure Zone 4 stands out but doesn't overwhelm other zones
  - [ ] 8.6 Test visual hierarchy: Zone 4 should be focal point

- [ ] 9. Test visual design and spacing (AC: 4)
  - [ ] 9.1 View page on desktop browser (1920x1080)
  - [ ] 9.2 Verify all 5 zones are visible without scrolling
  - [ ] 9.3 Check zones are evenly spaced and aligned
  - [ ] 9.4 Verify text is readable against black background
  - [ ] 9.5 Test Zone 4 accent is visible but not distracting
  - [ ] 9.6 View page on mobile (375x667)
  - [ ] 9.7 Verify vertical layout works well on small screens
  - [ ] 9.8 Check no horizontal scrolling occurs
  - [ ] 9.9 Verify font sizes are legible on mobile

- [ ] 10. Create Playwright visual regression tests (AC: 1, 2, 4)
  - [ ] 10.1 Create `/tests/screenshots/story-2-1-visual.spec.ts` test file
  - [ ] 10.2 Test desktop initial state:
    - Screenshot TerritoryMap section
    - Verify all 5 zones visible
    - Verify Zone 4 has ocean mint accent
    - Check text contrast is sufficient
  - [ ] 10.3 Test mobile viewport (375x667):
    - Screenshot TerritoryMap on mobile
    - Verify vertical zone layout
    - Check responsive text sizes
    - Verify no horizontal scroll
  - [ ] 10.4 Test accessibility:
    - Run Playwright accessibility snapshot
    - Verify ARIA labels present
    - Check heading hierarchy (h3 under section)
    - Verify text contrast ratios (WCAG AA)
  - [ ] 10.5 Test semantic HTML:
    - Verify zone structure (div.zone > h3 + p)
    - Check data-zone attributes present
    - Verify particle container exists
  - [ ] 10.6 Run tests and verify all pass
  - [ ] 10.7 Update screenshot baselines if design intentional

- [ ] 11. Document SVG structure for future stories (AC: 1)
  - [ ] 11.1 Create inline comment in HTML describing SVG structure
  - [ ] 11.2 Document zone positioning for particle targeting (Story 2.2)
  - [ ] 11.3 Note zone coordinates for future hover animations (Story 2.3)
  - [ ] 11.4 Document CSS classes available for animation targeting

## Dev Notes

### Epic Context
This is the **second story** in Epic 2: Territory Map WHOA Moment. Story 2.1 creates the foundational structure (HTML, CSS, SVG) that Stories 2.2 (particle system) and 2.3 (zone illumination and hovers) will build upon.

**Critical Dependencies:**
- Story 1.1 MUST be completed (design tokens, color palette)
- Story 1.2 MUST be completed (GSAP infrastructure)
- Story 2.0 MUST be completed (MapFraming integration patterns)

**Story Sequence:**
- Story 2.0: Pre-Map anticipation framing (COMPLETED)
- **Story 2.1: Territory Map structure** (THIS STORY)
- Story 2.2: Particle coalescence system (NEXT)
- Story 2.3: Zone illumination and magnetic hovers

**Why This Story Matters:**
Without the Territory Map structure, the particle system has nothing to coalesce into. This story:
1. Creates the visual foundation for the WHOA moment
2. Establishes the 5-zone learning journey concept
3. Prepares the particle container for Story 2.2
4. Sets up zone targeting for Story 2.3 animations

### Technical Requirements

#### HTML Structure Pattern (Follow Story 2.0 Integration):

**TerritoryMap.html Structure:**
```html
<!-- TerritoryMap.html -->
<section class="territory-map" id="territory-map" aria-label="Territory Map showing learning journey from Zone 0 to 4">
  <!-- Particle container for Story 2.2 -->
  <div class="particle-container">
    <!-- Particles will be injected here by MapParticles.js in Story 2.2 -->
  </div>

  <!-- SVG visual representation (background layer) -->
  <svg class="map-svg" viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img">
    <!-- Zone shapes and connections -->
    <g class="svg-zone zone-0-shape">
      <!-- Visual representation of Zone 0 -->
    </g>
    <!-- Continue for zones 1-4 -->
  </svg>

  <!-- Zone content (foreground layer) -->
  <div class="map-zones">
    <div class="zone zone-0" data-zone="0">
      <h3>AI isn't for me</h3>
      <p>Where most students start. Feeling overwhelmed.</p>
    </div>

    <div class="zone zone-1" data-zone="1">
      <h3>I could try this</h3>
      <p>First sparks of curiosity.</p>
    </div>

    <div class="zone zone-2" data-zone="2">
      <h3>AI does tasks for me</h3>
      <p>Using it for real work. But inconsistent.</p>
    </div>

    <div class="zone zone-3" data-zone="3">
      <h3>AI understands my intent</h3>
      <p>True collaboration begins.</p>
    </div>

    <div class="zone zone-4 zone-destination" data-zone="4">
      <h3>I control the quality</h3>
      <p>You direct. You refine. You own the outcome. This is where confidence lives.</p>
    </div>
  </div>
</section>
```

**Integration into main.js (Follow Story 2.0 Pattern):**
```javascript
// In main.js (add after MapFraming integration)
import territoryMapHtml from './components/TerritoryMap/TerritoryMap.html?raw';

// After MapFraming append
app.innerHTML += territoryMapHtml;

// TerritoryMap animations will be initialized in Story 2.2
```

#### CSS Styling Strategy:

**Layout Approach: Absolute Positioning (Awwwards-Level Spatial Storytelling)**

**Why Absolute Positioning (Party Mode Team Decision - 2026-01-16):**
- Zones positioned along actual SVG journey path (valley → summit)
- Creates "discovered map" feel vs grid's "checklist" feel
- Matches GSAP masters (Cuberto, Stripe, Apple) spatial storytelling patterns
- Better particle coalescence target positioning (Story 2.2)
- Blue Ocean strategy: organic vs commodity grid layouts

**Recommendation:** Absolute positioning matching SVG coordinates for visual journey progression

**CSS Structure:**
```css
/* TerritoryMap.css - Awwwards-Level Spatial Storytelling */
.territory-map {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  background: #000000; /* Pure black for WHOA moment */
  z-index: 3; /* Above MapFraming */
  overflow: hidden;
}

/* Particle container (for Story 2.2) */
.particle-container {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1; /* Above background, below zones */
  will-change: transform, opacity; /* Prepare for animations */
}

/* SVG background - "The Discovered Map" */
.territory-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 0; /* Behind everything */
  opacity: 0.2; /* More visible for journey path */
  filter: drop-shadow(0 0 20px rgba(32,178,170,0.3)); /* Subtle glow */
}

/* Zone container - Absolute positioning canvas */
.map-zones {
  position: relative;
  z-index: 2; /* Above particles and SVG */
  width: 100%;
  max-width: 1200px; /* Match SVG viewBox */
  height: 800px; /* Match SVG viewBox */
}

/* Individual zone styling - Positioned along journey path */
.zone {
  position: absolute;
  width: 220px; /* Fixed width for positioning */
  padding: 1.5rem;
  border-radius: 12px;
  background: rgba(26, 26, 26, 0.7); /* Frosted glass effect */
  backdrop-filter: blur(20px); /* Modern glass morphism */
  border: 1px solid rgba(255, 255, 255, 0.1);
  transform: translate(-50%, -50%); /* Center on SVG coordinates */
  transition: none; /* GSAP handles animations */
}

/* Zone positioning - Match SVG coordinates (percentage conversion) */
.zone-0 {
  left: 8.3%;   /* 100/1200 */
  bottom: 12.5%; /* (800-700)/800 from bottom */
  opacity: 0.3; /* Ghost state - degrees of becoming */
  filter: blur(2px);
}

.zone-1 {
  left: 33.3%;  /* 400/1200 */
  bottom: 31.25%; /* (800-550)/800 */
  opacity: 0.45; /* Emerging */
  filter: blur(1.5px);
}

.zone-2 {
  left: 54.2%;  /* 650/1200 */
  bottom: 46.25%; /* (800-430)/800 */
  opacity: 0.6; /* Forming */
  filter: blur(1px);
}

.zone-3 {
  left: 75%;    /* 900/1200 */
  bottom: 60%;  /* (800-320)/800 */
  opacity: 0.8; /* Solid */
  filter: blur(0.5px);
}

.zone-4 {
  left: 91.6%;  /* 1100/1200 */
  top: 22.5%;   /* 180/800 from top */
  opacity: 1.0; /* Fully present */
  filter: blur(0); /* Crystal clear */
}

.zone h3 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: clamp(1.25rem, 3vw, 1.75rem);
  font-weight: 700;
  line-height: 1.2;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.zone p {
  font-family: 'Inter', sans-serif;
  font-size: clamp(0.875rem, 2vw, 1rem);
  font-weight: 400;
  line-height: 1.6;
  color: var(--text-secondary);
}

/* Zone 4 destination styling */
.zone-destination {
  border: 2px solid var(--ocean-mint-glow);
  box-shadow: 0 0 30px rgba(64, 224, 208, 0.2);
}

.zone-destination h3 {
  color: var(--ocean-mint-glow); /* #40E0D0 */
}

/* Mobile responsive - Vertical journey */
@media (max-width: 768px) {
  .territory-map {
    padding: 2rem 1rem;
    min-height: auto; /* Let content determine height */
  }

  .map-zones {
    position: relative; /* Switch from absolute positioning */
    height: auto; /* Let content flow */
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .zone {
    position: relative; /* Reset from absolute */
    left: auto !important;
    right: auto !important;
    top: auto !important;
    bottom: auto !important;
    transform: none; /* Reset centering */
    width: 100%; /* Full width on mobile */
    max-width: 400px;
    margin: 0 auto;
    padding: 1.5rem;
    /* Maintain opacity gradient for vertical journey */
  }

  .territory-svg {
    display: none; /* Hide diagonal SVG on mobile */
  }

  .zone h3 {
    font-size: clamp(1rem, 5vw, 1.5rem);
  }

  .zone p {
    font-size: clamp(0.875rem, 4vw, 1rem);
  }
}
```

#### "The Discovered Map" SVG Design Spec

> **Philosophy:** The SVG should feel like it was DISCOVERED, not designed. Organic curves, worn paths, zones that feel like gravity wells where journeys naturally collect.

**Purpose of SVG:**
- Create **pre-recognition** - "something is about to name where I am"
- Show **topographical ascent** - valley (Zone 0) to summit (Zone 4)
- Establish **degrees of becoming** - opacity gradient from ghost to fully present
- Provide **particle coalescence targets** - exact coordinates for Story 2.2

**Zone Coordinates (for particle coalescence in Story 2.2):**
```javascript
// Desktop coordinates (viewBox 1200x800)
const ZONE_COORDINATES = {
  zone0: { x: 100, y: 700, r: 35 },   // Valley - starting point
  zone1: { x: 400, y: 550, r: 38 },   // Foothills
  zone2: { x: 650, y: 430, r: 42 },   // Crossing - midpoint
  zone3: { x: 900, y: 320, r: 46 },   // Ascent
  zone4: { x: 1100, y: 180, r: 55 }   // Summit - destination (GLOWING)
};

// Mobile: Use vertical stack, coordinates become relative to viewport
```

**Complete SVG Implementation:**
```html
<svg class="territory-svg" viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-label="Journey path from Zone 0 to Zone 4">
  <defs>
    <!-- Zone 4 presence glow - strongest attractor -->
    <radialGradient id="destination-glow">
      <stop offset="0%" stop-color="rgba(64,224,208,0.5)" />
      <stop offset="40%" stop-color="rgba(64,224,208,0.2)" />
      <stop offset="100%" stop-color="rgba(64,224,208,0)" />
    </radialGradient>
  </defs>

  <!-- The worn path - organic Bezier curve (NOT straight lines) -->
  <path
    d="M 100,700 C 200,650 300,600 400,550
       S 550,480 650,430
       S 800,380 900,320
       S 1000,250 1100,180"
    stroke="rgba(32,178,170,0.15)"
    stroke-width="4"
    stroke-linecap="round"
    stroke-dasharray="12 6"
    fill="none"
    class="journey-path" />

  <!-- Zone markers - DEGREES OF BECOMING (opacity increases toward Zone 4) -->
  <g class="zone-markers">
    <!-- Zone 0: Ghost state - barely visible -->
    <circle cx="100" cy="700" r="35"
            fill="rgba(26,26,26,0.6)"
            stroke="rgba(255,255,255,0.1)"
            stroke-width="1"
            class="zone-marker zone-0-marker"
            data-zone="0" />

    <!-- Zone 1: Emerging -->
    <circle cx="400" cy="550" r="38"
            fill="rgba(26,26,26,0.65)"
            stroke="rgba(255,255,255,0.15)"
            stroke-width="1"
            class="zone-marker zone-1-marker"
            data-zone="1" />

    <!-- Zone 2: Forming -->
    <circle cx="650" cy="430" r="42"
            fill="rgba(26,26,26,0.7)"
            stroke="rgba(255,255,255,0.2)"
            stroke-width="1.5"
            class="zone-marker zone-2-marker"
            data-zone="2" />

    <!-- Zone 3: Solid -->
    <circle cx="900" cy="320" r="46"
            fill="rgba(26,26,26,0.8)"
            stroke="rgba(32,178,170,0.3)"
            stroke-width="1.5"
            class="zone-marker zone-3-marker"
            data-zone="3" />

    <!-- Zone 4: The destination - FULLY PRESENT with glow -->
    <circle cx="1100" cy="180" r="180"
            fill="url(#destination-glow)"
            class="zone-4-glow" />
    <circle cx="1100" cy="180" r="55"
            fill="rgba(26,26,26,0.9)"
            stroke="rgba(64,224,208,0.8)"
            stroke-width="2"
            class="zone-marker zone-4-marker"
            data-zone="4" />
  </g>
</svg>
```

**Emotional Temperature Mapping:**
| Zone | Visual Temperature | Opacity | Stroke |
|------|-------------------|---------|--------|
| 0 | Cold, isolated, distant | 0.3 | barely visible |
| 1 | Warming, small light | 0.45 | faint |
| 2 | Flickering, unstable | 0.6 | forming |
| 3 | Steady warmth, connection | 0.8 | solid |
| 4 | Radiant, glowing, HOME | 1.0 | GLOWING |

---

### Pre-Recognition Orchestration (Animation Timing)

> **Rule:** Words never LEAD. Words only CONFIRM. The visual must suggest before the copy names.

**Animation Sequence (for Story 2.2/2.3 implementation, but structure must support):**

| Time | Visual Element | Words | Emotional Beat |
|------|----------------|-------|----------------|
| 0.0s | Black screen (night intact) | (none) | Darkness |
| 0.5s | Faint path emerges (worn trail) | (none) | "Something exists here" |
| 1.5s | Zone markers materialize (5 points) | (none) | "There are waypoints" |
| 2.5s | Zone 4 begins glowing (ocean mint) | (none) | "There's a destination" |
| 3.0s | Particles begin journey (Story 2.2) | (none) | "Chaos has structure" |
| 4.0s | Particles coalesce into zones | (none) | "I'm watching my confusion become legible" |
| 5.0s | Zone 0 label appears | "Zone 0" | "Naming begins" |
| 5.3s | Zone 0 tagline fades in | "AI isn't for me" | **RECOGNITION TRIGGER** |
| 5.6s | Zone 1 label + tagline | "Zone 1" / "I could try this" | |
| 6.2s | Zone 2 label + tagline | "Zone 2" / "AI does tasks for me" | |
| 6.8s | Zone 3 label + tagline | "Zone 3" / "AI understands my intent" | |
| 7.5s | Zone 4 label + tagline | "Zone 4" / "I control the quality" | Destination revealed |
| 8.0s | Map complete. Silence. | (none) | "Which zone am I?" |
| 9.0s+ | Descriptions (scroll-reveal) | "Where most students start..." | Confirmation (optional) |

**Key Insight:** 5 seconds of pure visual BEFORE any words. The map SHOWS before it TELLS.

---

### Word Budget: Copy-Visual Intersection Strategy

> **Philosophy:** Graphics create the question. Copy answers with a whisper.

**Recognition Phase (REQUIRED - 22 words total):**
| Zone | Label | Tagline | Words |
|------|-------|---------|-------|
| 0 | "Zone 0" | "AI isn't for me" | 5 |
| 1 | "Zone 1" | "I could try this" | 4 |
| 2 | "Zone 2" | "AI does tasks for me" | 5 |
| 3 | "Zone 3" | "AI understands my intent" | 4 |
| 4 | "Zone 4" | "I control the quality" | 4 |
| **Total** | | | **22** |

**Description Phase (OPTIONAL - scroll-gated, ~50 words):**
- Zone 0: "Where most students start. Feeling overwhelmed." (7 words)
- Zone 1: "First sparks of curiosity." (4 words)
- Zone 2: "Using it for real work. But inconsistent." (8 words)
- Zone 3: "True collaboration begins." (3 words)
- Zone 4: "You direct. You refine. You own the outcome. This is where confidence lives." (13 words)

**Comparison to Traditional Landing Pages:**
- Typical landing page: 500-1000+ words
- Territory Map section: **72 words maximum**
- This is ~7% of typical copy length
- **Surgical precision** - every word earns its place

**Implementation Notes:**
- Zone labels and taglines start with `opacity: 0` in CSS
- Animation reveals them AFTER visual sequence completes
- Descriptions are NOT shown initially - revealed on scroll or hover (Story 2.3)
- Mobile: same word budget, vertical scroll reveals

---

### Architecture Compliance

#### File Structure:
```
k2m-landing/
├── src/
│   ├── main.js                         # Entry point
│   ├── components/
│   │   ├── Hero/                       # Epic 1 (Foundation)
│   │   │   ├── Hero.html
│   │   │   ├── Hero.css
│   │   │   └── Hero.js
│   │   └── TerritoryMap/               # Epic 2 (Territory Map)
│   │       ├── MapFraming.html         # Story 2.0 - Pre-map anticipation
│   │       ├── MapFraming.css          # Story 2.0 - Framing styles
│   │       ├── MapFraming.js           # Story 2.0 - Anticipatory pin
│   │       ├── TerritoryMap.html       # THIS STORY - Map structure
│   │       ├── TerritoryMap.css        # THIS STORY - Map styles
│   │       ├── MapParticles.js         # Story 2.2 - Particle system
│   │       └── Map.css                 # Shared map styles (optional)
│   ├── utils/
│   │   ├── gsap-config.js              # Story 1.2 - GSAP infrastructure
│   │   ├── lenis-config.js             # Story 1.2 - Smooth scroll
│   │   └── performance-optimizations.js # Story 1.2 - GPU, FPS helpers
│   └── styles/
│       └── token.css                   # Story 1.1 - Design tokens
```

**New Files for This Story:**
- `/src/components/TerritoryMap/TerritoryMap.html` - Map HTML structure
- `/src/components/TerritoryMap/TerritoryMap.css` - Map styles

**Files Modified:**
- `/src/main.js` - Import and integrate TerritoryMap (CSS + HTML)

#### Import Pattern (Follow Story 2.0):
```javascript
// In main.js
import territoryMapHtml from './components/TerritoryMap/TerritoryMap.html?raw';
import './components/TerritoryMap/TerritoryMap.css';

// After MapFraming integration
app.innerHTML += territoryMapHtml;

// TerritoryMap.js will be created in Story 2.2 for particle animations
```

### Library/Framework Requirements

#### No New Libraries Required
This story uses existing infrastructure:
- **GSAP** (already installed in Story 1.2) - For future animations (Story 2.2, 2.3)
- **Lenis** (already configured in Story 1.2) - For smooth scroll
- **Design tokens** (already defined in Story 1.1) - For styling consistency

#### CSS Grid Layout (Modern, no library needed):
- Use native CSS Grid for zone layout
- Responsive with media queries
- No external dependencies

#### Inline SVG (No external assets):
- SVG code embedded directly in HTML
- No separate image files
- Scales responsively with viewBox

### Testing Requirements

#### Visual Testing Checklist:

1. **Layout Verification (Desktop):**
   - [ ] All 5 zones visible on desktop (1920x1080)
   - [ ] Zones evenly spaced with proper alignment
   - [ ] Text readable on black background (WCAG AA contrast)
   - [ ] Zone 4 accent visible but not overwhelming
   - [ ] SVG background visible but subtle
   - [ ] No horizontal or vertical overflow

2. **Layout Verification (Mobile):**
   - [ ] Zones stack vertically on mobile (375x667)
   - [ ] No horizontal scrolling
   - [ ] Text sizes appropriate for small screens
   - [ ] Spacing reduced but sufficient
   - [ ] Zone 4 still stands out on mobile
   - [ ] Touch targets large enough (min 44x44px)

3. **Copy Accuracy:**
   - [ ] Zone 0 heading: "AI isn't for me"
   - [ ] Zone 0 description: "Where most students start. Feeling overwhelmed."
   - [ ] Zone 1 heading: "I could try this"
   - [ ] Zone 1 description: "First sparks of curiosity."
   - [ ] Zone 2 heading: "AI does tasks for me"
   - [ ] Zone 2 description: "Using it for real work. But inconsistent."
   - [ ] Zone 3 heading: "AI understands my intent"
   - [ ] Zone 3 description: "True collaboration begins."
   - [ ] Zone 4 heading: "I control the quality"
   - [ ] Zone 4 description: "You direct. You refine. You own the outcome. This is where confidence lives."

4. **Zone 4 Styling:**
   - [ ] Ocean mint accent color applied (#40E0D0)
   - [ ] Border highlight visible
   - [ ] Subtle glow effect (box-shadow) present
   - [ ] Zone 4 is focal point but not overwhelming
   - [ ] Accent works on both desktop and mobile

5. **Accessibility Testing:**
   - [ ] ARIA label present on section
   - [ ] Semantic HTML structure (section > div.zone > h3 + p)
   - [ ] Heading hierarchy logical (h3 under section)
   - [ ] Keyboard navigation works (Tab through zones)
   - [ ] Screen reader announces zone content
   - [ ] Text contrast meets WCAG AA (4.5:1 for body, 3:1 for large text)

6. **Integration Testing:**
   - [ ] MapFraming → TerritoryMap transition smooth
   - [ ] No layout shift between sections
   - [ ] Lenis smooth scroll works across boundary
   - [ ] Pure black background consistent
   - [ ] Section height appropriate (100vh desktop, 80vh mobile)

7. **Particle Container Readiness (for Story 2.2):**
   - [ ] Particle container div exists
   - [ ] Container positioned absolutely with inset: 0
   - [ ] Pointer events disabled (won't block interactions)
   - [ ] Z-index correct (above background, below zones)
   - [ ] will-change property set for future animations

8. **Browser Compatibility:**
   - [ ] Chrome: Layout renders correctly
   - [ ] Safari: CSS Grid works properly
   - [ ] Firefox: Zones aligned properly
   - [ ] Edge: Consistent with Chrome

### Previous Story Intelligence

**Story 2.0 MapFraming (Integration Pattern):**
Story 2.0 established the integration pattern for Epic 2 components:
- Vite ?raw import for HTML files
- CSS import at top of main.js
- HTML append after previous section
- Self-contained component structure (HTML, CSS, JS)

**Apply Same Pattern to TerritoryMap:**
1. Import CSS: `import './components/TerritoryMap/TerritoryMap.css'`
2. Import HTML: `import territoryMapHtml from './components/TerritoryMap/TerritoryMap.html?raw'`
3. Append: `app.innerHTML += territoryMapHtml` (after MapFraming)

**Story 1.5 Performance (Mobile Optimization):**
Story 1.5 taught us to always optimize for mobile:
- Use media queries for responsive design
- Test on real mobile devices (iPhone, Android)
- Ensure 45fps+ performance baseline
- Reduce complexity on mobile (vertical layout, smaller text)

**Story 1.1 Design Tokens (Visual Consistency):**
- Use CSS variables for colors
- Apply Space Grotesk for headings, Inter for body
- Use ocean mint palette for accents
- Maintain pure black background

**Story 1.2 Infrastructure (GSAP Ready):**
- GSAP and ScrollTrigger configured
- Performance utilities available
- Lenis smooth scroll active

### Latest Tech Information

#### CSS Grid Layout (2025):
**Modern Approach for Zone Layout:**
```css
.map-zones {
  display: grid;
  grid-template-columns: repeat(5, 1fr); /* 5 equal columns */
  gap: 2rem; /* Space between zones */
  max-width: 1400px;
  margin: 0 auto; /* Center */
}
```

**Benefits:**
- Responsive and flexible
- Easy to reorder zones
- Built-in gap handling
- Better than flexbox for 2D layouts

**Mobile Responsive:**
```css
@media (max-width: 768px) {
  .map-zones {
    grid-template-columns: 1fr; /* Single column */
    gap: 1.5rem;
  }
}
```

#### Inline SVG Best Practices (2025):
**No External Files Needed:**
```html
<svg class="map-svg" viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img">
  <!-- SVG content here -->
</svg>
```

**Benefits:**
- No additional HTTP requests
- Scales responsively with viewBox
- Styleable with CSS
- Accessible with ARIA

**CSS Styling:**
```css
.map-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  opacity: 0.3;
}
```

#### Data Attributes for JavaScript Targeting (2025):
**HTML Pattern:**
```html
<div class="zone zone-0" data-zone="0">
  <h3>Zone 0 Heading</h3>
  <p>Zone 0 description</p>
</div>
```

**JavaScript Access (Story 2.3):**
```javascript
const zones = document.querySelectorAll('.zone');
zones.forEach(zone => {
  const zoneNumber = zone.dataset.zone; // "0", "1", etc.
  // Use for animations
});
```

**Benefits:**
- Semantic and accessible
- Easy JavaScript selection
- Supports future animations

### Project Context Reference

**Project Name:** k2m-edtech-program-
**Epic:** Epic 2: Territory Map WHOA Moment
**Story:** 2.1 - Create Territory Map SVG Structure
**Target Audience:** Kenyan students interested in AI education

**Emotional Journey (from animation strategy):**
- **Act I (Hero):** Validation - "You're not alone"
- **Act II (Territory Map):** Revelation - "Oh, THIS is where I am"
  - **Pre-scene (Story 2.0):** Anticipation - "Something is about to shift..."
  - **Map Structure (This Story):** Foundation - 5 zones, learning journey visual
  - **WHOA moment (Story 2.2):** Particle coalescence - Chaos → order
  - **Zone Interaction (Story 2.3):** Illumination and hovers
- **Act III (Discord):** Belonging - "This is alive"
- **Act IV (CTA):** Relief - "No pressure, just clarity"

**Color Palette:**
- Pure black (#000000) - Territory Map background
- Ocean mint (#20B2AA, #40E0D0, #008B8B) - Zone 4 accent
- Charcoal (#1A1A1A) - Zone backgrounds (semi-transparent)

**Performance Goals:**
- Desktop: 60fps consistent
- Mobile: 45fps+ acceptable
- Lighthouse Performance: 90+
- No layout shifts (CLS < 0.1)

**Critical Success Factors for This Story:**
1. All 5 zones clearly visible and readable
2. Zone 4 stands out with ocean mint accent
3. Responsive design works on mobile
4. Particle container ready for Story 2.2
5. Semantic HTML for accessibility
6. Integration pattern follows Story 2.0

**Next Stories After This One:**
1. Story 2.2: Build particle coalescence system (200 desktop, 50 mobile particles)
2. Story 2.3: Implement zone illumination and magnetic hovers

**Technical Dependencies:**
- Story 1.1: Design tokens (colors, typography)
- Story 1.2: GSAP infrastructure
- Story 2.0: MapFraming integration pattern

## Dev Agent Record

### Agent Model Used

_Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)_

### Debug Log References

### Completion Notes List

**Story Created: 2026-01-16**

**Comprehensive Analysis Completed:**
- ✅ Extracted requirements from Epic 2 (lines 606-648 in epics.md)
- ✅ Applied integration patterns from Story 2.0 (MapFraming)
- ✅ Incorporated performance patterns from Story 1.5 (mobile optimization)
- ✅ Used design tokens from Story 1.1 (ocean mint accent)
- ✅ Prepared infrastructure for Story 2.2 (particle container)
- ✅ Created foundation for Story 2.3 (data-zone attributes)

**Technical Approach:**
1. **HTML Structure:** Semantic, accessible, with data-zone attributes
2. **CSS Layout:** CSS Grid for responsive 5-zone layout
3. **SVG:** Inline, abstract, background layer for visual context
4. **Zone 4 Accent:** Ocean mint glow to highlight destination
5. **Particle Container:** Prepared for Story 2.2 coalescence animation
6. **Mobile-First:** Vertical layout, responsive text sizes

**Key Design Decisions:**
- **Layout:** CSS Grid over absolute positioning (better responsive)
- **SVG:** Inline over external file (fewer HTTP requests)
- **Zone 4 Accent:** Border + glow (subtle but visible)
- **Particle Container:** Absolute positioning with z-index layering
- **Copy:** Exact text from approved final document

**Performance Considerations:**
- Pure black background (#000000) for WHOA moment
- will-change on particle container (future animation prep)
- CSS Grid for efficient layout
- No external assets (SVG inline)

**Accessibility Features:**
- ARIA label on section
- Semantic HTML (section > div.zone > h3 + p)
- data-zone attributes for future JavaScript
- Keyboard navigable structure
- WCAG AA contrast ratios

**Testing Strategy:**
- Playwright visual regression tests
- Desktop and mobile viewport testing
- Accessibility snapshot verification
- Copy accuracy validation
- Zone 4 accent visibility

**Story Context:**
- Second story in Epic 2
- Creates structural foundation for WHOA moment
- Bridges MapFraming anticipation to particle revelation
- Critical for user understanding of learning journey

### File List

**New Files to Create:**
- `k2m-landing/src/components/TerritoryMap/TerritoryMap.html` - Map structure with zones
- `k2m-landing/src/components/TerritoryMap/TerritoryMap.css` - Map styles with responsive design
- `k2m-landing/tests/screenshots/story-2-1-visual.spec.ts` - Playwright visual tests
- `_bmad-output/implementation-artifacts/2-1-create-territory-map-svg-structure.md` - This story file

**Files to Modify:**
- `k2m-landing/src/main.js` - Import and integrate TerritoryMap

### Change Log

**2026-01-16 - Party Mode Architecture Decision (Sally, Caravaggio, Victor, Winston):**

**Problem Identified:** Initial implementation used horizontal grid layout - felt like "everyday slop" vs Awwwards-level design. Grid layout says "checklist" not "journey."

**Team Analysis of GSAP Storytellers:**
- Cuberto: Elements positioned along SVG paths using MotionPathPlugin
- Stripe: Scroll-triggered opacity + scale transforms
- Apple: Pinned sections with perspective
- Awwwards winners: Particle systems + scroll velocity

**Strategic Decision: Absolute Positioning**
- Zones positioned along actual SVG journey path (valley → summit)
- Creates "discovered map" feel vs commodity grid layouts
- Blue Ocean strategy: organic spatial storytelling
- Opacity gradient (0.3 → 1.0) = "degrees of becoming"
- Backdrop-filter blur for frosted glass effect
- SVG more prominent (opacity 0.2 vs 0.3) with drop-shadow glow
- Mobile: vertical journey (position: relative) instead of diagonal

**CSS Architecture Updated:** Lines 333-507 now reflect absolute positioning approach with percentage-based coordinates matching SVG viewBox (1200x800).

---

**2026-01-16 - Party Mode Validation (Creative Team):**

**Participants:** Bob (SM), Sally (UX), Caravaggio (Visual), Winston (Architect), Amelia (Dev), Sophia (Storyteller), Maya (Design Thinking)

**Major Design Decisions:**
1. **"The Discovered Map" philosophy** - SVG should feel discovered, not designed
2. **Topographical ascent metaphor** - Valley (Zone 0) → Summit (Zone 4)
3. **Degrees of becoming** - Opacity gradient showing increasing presence
4. **Pre-recognition orchestration** - 5 seconds of pure visual before any words
5. **Word budget: 22 words for recognition** - Surgical precision

**Adversarial Review Blockers RESOLVED:**
| # | Blocker | Resolution |
|---|---------|------------|
| 1 | SVG design undefined | ✅ "The Discovered Map" complete spec with Bezier paths, zone markers, opacity gradient |
| 2 | Zone layout progression ambiguous | ✅ Diagonal ascent (bottom-left → top-right), organic curve path |
| 3 | Copy source conflict | ✅ Single source: `k2m-landing-page-copy-final.md` (Task 0.4 updated) |
| 4 | "Particle container prepared" not testable | ✅ Defined: exact coordinates, data attributes, z-index layers |
| 5 | Zone positioning for coalescence undefined | ✅ Exact coordinates: Zone 0 (100,700) → Zone 4 (1100,180) |
| 6 | Text colors not specified | ✅ Follows opacity gradient pattern (0.3→1.0), uses design tokens |
| 7 | Zone wrapper missing from tasks | ✅ HTML structure includes `.map-zones` wrapper |

**New Sections Added:**
- Design Philosophy: "The Discovered Map"
- Master Cartographer Principles table
- Pre-Recognition Orchestration timing table
- Word Budget: Copy-Visual Intersection Strategy
- Complete SVG implementation with zone coordinates
- Emotional Temperature Mapping table

---

**2026-01-16 - Story 2.1 Created (Bob - Scrum Master):**
- Comprehensive story file created for Territory Map SVG Structure
- Requirements extracted from Epic 2 (epics.md lines 606-648)
- Integration pattern applied from Story 2.0 (MapFraming)
- Performance patterns from Story 1.5 (mobile optimization)
- Design tokens from Story 1.1 (ocean mint accent)
- Technical approach: CSS Grid layout, inline SVG, semantic HTML
- Particle container prepared for Story 2.2
- data-zone attributes added for Story 2.3
- Initial status: ready-for-dev
- YOLO mode execution (no user elicitation)
