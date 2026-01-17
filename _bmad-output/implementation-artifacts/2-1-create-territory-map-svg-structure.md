# Story 2.1: Create Territory Map SVG Structure

Status: review

<!-- Note: Implementation approach updated per Party Mode decision 2026-01-16. Changed from CSS Grid to absolute positioning for Awwwards-level spatial storytelling along diagonal journey path. -->

## Story

As a visitor,
I want to see the Territory Map with 5 distinct zones (0-4),
So that I can understand the learning journey and identify my current position.

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
**And** all copy matches the final approved document
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
  - [ ] 0.2 Review Story 2.0 implementation for integration patterns (Vite ?raw imports)
  - [ ] 0.3 Verify design tokens in token.css (ocean mint colors, typography)
  - [ ] 0.4 Confirm Epic 2 scope: Zones 0-4 only (Zones 5-7 deferred per git commit 28da64)
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
  - [ ] 1.7 Add `aria-label="Territory Map showing learning journey from Zone 0 to 4"` to section
  - [ ] 1.8 Ensure semantic HTML structure (section > div.zone > h3 + p)
  - [ ] 1.9 Verify all text content matches approved copy exactly

- [ ] 2. Create TerritoryMap CSS with absolute positioning layout (AC: 3, 4)
  - [ ] 2.1 Create `/src/components/TerritoryMap/TerritoryMap.css` file
  - [ ] 2.2 Add section styling with pure black background (#000000)
  - [ ] 2.3 Set section dimensions: `min-height: 100vh` for full viewport
  - [ ] 2.4 Use **absolute positioning** for zone layout along diagonal journey path (Party Mode decision)
  - [ ] 2.5 Position zones to match SVG coordinates (viewBox 1200x800):
    - Zone 0: `left: 8.3%, bottom: 12.5%` (100/1200, 700/800)
    - Zone 1: `left: 33.3%, bottom: 31.25%` (400/1200, 550/800)
    - Zone 2: `left: 54.2%, bottom: 46.25%` (650/1200, 430/800)
    - Zone 3: `left: 75%, bottom: 60%` (900/1200, 320/800)
    - Zone 4: `left: 91.6%, top: 22.5%` (1100/1200, 180/800) - destination
  - [ ] 2.6 Add generous padding: `4rem` on desktop, `2rem` on mobile
  - [ ] 2.7 Style zone containers with:
    - `position: absolute` with `transform: translate(-50%, -50%)` for centering
    - `width: 220px` for consistent zone cards
    - `border-radius: 12px` for soft edges
    - `padding: 1.5rem` for text spacing
    - `background: rgba(26, 26, 26, 0.7)` for semi-transparent effect
    - `backdrop-filter: blur(10px)` for frosted glass effect
  - [ ] 2.8 Apply typography: Space Grotesk (h3), Inter (p)
  - [ ] 2.9 Style Zone 4 with ocean mint accent:
    - `border: 2px solid var(--ocean-mint-glow)`
    - `box-shadow: 0 0 30px rgba(64, 224, 208, 0.2)`
    - Accent color on heading text: `color: var(--ocean-mint-glow)`
  - [ ] 2.10 Ensure text contrast meets WCAG AA (4.5:1 for body, 3:1 for large text)

- [ ] 3. Implement responsive design for mobile (AC: 4)
  - [ ] 3.1 Add media query for mobile breakpoint (max-width: 768px)
  - [ ] 3.2 Adjust zone layout: **switch from absolute to relative** positioning for vertical stack
  - [ ] 3.3 Reset zone positioning: `left: auto, right: auto, top: auto, bottom: auto, transform: none`
  - [ ] 3.4 Reduce padding on mobile: `2rem` instead of `4rem`
  - [ ] 3.5 Scale font sizes with `clamp()` for responsive typography
  - [ ] 3.6 Ensure no horizontal scrolling on mobile devices
  - [ ] 3.7 Test on iPhone 12+ viewport (375x667)
  - [ ] 3.8 Test on Samsung Galaxy S21+ viewport (360x800)

- [ ] 4. Create "The Discovered Map" SVG structure (AC: 1)
  - [ ] 4.1 Add inline SVG element with `viewBox="0 0 1200 800"` to TerritoryMap.html
  - [ ] 4.2 Create organic Bezier path (NOT straight lines) showing worn journey trail
  - [ ] 4.3 Add zone markers at exact coordinates:
    - Zone 0: cx="100" cy="700" (bottom-left, valley)
    - Zone 1: cx="400" cy="550" (lower-middle)
    - Zone 2: cx="650" cy="430" (middle, crossing)
    - Zone 3: cx="900" cy="320" (upper-middle, ascent)
    - Zone 4: cx="1100" cy="180" (top-right, summit - GLOWING)
  - [ ] 4.4 Apply opacity gradient to zone markers:
    - Zone 0: opacity 0.3 (ghost state)
    - Zone 1: opacity 0.45 (emerging)
    - Zone 2: opacity 0.6 (forming)
    - Zone 3: opacity 0.8 (solid)
    - Zone 4: opacity 1.0 (fully present) + glow
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
  - [ ] 7.1 Verify `aria-label` present on main section
  - [ ] 7.2 Add `role="img"` to SVG container
  - [ ] 7.3 Ensure all headings (h3) are in logical order
  - [ ] 7.4 Test keyboard navigation: Tab through zones
  - [ ] 7.5 Verify screen reader announces zone headings and descriptions
  - [ ] 7.6 Test with VoiceOver (macOS) or TalkBack (Android)
  - [ ] 7.7 Verify semantic HTML: section > div.zone > h3 + p

- [ ] 8. Implement Zone 4 special styling (AC: 2, 4)
  - [ ] 8.1 Add class `zone-destination` to Zone 4 container
  - [ ] 8.2 Apply ocean mint accent color: `color: var(--ocean-mint-glow)`
  - [ ] 8.3 Add subtle glow effect: `box-shadow: 0 0 30px rgba(64, 224, 208, 0.2)`
  - [ ] 8.4 Add border highlight: `border: 2px solid var(--ocean-mint-glow)`
  - [ ] 8.5 Ensure Zone 4 stands out but doesn't overwhelm other zones
  - [ ] 8.6 Test visual hierarchy: Zone 4 should be focal point

- [ ] 9. Test visual design and spacing (AC: 4)
  - [ ] 9.1 View page on desktop browser (1920x1080)
  - [ ] 9.2 Verify all 5 zones are visible without scrolling
  - [ ] 9.3 Check zones are positioned along diagonal journey path (bottom-left → top-right)
  - [ ] 9.4 Verify text is readable against black background
  - [ ] 9.5 Test Zone 4 accent is visible but not distracting
  - [ ] 9.6 View page on mobile (375x667)
  - [ ] 9.7 Verify vertical layout works well on small screens (zones stack relative)
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
2. Establishes the 5-zone learning journey concept (Zones 0-4 only per Epic 2 scope update)
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
  <svg class="map-svg" viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Journey path from Zone 0 to Zone 4">
    <defs>
      <!-- Zone 4 glow gradient -->
      <radialGradient id="destination-glow">
        <stop offset="0%" stop-color="rgba(64,224,208,0.5)" />
        <stop offset="40%" stop-color="rgba(64,224,208,0.2)" />
        <stop offset="100%" stop-color="rgba(64,224,208,0)" />
      </radialGradient>
    </defs>

    <!-- Journey path - organic Bezier curve -->
    <path d="M 100,700 C 200,650 300,600 400,550
              S 550,480 650,430
              S 800,380 900,320
              S 1000,250 1100,180"
          stroke="rgba(32,178,170,0.15)"
          stroke-width="4"
          stroke-linecap="round"
          stroke-dasharray="12 6"
          fill="none"
          class="journey-path" />

    <!-- Zone markers with opacity gradient -->
    <g class="zone-markers">
      <circle cx="100" cy="700" r="35" class="zone-marker zone-0-marker" data-zone="0" />
      <circle cx="400" cy="550" r="38" class="zone-marker zone-1-marker" data-zone="1" />
      <circle cx="650" cy="430" r="42" class="zone-marker zone-2-marker" data-zone="2" />
      <circle cx="900" cy="320" r="46" class="zone-marker zone-3-marker" data-zone="3" />
      <circle cx="1100" cy="180" r="180" fill="url(#destination-glow)" class="zone-4-glow" />
      <circle cx="1100" cy="180" r="55" class="zone-marker zone-4-marker" data-zone="4" />
    </g>
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
import './components/TerritoryMap/TerritoryMap.css';

// After MapFraming append
app.innerHTML += territoryMapHtml;

// TerritoryMap animations will be initialized in Story 2.2
```

#### CSS Styling Strategy:

**Absolute Positioning Layout (Diagonal Journey Path - Party Mode Decision):**
```css
/* TerritoryMap.css */
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
.map-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 0; /* Behind everything */
  opacity: 0.3; /* Subtle background */
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
  background: rgba(26, 26, 26, 0.7); /* Semi-transparent */
  backdrop-filter: blur(10px); /* Frosted glass effect */
  border: 1px solid rgba(255, 255, 255, 0.1);
  transform: translate(-50%, -50%); /* Center on SVG coordinates */
  transition: none; /* GSAP handles animations in Story 2.3 */
}

