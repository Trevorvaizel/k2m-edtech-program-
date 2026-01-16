# Story 2.1: Create Territory Map SVG Structure

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a visitor,
I want to see the Territory Map with 5 distinct zones (0-4),
So that I can understand the learning journey and identify my current position.

## Acceptance Criteria

**Given** the Hero section is complete
**When** I create `/src/components/TerritoryMap/TerritoryMap.html`
**Then** a map section exists with:
  - Container for particle system
  - Inline SVG with 5 zone groups (0, 1, 2, 3, 4)
  - Each zone has title and description text
  - Zone 4 has ocean mint accent styling
**And** the map is centered on the page
**And** zones are visually distinct

**Given** the zones need content
**When** I add zone text
**Then** each zone displays:
  - Zone 0: "AI isn't for me" with "Where most students start. Feeling overwhelmed."
  - Zone 1: "I could try this" with "First sparks of curiosity."
  - Zone 2: "AI does tasks for me" with "Using it for real work. But inconsistent."
  - Zone 3: "AI understands my intent" with "True collaboration begins."
  - Zone 4: "I control the quality" with "You direct. You refine. You own the outcome. This is where confidence lives."
**And** all copy matches the final document

**Given** I need interactive elements
**When** I structure the HTML
**Then** each zone has `data-zone` attribute
**And** zones have class names for styling and animation targeting
**And** zones are semantically structured (headings, paragraphs)
**And** zones are accessible with keyboard navigation

**Given** the map structure exists
**When** I view the page
**Then** all 5 zones are visible
**And** text is readable on black background
**And** Zone 4 stands out with ocean mint accent
**And** the layout is responsive (mobile friendly)

## Tasks / Subtasks

- [ ] 1. Create TerritoryMap component directory and HTML structure (AC: 1)
  - [ ] 1.1 Create `/src/components/TerritoryMap/` directory
  - [ ] 1.2 Create `TerritoryMap.html` with map section structure
  - [ ] 1.3 Add particle system container div
  - [ ] 1.4 Create inline SVG with viewport and coordinate system
  - [ ] 1.5 Add 5 zone groups (`<g class="zone" data-zone="0">` etc.)
  - [ ] 1.6 Verify HTML is semantic and accessible

- [ ] 2. Implement zone content and copy (AC: 2)
  - [ ] 2.1 Add Zone 0 content: "AI isn't for me" + description
  - [ ] 2.2 Add Zone 1 content: "I could try this" + description
  - [ ] 2.3 Add Zone 2 content: "AI does tasks for me" + description
  - [ ] 2.4 Add Zone 3 content: "AI understands my intent" + description
  - [ ] 2.5 Add Zone 4 content: "I control the quality" + description
  - [ ] 2.6 Verify all copy matches epics.md final document
  - [ ] 2.7 Apply ocean mint accent styling to Zone 4

- [ ] 3. Add interactive attributes and semantic structure (AC: 3)
  - [ ] 3.1 Add `data-zone` attribute to each zone (0-4)
  - [ ] 3.2 Add CSS class names for targeting (`.zone`, `.zone-0`, etc.)
  - [ ] 3.3 Structure with semantic HTML (`<heading>`, `<p>`)
  - [ ] 3.4 Ensure keyboard accessibility (tab order, ARIA labels)
  - [ ] 3.5 Add `role="img"` and `aria-label` to SVG
  - [ ] 3.6 Test with screen reader if possible

- [ ] 4. Create Map.css with styling (AC: 4)
  - [ ] 4.1 Create `/src/components/TerritoryMap/Map.css`
  - [ ] 4.2 Style map section with black background
  - [ ] 4.3 Center map on page (flexbox or grid)
  - [ ] 4.4 Style zones to be visually distinct
  - [ ] 4.5 Apply ocean mint color to Zone 4 (`--ocean-mint-primary`)
  - [ ] 4.6 Ensure text contrast meets WCAG AA (4.5:1)
  - [ ] 4.7 Add responsive breakpoints for mobile

- [ ] 5. Implement responsive design (AC: 4)
  - [ ] 5.1 Test on desktop (1920×1080)
  - [ ] 5.2 Test on tablet (iPad)
  - [ ] 5.3 Test on mobile (iPhone 12+, Android)
  - [ ] 5.4 Ensure zones stack or scale appropriately
  - [ ] 5.5 Verify no horizontal scrolling on mobile
  - [ ] 5.6 Test text readability on all screen sizes

- [ ] 6. Integrate TerritoryMap into main application
  - [ ] 6.1 Import TerritoryMap.html in main.js or index.html
  - [ ] 6.2 Import Map.css in main.js or index.html
  - [ ] 6.3 Position TerritoryMap after Hero section
  - [ ] 6.4 Verify section order: Hero → Territory Map
  - [ ] 6.5 Test page loads without errors
  - [ ] 6.6 Verify map appears on scroll

## Dev Notes

### Epic Context
This is the **second story** in Epic 2: Territory Map WHOA Moment. Story 2.0 (Pre-Map Anticipation Framing) should ideally be completed first, but this story focuses on the static structure of the Territory Map itself.

**Critical Dependencies:**
- Story 1.1 MUST be completed (design tokens, typography, colors)
- Story 1.2 MUST be completed (GSAP + Lenis infrastructure)
- Story 1.3 SHOULD be completed (Hero section for context)
- Hero section provides the emotional foundation ("You're not alone")
- This story creates the visual structure for the particle system (Story 2.2)

**Why This Story Matters:**
The Territory Map is the **WHOA moment** of the landing page. It's where visitors experience revelation - "Oh, THIS is where I am." The static structure created here becomes the canvas for the particle coalescence animation (Story 2.2) and zone illumination effects (Story 2.3).

**Emotional Design Goal:**
- Zone 0-1 visitors feel: "This sees me. They understand where I'm starting."
- Zone 2-3 visitors feel: "I'm on the path. I can get to Zone 4."
- Zone 4 visitors feel: "This is advanced. I want to master this."
- Overall: "The map lights the way. I'm not alone in this journey."

### Technical Requirements

#### File Structure (Following Story 1.3 Pattern):
```
k2m-landing/
├── src/
│   ├── main.js                 # Entry JavaScript
│   ├── components/             # Component-based architecture
│   │   ├── Hero/               # Hero component (Story 1.3, 1.4)
│   │   │   ├── Hero.html
│   │   │   ├── Hero.css
│   │   │   └── Hero.js
│   │   └── TerritoryMap/       # Territory Map component (THIS STORY)
│   │       ├── TerritoryMap.html  # Map HTML structure
│   │       ├── Map.css            # Map-specific styles
│   │       ├── MapParticles.js    # Particle system (Story 2.2)
│   │       └── TerritoryMap.js    # Map interactions (Story 2.3)
│   ├── utils/                  # Utility functions (Story 1.2)
│   │   ├── gsap-config.js
│   │   ├── lenis-config.js
│   │   └── performance-optimizations.js
│   └── styles/
│       └── token.css           # Design tokens (Story 1.1)
```

**Component Pattern:**
- Self-contained component (HTML + CSS in dedicated directory)
- Shared utilities live in `/src/utils/`
- Global styles live in `/src/styles/`
- Consistent with Hero component structure

#### TerritoryMap.html Structure:
```html
<section class="territory-map" id="territory-map">
  <!-- Particle system container for Story 2.2 -->
  <div class="particle-container">
    <!-- Particles will be injected by MapParticles.js -->
  </div>

  <!-- Territory Map SVG -->
  <svg
    class="territory-map-svg"
    viewBox="0 0 1200 800"
    role="img"
    aria-label="Territory Map showing 5 zones of AI learning journey"
  >
    <!-- Background -->
    <rect class="map-background" width="1200" height="800" fill="#000000" />

    <!-- Zone 0: "AI isn't for me" -->
    <g class="zone zone-0" data-zone="0" tabindex="0">
      <text x="200" y="150" class="zone-title">Zone 0</text>
      <text x="200" y="180" class="zone-heading">"AI isn't for me"</text>
      <text x="200" y="210" class="zone-description">
        Where most students start. Feeling overwhelmed.
      </text>
    </g>

    <!-- Zone 1: "I could try this" -->
    <g class="zone zone-1" data-zone="1" tabindex="0">
      <text x="400" y="300" class="zone-title">Zone 1</text>
      <text x="400" y="330" class="zone-heading">"I could try this"</text>
      <text x="400" y="360" class="zone-description">
        First sparks of curiosity.
      </text>
    </g>

    <!-- Zone 2: "AI does tasks for me" -->
    <g class="zone zone-2" data-zone="2" tabindex="0">
      <text x="600" y="450" class="zone-title">Zone 2</text>
      <text x="600" y="480" class="zone-heading">"AI does tasks for me"</text>
      <text x="600" y="510" class="zone-description">
        Using it for real work. But inconsistent.
      </text>
    </g>

    <!-- Zone 3: "AI understands my intent" -->
    <g class="zone zone-3" data-zone="3" tabindex="0">
      <text x="800" y="600" class="zone-title">Zone 3</text>
      <text x="800" y="630" class="zone-heading">"AI understands my intent"</text>
      <text x="800" y="660" class="zone-description">
        True collaboration begins.
      </text>
    </g>

    <!-- Zone 4: "I control the quality" (Highlighted) -->
    <g class="zone zone-4 zone-highlight" data-zone="4" tabindex="0">
      <text x="1000" y="750" class="zone-title">Zone 4</text>
      <text x="1000" y="780" class="zone-heading">"I control the quality"</text>
      <text x="1000" y="810" class="zone-description">
        You direct. You refine. You own the outcome. This is where confidence lives.
      </text>

      <!-- Ocean mint accent circle for Zone 4 -->
      <circle
        class="zone-accent"
        cx="1000"
        cy="750"
        r="50"
        fill="none"
        stroke="var(--ocean-mint-primary)"
        stroke-width="2"
        opacity="0.5"
      />
    </g>
  </svg>

  <!-- Map introduction text (optional) -->
  <div class="map-intro">
    <h2 class="map-title">We don't teach tools. We guide you through territory.</h2>
    <p class="map-subtitle">In 6 weeks, Zone 0 → early Zone 4</p>
  </div>
</section>
```