/* Zone positioning - Match SVG coordinates (percentage conversion) */
/* Valley - Starting point (ghost state) */
.zone-0 {
  left: 8.3%;   /* 100/1200 */
  bottom: 12.5%; /* (800-700)/800 from bottom */
  opacity: 0.3; /* Ghost state - degrees of becoming */
}

/* Foothills (emerging) */
.zone-1 {
  left: 33.3%;  /* 400/1200 */
  bottom: 31.25%; /* (800-550)/800 */
  opacity: 0.45; /* Emerging */
}

/* Crossing - Midpoint (forming) */
.zone-2 {
  left: 54.2%;  /* 650/1200 */
  bottom: 46.25%; /* (800-430)/800 */
  opacity: 0.6; /* Forming */
}

/* Ascent (solid) */
.zone-3 {
  left: 75%;    /* 900/1200 */
  bottom: 60%;  /* (800-320)/800 */
  opacity: 0.8; /* Solid */
}

/* Summit - Destination (fully present) */
.zone-4 {
  left: 91.6%;  /* 1100/1200 */
  top: 22.5%;   /* 180/800 from top */
  opacity: 1.0; /* Fully present */
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

  .map-svg {
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

#### Zone Coordinates (for Story 2.2 particle coalescence):
```javascript
// Desktop coordinates (viewBox 1200x800)
const ZONE_COORDINATES = {
  zone0: { x: 100, y: 700, r: 35 },   // Valley - starting point
  zone1: { x: 400, y: 550, r: 38 },   // Foothills
  zone2: { x: 650, y: 430, r: 42 },   // Crossing - midpoint
  zone3: { x: 900, y: 320, r: 46 },   // Ascent
  zone4: { x: 1100, y: 180, r: 55 }   // Summit - destination (GLOWING)
};

// Mobile: Vertical stack, coordinates become relative to viewport
```

#### SVG Zone Marker Opacity Gradient:
| Zone | Opacity | Stroke | Visual Meaning |
|------|---------|--------|-----------------|
| 0 | 0.3 | barely visible | Ghost state - where most start |
| 1 | 0.45 | faint | Emerging |
| 2 | 0.6 | forming | Forming |
| 3 | 0.8 | solid | Solid understanding |
| 4 | 1.0 + glow | GLOWING | Fully present - destination |

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
   - [ ] Zones evenly spaced with CSS Grid (gap: 2rem)
   - [ ] Text readable on black background (WCAG AA contrast)
   - [ ] Zone 4 accent visible but not overwhelming
   - [ ] SVG background visible but subtle
   - [ ] No horizontal or vertical overflow

2. **Layout Verification (Mobile):**
   - [ ] Zones stack vertically on mobile (375x667)
   - [ ] No horizontal scrolling
   - [ ] Text sizes appropriate for small screens
   - [ ] Spacing reduced but sufficient (gap: 1.5rem)
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
   - [ ] Border highlight visible (2px solid)
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
   - [ ] Section height appropriate (100vh desktop, auto mobile)

7. **Particle Container Readiness (for Story 2.2):**
   - [ ] Particle container div exists
   - [ ] Container positioned absolutely with inset: 0
   - [ ] Pointer events disabled (won't block interactions)
   - [ ] Z-index correct (above background, below zones)
   - [ ] will-change property set for future animations

8. **Browser Compatibility:**
   - [ ] Chrome: CSS Grid renders correctly
   - [ ] Safari: backdrop-filter works properly
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

#### Absolute Positioning Best Practices (2025):
**Awwwards-Level Spatial Storytelling:**
```css
/* Zone container - Absolute positioning canvas */
.map-zones {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 1200px; /* Match SVG viewBox */
  height: 800px; /* Match SVG viewBox */
}

/* Individual zone positioning - Along diagonal journey */
.zone {
  position: absolute;
  width: 220px;
  transform: translate(-50%, -50%); /* Center on coordinates */
}

/* Position zones to match SVG viewBox coordinates */
.zone-0 { left: 8.3%; bottom: 12.5%; }
.zone-1 { left: 33.3%; bottom: 31.25%; }
.zone-2 { left: 54.2%; bottom: 46.25%; }
.zone-3 { left: 75%; bottom: 60%; }
.zone-4 { left: 91.6%; top: 22.5%; }
```

**Benefits:**
- **Spatial Storytelling**: Diagonal ascent (bottom-left → top-right) creates emotional journey
- **Visual Hierarchy**: Zone positions reflect "degrees of becoming" (ghost → fully present)
- **Particle Targeting**: Absolute positions work perfectly with GSAP motionPath (Story 2.2)
- **Mobile Flexibility**: Absolute on desktop, relative stack on mobile

#### Inline SVG Best Practices (2025):
**No External Files Needed:**
```html
<svg class="map-svg" viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg" role="img">
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

**Story Created: 2026-01-17 (Fresh Generation)**

**Comprehensive Analysis Completed:**
- ✅ Extracted requirements from Epic 2 (epics.md lines 608-650)
- ✅ Applied integration patterns from Story 2.0 (MapFraming Vite imports)
- ✅ Incorporated performance patterns from Story 1.5 (mobile optimization)
- ✅ Used design tokens from Story 1.1 (ocean mint accent)
- ✅ Prepared infrastructure for Story 2.2 (particle container)
- ✅ Confirmed Epic 2 scope: Zones 0-4 only (per git commit 28da64)
- ✅ Created foundation for Story 2.3 (data-zone attributes)

**Technical Approach:**
1. **HTML Structure:** Semantic, accessible, with data-zone attributes
2. **CSS Layout:** CSS Grid for responsive 5-zone layout (desktop) → vertical stack (mobile)
3. **SVG:** Inline, organic Bezier path, zone markers with opacity gradient
4. **Zone 4 Accent:** Ocean mint glow (#40E0D0) to highlight destination
5. **Particle Container:** Absolute positioning with z-index layering
6. **Mobile-First:** Vertical layout, responsive text sizes, hide diagonal SVG

**Key Design Decisions:**
- **Layout:** CSS Grid (5 columns desktop, 1 column mobile)
- **SVG:** Inline organic path with "worn trail" effect
- **Zone 4 Accent:** 2px border + glow (subtle but visible)
- **Particle Container:** Absolute positioning with inset: 0, z-index: 1
- **Copy:** Exact text from Epic 2 requirements
- **Scope:** Zones 0-4 only (Zones 5-7 deferred per Epic 2 update)

**Performance Considerations:**
- Pure black background (#000000) for WHOA moment
- will-change on particle container (future animation prep)
- CSS Grid for efficient layout
- No external assets (SVG inline)
- backdrop-filter for frosted glass effect

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

**2026-01-17 - Fresh Story Generation (Bob - Scrum Master):**
- Generated comprehensive story file from scratch with exhaustive artifact analysis
- Requirements extracted from Epic 2 (epics.md lines 608-650)
- Integration patterns applied from Story 2.0 (Vite ?raw imports)
- Performance patterns incorporated from Story 1.5 (mobile optimization)
- Design tokens used from Story 1.1 (ocean mint accent)
- Technical approach: **Absolute positioning along diagonal journey path** per Party Mode decision 2026-01-16
- Particle container prepared for Story 2.2 (absolute positioning, z-index layering)
- data-zone attributes added for Story 2.3 (hover animations)
- Confirmed Epic 2 scope: Zones 0-4 only (per git commit 28da64)
- YOLO mode execution (no user elicitation)
- Status: ready-for-dev