**HTML Structure Explained:**
- `.particle-container`: Empty div for particle system (Story 2.2)
- `svg`: Inline SVG for crisp rendering at any size
- `viewBox`: Defines coordinate system (1200×800)
- `role="img"`: ARIA role for accessibility
- `aria-label`: Describes map content for screen readers
- `.zone`: CSS class for styling all zones
- `.zone-0`, `.zone-1`, etc.: Zone-specific classes
- `data-zone`: Data attribute for JavaScript targeting (Story 2.3)
- `tabindex="0"`: Makes zones keyboard accessible
- `.zone-highlight`: Special styling for Zone 4
- `.zone-accent`: Ocean mint circle for Zone 4

**Note:** The coordinate system above is a placeholder. The actual SVG should be designed in Figma/Illustrator with proper spatial layout. Consider a diagonal progression from bottom-left (Zone 0) to top-right (Zone 4) to visually represent the journey upward.

#### Map.css Styling:
```css
/* Territory Map Section */
.territory-map {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: var(--pure-black);
  z-index: 1;
}

/* Particle System Container (for Story 2.2) */
.particle-container {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none; /* Let clicks pass through to zones */
}

/* Territory Map SVG */
.territory-map-svg {
  width: 100%;
  max-width: 1200px;
  height: auto;
  display: block;
  z-index: 3;
}

/* Map Background */
.map-background {
  fill: var(--pure-black);
}

/* All Zones */
.zone {
  cursor: pointer;
  transition: all 0.3s ease;
}

.zone:hover,
.zone:focus {
  opacity: 1;
  outline: 2px solid var(--ocean-mint-primary);
  outline-offset: 4px;
}

/* Zone Text Styles */
.zone-title {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 24px;
  fill: var(--text-primary);
}

.zone-heading {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  font-size: 20px;
  fill: var(--text-secondary);
}

.zone-description {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 14px;
  fill: var(--text-muted);
  max-width: 200px;
}

/* Zone 4 Highlight */
.zone-highlight .zone-heading,
.zone-highlight .zone-title {
  fill: var(--ocean-mint-primary);
}

.zone-accent {
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    opacity: 0.3;
    r: 50;
  }
  50% {
    opacity: 0.6;
    r: 55;
  }
}

/* Map Introduction Text */
.map-intro {
  text-align: center;
  margin-top: 2rem;
  z-index: 4;
}

.map-title {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.map-subtitle {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: clamp(1rem, 2vw, 1.25rem);
  color: var(--text-secondary);
}

/* Responsive Design */
@media (max-width: 768px) {
  .territory-map {
    padding: 1rem;
  }

  .territory-map-svg {
    max-width: 100%;
  }

  .zone-title {
    font-size: 18px;
  }

  .zone-heading {
    font-size: 16px;
  }

  .zone-description {
    font-size: 12px;
  }

  .map-intro {
    padding: 0 1rem;
  }
}
```

**CSS Key Features:**
- Flexbox centering for map and text
- Design token variables from Story 1.1
- Ocean mint accent on Zone 4 only
- Subtle pulse animation on Zone 4 accent circle
- Keyboard focus outline for accessibility
- Responsive font sizes with `clamp()`
- Mobile-optimized spacing

#### Integration with Main Application:
```javascript
// In /src/main.js
import { initHeroAnimations } from './components/Hero/Hero.js';
import './components/Hero/Hero.css';

// Import Territory Map (this story)
import './components/TerritoryMap/TerritoryMap.html';
import './components/TerritoryMap/Map.css';

// Initialize Hero animations
window.addEventListener('load', () => {
  initHeroAnimations();
  // Map particle animations will be added in Story 2.2
  // Map interactions will be added in Story 2.3
});
```

**HTML Import Pattern:**
```html
<!-- In /index.html -->
<head>
  <!-- ... other imports ... -->
  <link rel="stylesheet" href="/src/components/TerritoryMap/Map.css">
</head>
<body>
  <!-- Hero section -->
  <section class="hero">...</section>

  <!-- Territory Map section -->
  <link rel="import" href="/src/components/TerritoryMap/TerritoryMap.html">

  <!-- ... other sections ... -->
</body>
```

**Note:** Vite supports direct HTML imports via `@vitejs/plugin-vue` or similar. If not available, include TerritoryMap.html content directly in `index.html`.

### Architecture Compliance

#### Component-Based Architecture (Established in Epic 1):
- **Self-contained:** Territory Map has its own HTML, CSS (and future JS)
- **Reusable:** Map component can be moved or modified independently
- **Testable:** Map can be developed in isolation
- **Consistent:** Follows Hero component pattern

#### Design Tokens (From Story 1.1):
```css
/* Colors used in this story */
--pure-black: #000000        /* Map background */
--ocean-mint-primary: #20B2AA  /* Zone 4 highlight */
--ocean-mint-glow: #40E0D0    /* Zone 4 accent glow */
--text-primary: #FFFFFF       /* Zone titles */
--text-secondary: #B0B0B0     /* Zone headings */
--text-muted: #6A6A6A        /* Zone descriptions */
```

**Typography:**
- Headings (`.zone-title`, `.map-title`): Space Grotesk 700
- Subheadings (`.zone-heading`): Space Grotesk 600
- Body (`.zone-description`, `.map-subtitle`): Inter 400
- Font display: swap (configured in Story 1.1)

#### Semantic HTML:
- `<section>` for map container (landmark region)
- `<svg>` with `role="img"` for graphics
- `<text>` SVG elements for content (searchable, accessible)
- `aria-label` on SVG for screen readers
- `tabindex="0"` on zones for keyboard navigation
- Semantic heading structure within map intro

#### Accessibility Requirements (From Epics NFR8):
- **Color Contrast:** All text must meet WCAG AA (4.5:1 for normal text)
- **Keyboard Navigation:** All zones focusable with Tab key
- **Screen Reader:** SVG has `aria-label`, zones are readable
- **Focus Indicators:** `:focus` state has visible outline
- **Semantic Markup:** Proper heading hierarchy, landmark regions

**Testing Accessibility:**
1. Test with keyboard: Tab through all zones
2. Test with screen reader: Verify zone descriptions are read
3. Test color contrast: Use Chrome DevTools Lighthouse audit
4. Test with browser zoom: 200% zoom should remain usable

#### Performance Requirements (From Epics NFR1, NFR2):
- **GPU Acceleration:** Use `transform` and `opacity` for future animations
- **No Layout Thrashing:** Future animations won't use width/height/top/left
- **60fps Desktop / 45fps Mobile:** Target for particle system (Story 2.2)
- **Lighthouse 90+:** Optimize SVG file size, use inline SVG (no HTTP request)

**SVG Optimization:**
- Use `viewBox` for responsiveness (no width/height attributes)
- Remove unnecessary `<defs>` and unused elements
- Minify SVG (remove unnecessary whitespace)
- Consider using SVGOMG tool before final implementation

### Library/Framework Requirements

#### GSAP + ScrollTrigger (From Story 1.2):
- **Story 2.2 will use:** GSAP for particle coalescence animation
- **Story 2.3 will use:** GSAP for zone illumination and magnetic hovers
- **This story:** Just HTML/CSS structure - no JS yet

**Future GSAP Integration:**
```javascript
// Story 2.2: Particle system
import { gsap, ScrollTrigger } from '../../utils/gsap-config.js';

// Story 2.3: Zone interactions
gsap.utils.toArray('.zone').forEach(zone => {
  // Magnetic hover effect
  // Zone illumination animation
});
```

#### Lenis Smooth Scroll (From Story 1.2):
- Active globally from Story 1.2
- Will create luxurious scroll feel when user reaches map
- No additional code needed for this story

#### Performance Utilities (From Story 1.2):
```javascript
// Will be used in Story 2.2 and 2.3
import { isMobile, monitorPerformance } from '../../utils/performance-optimizations.js';

if (isMobile()) {
  // Reduce particle count or simplify animations
}
```

### Testing Requirements

#### Manual Testing Checklist:

1. **Structure Verification:**
   - [ ] Map section appears after Hero section
   - [ ] All 5 zones are visible
   - [ ] Zone content matches epic requirements exactly
   - [ ] SVG renders without distortion
   - [ ] Particle container is present (but empty for now)

2. **Visual Design:**
   - [ ] Map is centered on page
   - [ ] Zones are visually distinct (different positions)
   - [ ] Zone 4 stands out with ocean mint accent
   - [ ] Text is readable on black background
   - [ ] Zone 4 accent circle pulses subtly
   - [ ] Overall aesthetic matches "luxury" brand feel

3. **Responsive Design:**
   - [ ] Desktop (1920×1080): Map uses full width appropriately
   - [ ] Tablet (iPad): Zones scale down, remain readable
   - [ ] Mobile (iPhone 12+, Android): Text stacks or scales
   - [ ] No horizontal scrolling on any device
   - [ ] SVG maintains aspect ratio
   - [ ] Touch targets are large enough (44×44px minimum)

4. **Accessibility:**
   - [ ] Keyboard: Tab key navigates through all zones
   - [ ] Keyboard: Enter/Space key activates zone (future feature)
   - [ ] Screen reader: Zone titles and descriptions are read
   - [ ] Focus indicator: Visible outline on focused zone
   - [ ] Color contrast: All text passes WCAG AA (4.5:1)
   - [ ] Semantic HTML: Proper use of `<section>`, `<svg>`, `<text>`

5. **Browser Compatibility:**
   - [ ] Chrome (primary development browser)
   - [ ] Safari (macOS and iOS)
   - [ ] Firefox
   - [ ] Edge
   - [ ] Mobile browsers (Android Chrome, iOS Safari)

6. **Performance:**
   - [ ] SVG loads instantly (no external HTTP request)
   - [ ] No console errors or warnings
   - [ ] Lighthouse Performance score not impacted
   - [ ] Lighthouse Accessibility score 95+
   - [ ] Page load time not significantly increased

7. **Integration:**
   - [ ] Map imports correctly in main.js/index.html
   - [ ] CSS loads without conflicts
   - [ ] Design tokens are applied correctly
   - [ ] Hero section scrolls to map section smoothly
   - [ ] No conflicts with Hero component styles

#### Automated Testing (Future):
- **Playwright:** Visual regression tests for map layout
- **Lighthouse CI:** Accessibility and performance scores
- **Pa11y:** Automated accessibility testing

### Previous Story Intelligence

**Story 1.3 Patterns to Follow:**
- Component structure: `/src/components/TerritoryMap/` with TerritoryMap.html, Map.css
- HTML structure: Semantic markup with ARIA attributes
- CSS classes: BEM-like naming (`.territory-map`, `.zone-title`)
- Import patterns: ES6 imports or HTML imports
- Design tokens: Use CSS variables from Story 1.1

**Critical Files from Story 1.1:**
- `/src/styles/token.css` - Design tokens (ocean mint colors, typography)
- Tailwind config: Custom colors if using Tailwind

**Critical Files from Story 1.2:**
- `/src/utils/gsap-config.js` - GSAP and ScrollTrigger (for future stories)
- `/src/utils/performance-optimizations.js` - `isMobile()` utility
- Lenis smooth scroll - Active globally

**Critical Context from Story 1.3:**
- Hero section sets emotional tone ("You're not alone")
- Pure black background (#000000) established
- Ocean mint accent color (#20B2AA) introduced
- Space Grotesk + Inter typography applied
- Component architecture established

**Story 1.4 Patterns (Animation Foundation):**
- GSAP timeline with ScrollTrigger
- Text reveals with stagger
- Ocean mint glow effects
- Performance optimizations (GPU acceleration)
- Safari compatibility considerations

**Applying Story 1.4 Learnings:**
- Map structure should be animation-ready (use CSS classes for targeting)
- Design particle container with GPU acceleration in mind
- Plan for `will-change: transform, opacity` in future stories
- Test Safari compatibility early (SVG rendering quirks)

### Latest Tech Information

#### Inline SVG Best Practices (2025):
```html
<!-- ✅ RIGHT - Responsive SVG with viewBox -->
<svg viewBox="0 0 1200 800" class="territory-map-svg">
  <!-- Content -->
</svg>

<!-- ❌ WRONG - Fixed width/height breaks responsiveness -->
<svg width="1200" height="800">
  <!-- Content -->
</svg>
```

**Why `viewBox`:**
- Maintains aspect ratio at any screen size
- Responsive by default (no fixed dimensions)
- Scales perfectly on high-DPI displays
- Mobile-optimized without media queries

#### SVG Accessibility (2025):
```html
<!-- ✅ RIGHT - Accessible SVG -->
<svg
  role="img"
  aria-label="Territory Map showing 5 zones of AI learning journey"
  aria-describedby="map-caption"
>
  <title id="map-caption">Territory Map with 5 zones from AI confusion to confidence</title>
  <!-- Content -->
</svg>

<!-- ❌ WRONG - No accessibility info -->
<svg>
  <!-- Content -->
</svg>
```

**Accessibility Requirements:**
- `role="img"`: Identifies SVG as image
- `aria-label`: Short description for screen readers
- `<title>`: Detailed description (optional)
- `tabindex="0"`: Makes interactive elements focusable

#### CSS Custom Properties (Design Tokens):
```css
/* ✅ RIGHT - Use design tokens */
.zone-title {
  color: var(--ocean-mint-primary);
  font-family: 'Space Grotesk', sans-serif;
}

/* ❌ WRONG - Hardcoded values */
.zone-title {
  color: #20B2AA;
  font-family: 'Space Grotesk', sans-serif;
}
```

**Benefits of Design Tokens:**
- Consistent colors across components
- Easy theme updates (change in one place)
- Follows Story 1.1 token system
- Maintainable codebase

#### Responsive Typography (2025):
```css
/* ✅ RIGHT - Fluid typography with clamp() */
.map-title {
  font-size: clamp(1.5rem, 4vw, 2.5rem);
}

/* ❌ WRONG - Fixed font size */
.map-title {
  font-size: 2.5rem;
}
```

**How `clamp()` Works:**
- Minimum: `1.5rem` (small screens)
- Preferred: `4vw` (scales with viewport)
- Maximum: `2.5rem` (large screens)
- No media queries needed

#### Focus Indicators for Accessibility:
```css
/* ✅ RIGHT - Visible focus outline */
.zone:focus {
  outline: 2px solid var(--ocean-mint-primary);
  outline-offset: 4px;
}

/* ❌ WRONG - No focus state */
.zone:focus {
  /* Nothing - keyboard users can't see focus */
}
```

**Focus Best Practices:**
- Always provide `:focus` state
- Use `outline` (not `box-shadow`) for better browser support
- `outline-offset` creates space between element and outline
- Match focus color to brand (ocean mint)

#### SVG Animation Preparation (Future-Ready):
```css
/* Prepare zones for GSAP animation (Story 2.2, 2.3) */
.zone {
  will-change: transform, opacity; /* Only when animating */
  transform: translate3d(0, 0, 0); /* Force GPU layer */
}
```

**Note:** Don't add `will-change` yet - Story 2.3 will add it dynamically during animations to avoid memory leaks.

### Project Context Reference

**Project Name:** k2m-edtech-program-
**Epic:** Epic 2: Territory Map WHOA Moment
**Story:** 2.1 - Create Territory Map SVG Structure
**Target Audience:** Kenyan students interested in AI education

**Epic 2 Goals (From Epics.md):**
- Visitors witness stunning particle coalescence (200 desktop, 50 mobile)
- Particles transform from chaos to order, revealing the Territory Map
- Users discover their current zone on the learning journey
- Create "WHOA moment" - unforgettable visual metaphor for transformation

**User Value (From Epics.md):**
> "Users experience a 'revelation moment' as they understand their current position (Zone 0-4) and see the path to Zone 4. The particle system creates an unforgettable visual metaphor for transformation."

**Performance Goals (From Epics NFR1, NFR2):**
- Desktop: 60fps consistent
- Mobile: 45fps+ acceptable
- Lighthouse Performance: 90+
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s

**Accessibility (From Epics NFR8):**
- WCAG AA compliance required
- Text contrast: 4.5:1 (normal text), 3:1 (large text)
- Semantic HTML required
- Screen reader accessible
- Keyboard navigation required

**Browser Support (From Epics NFR6, NFR7):**
- Chrome, Safari, Firefox, Edge (desktop)
- iOS Safari (iPhone 12+)
- Android Chrome (Samsung Galaxy S21+)

**Design Philosophy (From Animation Strategy):**
> "Act II: The Map Awakening (25-60% scroll)
> Emotional Beat: Revelation - 'Oh, THIS is where I am'

> The 'WHOA' Moment:
> - Screen goes pitch black for 0.5s
> - 200 particles COALESCE from chaos
> - Particles spiral inward using GSAP motionPath
> - Particles form the Territory Map shape
> - Each zone (0→1→2→3→4) illuminates with ocean mint glow
> - Zone 4 gets warm ocean mint highlight
> - Magnetic Hover: Zones subtly follow cursor movement"

**Zone Copy Content (From Epics.md, Lines 627-632):**
- **Zone 0:** "AI isn't for me" - "Where most students start. Feeling overwhelmed."
- **Zone 1:** "I could try this" - "First sparks of curiosity."
- **Zone 2:** "AI does tasks for me" - "Using it for real work. But inconsistent."
- **Zone 3:** "AI understands my intent" - "True collaboration begins."
- **Zone 4:** "I control the quality" - "You direct. You refine. You own the outcome. This is where confidence lives."

**Next Stories After This One:**
1. Story 2.2: Build Particle Coalescence System (adds animated particles)
2. Story 2.3: Implement Zone Illumination and Magnetic Hovers (adds interactions)
3. Epic 3: Discord Preview & Community
4. Epic 4: Graceful Degradation & Post-Launch

**Critical Success Factors for This Story:**
1. Map structure is semantic and accessible
2. All 5 zones are visually distinct
3. Zone 4 stands out with ocean mint accent
4. Layout is responsive across devices
5. Copy matches epic requirements exactly
6. Foundation is ready for particle system (Story 2.2)

**Technical Preparation (Done in Previous Stories):**
- Story 1.1: Design tokens (colors, typography) ✅
- Story 1.2: GSAP + Lenis infrastructure ✅
- Story 1.3: Hero HTML structure + CSS ✅
- Story 1.4: Hero animations ✅
- This Story: Create static Territory Map structure
- Next Story (2.2): Add particle coalescence animation

**Technical Dependencies:**
- Story 1.1 MUST be completed (design tokens, Vite, Tailwind)
- Story 1.2 MUST be completed (GSAP, ScrollTrigger, Lenis)
- Story 1.3 SHOULD be completed (Hero section context)
- Story 1.4 SHOULD be completed (animation patterns)

**Integration Points:**
- Hero section (Story 1.3) scrolls into Territory Map
- GSAP infrastructure (Story 1.2) will power particle animations
- Design tokens (Story 1.1) define ocean mint accent colors
- Performance utilities (Story 1.2) will optimize particle system

## Dev Agent Record

### Agent Model Used

_Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)_

### Debug Log References

No debugging issues encountered during story creation.

### Completion Notes List

**Story 2.1 Creation Complete** ✅

Comprehensive story file generated with ultimate context engine analysis:

1. **Story Foundation** ✅
   - User story: "As a visitor, I want to see the Territory Map with 5 distinct zones"
   - Acceptance criteria: 4 BDD-formatted scenarios covering structure, content, interactivity, and visuals
   - Epic context: Second story in Epic 2 (Territory Map WHOA Moment)

2. **Developer Context** ✅
   - Epic objectives: "WHOA moment" with particle coalescence animation
   - Business value: Revelation moment - users identify their current position
   - Technical requirements: Inline SVG, semantic HTML, accessible zones
   - Success criteria: Map structure ready for particle system (Story 2.2)

3. **Technical Requirements** ✅
   - File structure: `/src/components/TerritoryMap/` following Hero component pattern
   - HTML structure: Inline SVG with 5 zone groups, particle container
   - CSS styling: Ocean mint accent on Zone 4, responsive design
   - Integration: Import pattern compatible with Vite and ES6 modules

4. **Architecture Compliance** ✅
   - Component-based architecture (self-contained Territory Map)
   - Design tokens from Story 1.1 (ocean mint colors, typography)
   - Semantic HTML (section, SVG with ARIA, proper heading structure)
   - Accessibility requirements (WCAG AA, keyboard navigation, screen reader)

5. **Library/Framework Requirements** ✅
   - GSAP + ScrollTrigger (Story 1.2) - Foundation for future animations
   - Lenis smooth scroll (Story 1.2) - Active globally
   - Performance utilities (Story 1.2) - `isMobile()` for particle optimization
   - No new dependencies for this story (just HTML/CSS structure)

6. **File Structure Requirements** ✅
   - TerritoryMap.html: Map HTML structure with inline SVG
   - Map.css: Map-specific styles with ocean mint accents
   - Component directory: `/src/components/TerritoryMap/`
   - Integration: Import in main.js or index.html after Hero section

7. **Testing Requirements** ✅
   - Manual testing: 7 categories (structure, visual, responsive, accessibility, browser, performance, integration)
   - Automated testing: Playwright visual regression, Lighthouse CI, Pa11y
   - Accessibility: WCAG AA compliance, keyboard navigation, screen reader
   - Performance: SVG inline (no HTTP request), Lighthouse 90+

8. **Previous Story Intelligence** ✅
   - Story 1.1: Design tokens (ocean mint colors, Space Grotesk + Inter typography)
   - Story 1.2: GSAP + Lenis infrastructure, performance utilities
   - Story 1.3: Hero component structure, HTML/CSS patterns to follow
   - Story 1.4: Animation patterns (GPU acceleration, Safari compatibility)

9. **Latest Tech Information** ✅
   - Inline SVG best practices (viewBox for responsiveness)
   - SVG accessibility (role="img", aria-label, tabindex)
   - CSS custom properties (design tokens for maintainability)
   - Responsive typography (clamp() for fluid font sizes)
   - Focus indicators (visible outline for keyboard navigation)

10. **Project Context Reference** ✅
    - Epic 2 goals: WHOA moment with particle coalescence
    - User value: Revelation - "Oh, THIS is where I am"
    - Zone copy: All 5 zones with titles and descriptions
    - Design philosophy: "Disruption with emotional safety"
    - Performance targets: 60fps desktop, 45fps mobile

**Ready for Development Status:** ✅
- All acceptance criteria clearly defined
- File structure specified
- Code examples provided (HTML, CSS)
- Integration points documented
- Testing checklist comprehensive
- Developer guardrails in place

**Next Steps:**
1. Developer runs `dev-story` workflow to implement this story
2. Story 2.2 will add particle coalescence animation
3. Story 2.3 will add zone illumination and magnetic hovers
4. Epic 2 retrospective after all stories complete

**File Location:** `_bmad-output/implementation-artifacts/2-1-create-territory-map-svg-structure.md`
**Status:** ready-for-dev
**Comprehensive Analysis:** Complete - Developer has everything needed for flawless implementation

### File List

**Story File Created:**
- `_bmad-output/implementation-artifacts/2-1-create-territory-map-svg-structure.md` - Comprehensive story file

**Files to Create During Implementation:**
- `k2m-landing/src/components/TerritoryMap/TerritoryMap.html` - Map HTML structure (NEW)
- `k2m-landing/src/components/TerritoryMap/Map.css` - Map-specific styles (NEW)

**Files to Modify During Implementation:**
- `k2m-landing/src/main.js` - Import TerritoryMap component
- `k2m-landing/index.html` - Include TerritoryMap section

**Dependency Files (Already Created):**
- `k2m-landing/src/styles/token.css` - Design tokens (Story 1.1)
- `k2m-landing/src/utils/gsap-config.js` - GSAP + ScrollTrigger (Story 1.2)
- `k2m-landing/src/utils/performance-optimizations.js` - Performance utilities (Story 1.2)
- `k2m-landing/src/components/Hero/Hero.html` - Hero section (Story 1.3)
- `k2m-landing/src/components/Hero/Hero.css` - Hero styles (Story 1.3)

**Reference Documents:**
- `_bmad-output/planning-artifacts/epics.md` - Epic and story requirements
- `_bmad-output/k2m-awwwards-landing-page-implementation-plan.md` - Technical architecture
- `_bmad-output/k2m-landing-page-animation-strategy.md` - Animation strategy
- `_bmad-output/implementation-artifacts/sprint-status.yaml` - Sprint tracking
