---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories']
inputDocuments:
  - /_bmad-output/k2m-awwwards-landing-page-implementation-plan.md
  - /_bmad-output/k2m-landing-page-animation-strategy.md
  - /_bmad-output/k2m-landing-page-copy-final.md
---

# K2M EdTech Landing Page - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for K2M EdTech Awwwards-Level Landing Page, decomposing the requirements from the implementation plan, animation strategy, and copy documentation into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Landing page shall display a Hero section with animated text reveals using staggered animations
FR2: Landing page shall implement a 4-Act cinematic scroll experience (Hero → Map → Discord → CTA)
FR3: Landing page shall display an interactive Territory Map with particle coalescence animation (200 particles desktop, 50 mobile)
FR4: Landing page shall show particles transitioning from chaos to order in a spiral formation using GSAP motionPath
FR5: Landing page shall illuminate 5 zones (0-4) sequentially on the Territory Map
FR6: Landing page shall implement magnetic hover effects on map zones that follow cursor movement
FR7: Landing page shall display a Discord Preview section with animated chat bubbles
FR8: Landing page shall show emoji reactions (💡🔥❤️) with continuous pulse animation
FR9: Landing page shall display a CTA section with "Begin Your Journey" button linking to Typeform diagnostic
FR10: Landing page shall implement Lenis smooth scroll for luxurious scroll feel
FR11: Landing page shall use GSAP ScrollTrigger for all scroll-based animations
FR12: Landing page shall display all final copy content (326 words across 4 acts)
FR13: Landing page shall implement ocean mint (#20B2AA) glow effects on key phrases
FR14: Landing page shall render pure black (#000000) to soft black (#0A0A0A) gradient background
FR15: Landing page shall implement anticipatory pin effect before Territory Map reveal
FR16: Landing page shall support responsive design for desktop, tablet, and mobile devices
FR17: Landing page shall implement all typography using Space Grotesk (headings) and Inter (body) fonts

### NonFunctional Requirements

NFR1: Landing page must maintain 60fps performance on desktop devices
NFR2: Landing page must maintain 45fps+ performance on mobile devices
NFR3: Landing page must achieve Lighthouse Performance Score of 90 or higher
NFR4: Landing page must achieve First Contentful Paint in under 1.5 seconds
NFR5: Landing page must achieve Time to Interactive in under 3.5 seconds
NFR6: Landing page must work on Chrome, Safari, Firefox, and Edge browsers
NFR7: Landing page must work on iOS (iPhone 12+) and Android (Samsung Galaxy S21+) devices
NFR8: Landing page must follow WCAG AA accessibility standards
NFR9: Landing page must support prefers-reduced-motion for users with motion sensitivities
NFR10: Landing page must use GPU-accelerated properties (transform, opacity) for all animations
NFR11: Landing page must implement mobile-specific optimizations using matchMedia
NFR12: Landing page must handle image lazy loading for performance
NFR13: Landing page must implement code splitting for GSAP plugins

### Additional Requirements

AR1: Use Vite as build tool for fast development
AR2: Use Tailwind CSS for utility classes
AR3: Use GSAP Core v3.12+ with ScrollTrigger and MotionPath plugins
AR4: Use Lenis smooth scroll library with duration 1.2 for luxury feel
AR5: Implement color palette with pure black (#000000), soft black (#0A0A0A), ocean mint (#20B2AA, #40E0D0, #008B8B)
AR6: Create inline SVG Territory Map with zone groups
AR7: Design 200 particle positions for desktop, 50 for mobile
AR8: Integrate with Typeform for diagnostic form (no backend)
AR9: Implement basic conversion tracking (scroll depth, CTA clicks, diagnostic completion)
AR10: No Awwwards submission planned
AR21: Typeform diagnostic URL: https://k2m-edtech.typeform.com/diagnostic (CONFIRM WITH TREVOR)
AR22: Testimonials must use real cohort member names with permission (Sarah, Marcus, Amani are placeholders)
AR23: Implement Hotjar or Microsoft Clarity for heatmap tracking (free tier)
AR24: GSAP Club license required for commercial use ($199/year)
AR11: Use elastic.out(1, 0.5) easing for Discord chat bubbles
AR12: Use power2.inOut easing for particle coalescence
AR13: Implement anticipatoryPin: 1 for smooth scroll pinning
AR14: Use scrub: 1-2 for scroll-controlled animations
AR15: Handle browser URL bar viewport changes on mobile
AR16: Wrap ScrollTrigger in window.addEventListener("load") for image readiness
AR17: Implement document.hidden detection for pause/resume on tab switch
AR18: Create particle elements as 4px circles with radial gradient (2px on mobile)
AR19: Design Discord chat bubble graphics with emoji reactions
AR20: Implement CTA button with scale: 1.05 hover effect

### FR Coverage Map

FR1: Epic 1 - Hero text reveals
FR2: Epic 1 - 4-Act structure setup
FR3: Epic 2 - Territory Map with particles
FR4: Epic 2 - Chaos to order animation
FR5: Epic 2 - Zone illumination
FR6: Epic 2 - Magnetic hovers
FR7: Epic 3 - Discord chat bubbles
FR8: Epic 3 - Emoji animations
FR9: Epic 3 - CTA to Typeform
FR10: Epic 1 - Smooth scroll infrastructure
FR11: Epic 1 - GSAP ScrollTrigger setup
FR12: Epic 1 - All copy content
FR13: Epic 1 - Ocean mint effects
FR14: Epic 1 - Black gradient background
FR15: Epic 2 - Anticipatory pin
FR16: Epic 3 - Responsive design
FR17: Epic 1 - Typography

## Epic List

### Epic 0: Conversion Foundation & Success Metrics

Before building, define what success looks like. This epic establishes conversion baselines, analytics infrastructure, and validation protocols.

**FRs covered:** (Conversion-critical, not feature-based)

**User Value:** Ensures every pixel built serves the goal: diagnostic completion. Without this, we're building blind.

### Epic 1: Foundation & Hero Experience

Visitors experience smooth scroll with cinematic text reveals that validate their AI confusion and provide emotional relief through the "You're not alone" message.

**FRs covered:** FR1, FR2, FR10, FR11, FR12, FR13, FR14, FR17

**User Value:** Users feel seen, understood, and relieved as they discover their AI confusion is shared. The luxurious smooth scroll and animated text creates an immediate premium brand impression.

### Epic 2: Territory Map WHOA Moment (Zone 0-4 Implementation)

Visitors witness a stunning particle coalescence animation (200 particles desktop, 50 mobile) that transforms from chaos to order, revealing the Territory Map (Zones 0-4) and helping them discover their current zone on the learning journey.

**🎯 SCOPE DECISION:** Zones 0-4 implemented for V1. Zones 5-7 displayed as "Coming Soon" placeholders (greyed out/faded) to show future roadmap without overcommitting.

**FRs covered:** FR3, FR4, FR5, FR6, FR15

**Story Count:** 5 stories (2.0, 2.1, 2.2, 2.3, 2.4)

**User Value:** Users experience a complete emotional arc from confusion (Zone 0) → recognition (Zones 1-3) → breakthrough (Zone 4). The particle system creates an unforgettable visual metaphor for transformation, while zones 5-7 hint at future possibilities.

### Epic 3: Community Preview & Conversion

Visitors see social proof through animated Discord chat bubbles showing real community interactions, and can begin their journey by clicking "Begin Your Journey" to access the Typeform diagnostic.

**FRs covered:** FR7, FR8, FR9, FR16

**User Value:** Users feel belonging through community preview and feel safe taking the next step through the no-pressure diagnostic. Responsive design ensures the experience works on all devices.

### Epic 4: Graceful Degradation & Post-Launch

Ensure the page works on all devices, has fallbacks for when things fail, and can be iterated based on real data.

**FRs covered:** (Resilience and iteration)

**User Value:** Even on old phones or slow connections, users can still convert. After launch, we improve based on real data.

---

## Epic 0: Conversion Foundation & Success Metrics

Before building, define what success looks like. This epic establishes conversion baselines, analytics infrastructure, and validation protocols.

**FRs covered:** (Conversion-critical, not feature-based)

### Story 0.1: Define Conversion Baseline & Success Metrics

As the product owner,
I want clearly defined conversion metrics before development begins,
So that we can measure whether the page is actually converting, not just looking pretty.

**Acceptance Criteria:**

**Given** we are planning the landing page
**When** we define success metrics
**Then** the following conversion targets are documented:
  - **Primary Metric:** Diagnostic form click rate > 15% of visitors
  - **Secondary Metrics:**
    - Scroll depth to CTA section > 80%
    - Time on page > 90 seconds (enough to read all content)
    - Diagnostic completion rate > 70% of those who start
  - **Performance Metrics:**
    - Lighthouse Performance Score > 90
    - First Contentful Paint < 1.5s
    - 60fps desktop, 45fps+ mobile

**Given** we need to validate emotional impact
**When** we define qualitative success criteria
**Then** the following emotional responses are targeted:
  - Hero section: User reports feeling "seen" or "validated"
  - Territory Map: User can identify their current zone (0-4)
  - Discord section: User feels "belonging" or "community"
  - CTA section: User feels "relief" not "pressure"

**Given** we have success metrics defined
**When** the page launches
**Then** we can objectively determine if the page is converting

---

### Story 0.2: Implement Analytics & Heatmap Tracking

As a product owner,
I want analytics and heatmap tracking installed,
So that I can measure scroll depth, click patterns, and identify drop-off points.

**Acceptance Criteria:**

**Given** the page needs conversion tracking
**When** I implement analytics
**Then** Microsoft Clarity (free) or Hotjar (free tier) is installed
**And** scroll depth tracking is enabled (25%, 50%, 75%, 100%)
**And** click heatmaps are recording
**And** session recordings are enabled for qualitative analysis

**Given** the CTA button is critical
**When** I track CTA interactions
**Then** the following events are tracked:
  - `cta_button_visible`: When CTA enters viewport
  - `cta_button_hover`: When user hovers over button
  - `cta_button_click`: When user clicks button
  - `typeform_opened`: When Typeform loads (if embedded)

**Given** the Territory Map is the WHOA moment
**When** I track map engagement
**Then** the following events are tracked:
  - `map_entered_viewport`: When map section becomes visible
  - `map_zone_hover`: Which zones users hover over
  - `map_time_spent`: Duration user spends in map section

**Given** we need to respect privacy
**When** I configure analytics
**Then** no PII is collected
**And** GDPR/cookie consent is implemented if required
**And** analytics script is loaded asynchronously (non-blocking)

---

### Story 0.3: Establish User Testing Protocol

As a product owner,
I want a user testing protocol defined,
So that we validate emotional response with real users, not just technical metrics.

**Acceptance Criteria:**

**Given** we need to validate the page works emotionally
**When** we define the testing protocol
**Then** the following is documented:
  - **Test Group:** 5 users from target demographic (Kenyan students interested in AI)
  - **Test Method:** Screen share + think-aloud protocol
  - **Test Tasks:**
    1. Scroll through entire page naturally
    2. Identify which zone (0-4) they feel they're in
    3. Describe what K2M offers in one sentence
    4. Rate emotional response (1-5) for each section
    5. Click CTA (even if not completing diagnostic)

**Given** we need specific validation questions
**When** we test each section
**Then** we ask:
  - **Hero:** "How does this opening make you feel?" (Target: relief, seen, understood)
  - **Map:** "Which zone do you think you're in? Why?" (Target: clear identification)
  - **Discord:** "Would you want to join this community?" (Target: yes, belonging)
  - **CTA:** "Does this feel like pressure or an invitation?" (Target: invitation)

**Given** testing reveals issues
**When** 3+ users report the same friction
**Then** that section is flagged for revision before launch

**Given** we have limited time
**When** we schedule testing
**Then** testing occurs after Epic 1 (Hero) and after Epic 3 (full page)
**And** 2-3 hours are allocated for each testing round
**And** findings are documented in a testing report

---

## Epic 1: Foundation & Hero Experience

Visitors experience smooth scroll with cinematic text reveals that validate their AI confusion and provide emotional relief through the "You're not alone" message.

**FRs covered:** FR1, FR2, FR10, FR11, FR12, FR13, FR14, FR17

### Story 1.1: Initialize Project with Design Tokens

As a developer,
I want to initialize a Vite project with Tailwind CSS and configure the design token system,
So that I have a solid foundation with the pure black and ocean mint color palette.

**Acceptance Criteria:**

**Given** I have Node.js installed locally
**When** I run `npm init vite@latest k2m-landing -- --template vanilla`
**Then** a new Vite project is created successfully
**And** Tailwind CSS is installed and configured
**And** PostCSS and Autoprefixer are set up

**Given** the project is initialized
**When** I create `/src/styles/token.css`
**Then** all color variables are defined:
  - `--pure-black: #000000`
  - `--soft-black: #0A0A0A`
  - `--charcoal: #1A1A1A`
  - `--ocean-mint-primary: #20B2AA`
  - `--ocean-mint-glow: #40E0D0`
  - `--ocean-mint-dim: #008B8B`
  - `--text-primary: #FFFFFF`
  - `--text-secondary: #B0B0B0`
  - `--text-muted: #6A6A6A`
**And** Tailwind config extends with custom colors

**Given** I need typography
**When** I configure Google Fonts
**Then** Space Grotesk (weights 400, 600, 700) is loaded
**And** Inter (weights 400, 600) is loaded
**And** `font-display: swap` is set for performance
**And** fonts are applied to Tailwind config

**Given** the development server is running
**When** I open localhost:5173
**Then** the page loads without errors
**And** the background is pure black (#000000)
**And** the build completes successfully

---

### Story 1.2: Configure GSAP + Lenis Infrastructure

As a developer,
I want to install and configure GSAP with ScrollTrigger and Lenis smooth scroll,
So that I have the animation foundation ready for scroll-based interactions.

**Acceptance Criteria:**

**Given** the Vite project is set up
**When** I install GSAP packages
**Then** `gsap` version 3.12+ is installed
**And** `ScrollTrigger` plugin is installed
**And** all plugins are registered correctly

**Given** GSAP is installed
**When** I create `/src/utils/gsap-config.js`
**Then** global defaults are set:
  - `ease: "power2.out"`
  - `duration: 0.8`
**And** ScrollTrigger config includes:
  - `ignoreMobileResize: true`
  - `autoRefreshEvents: "visibilitychange,DOMContentLoaded,load"`
**And** GSAP and ScrollTrigger are exported for use

**Given** smooth scroll is needed
**When** I create `/src/utils/lenis-config.js`
**Then** Lenis is configured with:
  - `duration: 1.2`
  - `smooth: true`
  - `direction: "vertical"`
**And** Lenis integrates with GSAP ticker
**And** Lenis updates ScrollTrigger on scroll
**And** the smooth scroll feels luxurious, not sluggish

**Given** performance monitoring is needed
**When** I create `/src/utils/performance-optimizations.js`
**Then** `enableGPU()` helper function exists
**And** `disableGPU()` helper function exists
**And** `isMobile()` detection function exists
**And** `monitorPerformance()` FPS counter is implemented

**Given** all infrastructure is configured
**When** I import and initialize in main.js
**Then** Lenis smooth scroll is active
**And** ScrollTrigger is ready to use
**And** no console errors appear
**And** the page scrolls smoothly

**Given** Safari has known GSAP/Lenis conflicts
**When** I test on Safari (macOS and iOS)
**Then** Lenis smooth scroll works without jitter
**And** ScrollTrigger animations fire at correct scroll positions
**And** no "snap back" behavior occurs on iOS Safari
**And** document.hidden detection pauses/resumes animations correctly on tab switch

**Given** tab visibility affects animations
**When** user switches browser tabs
**Then** GSAP timeline pauses when `document.hidden` is true
**And** timeline resumes when tab becomes visible again
**And** no animation desync occurs after tab switch

---

### Story 1.3: Build Hero Section Structure

As a visitor,
I want to see the Hero section with all copy content on a pure black background,
So that I can read the message and understand what K2M offers.

**Acceptance Criteria:**

**Given** the GSAP infrastructure is ready
**When** I create `/src/components/Hero/Hero.html`
**Then** the Hero section exists with all content:
  - Headline: "Using AI but don't feel in control?"
  - Subheadline: "You're not alone."
  - Body paragraphs (38 words total)
  - Ocean mint key phrases (per copy doc):
    - "in control?" in headline gets ocean mint glow
    - "Here's what nobody tells you:" gets ocean mint glow
**And** the HTML structure follows semantic markup
**And** text elements have class names for animation targeting

**Given** the Hero HTML exists
**When** I create `/src/components/Hero/Hero.css`
**Then** the Hero section has:
  - `position: relative`
  - `min-height: 100vh`
  - `display: flex` with centered content
  - `padding: 2rem` on all sides
  - `z-index: 1` for content layer
**And** the background is pure black (#000000)
**And** text colors use CSS variables (white, secondary, muted)

**Given** I need the gradient background
**When** I add the `.gradient-layer` div
**Then** it has `position: absolute` covering the full Hero
**And** the gradient is `linear-gradient(180deg, #000000 0%, #0A0A0A 100%)`
**And** it has `z-index: 0` behind content
**And** opacity is 1 by default

**Given** typography needs to be applied
**When** I style text elements
**Then** H1 uses Space Grotesk 700
**And** H1 font size is `clamp(2.5rem, 8vw, 5rem)`
**And** body text uses Inter 400
**And** line height for body is 1.6 for readability
**And** paragraph spacing is 1.5em for breathing room

**Given** the Hero section is built
**When** I view the page in a browser
**Then** all copy is readable on pure black background
**And** text contrast meets WCAG AA standards
**And** the section takes full viewport height
**And** no horizontal scrolling occurs on mobile

---

### Story 1.4: Implement Hero Text Reveal Animations

As a visitor,
I want to see text reveal animations with staggered timing as I scroll,
So that I feel the content is being revealed cinematically, creating an emotional connection.

**Acceptance Criteria:**

**Given** the Hero section structure exists
**When** I create `/src/components/Hero/Hero.js`
**Then** a `initHeroAnimations()` function is defined
**And** GSAP timeline is created with ScrollTrigger
**And** ScrollTrigger config includes:
  - `trigger: ".hero"`
  - `start: "top top"`
  - `end: "bottom top"`
  - `scrub: 1`

**Given** I need text reveal animations
**When** I animate the headline
**Then** each text span animates with:
  - `y: 50` starting position
  - `opacity: 0` starting state
  - `stagger: 0.2` between elements
  - `duration: 1`
  - `ease: "power3.out"`
**And** ScrollTrigger starts at `"top 80%"`
**And** text moves up into view smoothly

**Given** ocean mint phrases need glow
**When** I animate the key phrase
**Then** the text shadow animates:
  - From: `0 0 50px rgba(32, 178, 170, 0)`
  - To: `0 0 30px rgba(32, 178, 170, 0.8)`
  - Duration: 1.5s
**And** the glow appears when text enters viewport
**And** the glow is subtle, not overwhelming

**Given** I need text depth effects (parallax layers)
**When** I implement living typography
**Then** text is split into 3 layers with parallax:
  - Layer 1 (Shadow): `opacity: 0.3, filter: blur(4px), z-index: 1`
  - Layer 2 (Blur): `opacity: 0.6, filter: blur(1px), z-index: 2`
  - Layer 3 (Sharp): `opacity: 1, filter: blur(0px), z-index: 3`
**And** each layer moves at different scroll speeds:
  - Layer 1 (Shadow): `y: -30` (slowest, background layer)
  - Layer 2 (Blur): `y: -15` (medium)
  - Layer 3 (Sharp): `y: 0` (fastest, foreground)
**And** the parallax creates 3D terrain depth effect
**And** text breathes with `scrub: 2` for frame-by-frame control

**Given** performance optimization is required
**When** I apply animations
**Then** only GPU-accelerated properties are animated (transform, opacity)
**And** `will-change: transform, opacity` is applied during animation
**And** `will-change: auto` is set after animation completes
**And** no layout-triggering properties (width, height, top, left) are animated

**Given** the animations are implemented
**When** I scroll through the Hero section
**Then** text reveals smoothly with stagger
**And** ocean mint glow appears on key phrase
**And** animations feel cinematic, not rushed
**And** the scroll is smooth with Lenis

---

### Story 1.5: Optimize Hero Performance

As a developer,
I want to optimize Hero animations for 60fps desktop and 45fps mobile performance,
So that the landing page meets Lighthouse 90+ score and provides smooth experience.

**Acceptance Criteria:**

**Given** Hero animations are working
**When** I implement mobile-specific optimizations
**Then** ScrollTrigger `matchMedia()` is used
**And** mobile breakpoint is `(max-width: 768px)`
**And** desktop breakpoint is `(min-width: 769px)`
**And** mobile animations use reduced particle count (future-proofing)
**And** mobile animations have shorter durations (0.5s vs 1s)

**Given** performance monitoring is needed
**When** I run `monitorPerformance()` from Hero.js
**Then** FPS counter displays in console
**And** warning appears if FPS drops below 30
**And** performance is logged every second

**Given** I need to validate performance
**When** I run Lighthouse audit
**Then** Performance score is 90 or higher
**And** First Contentful Paint is under 1.5s
**And** Time to Interactive is under 3.5s
**And** no layout shift warnings appear

**Given** the page loads
**When** I test on desktop browser
**Then** animations maintain 60fps consistently
**And** no jank or stutter occurs
**And** scroll feels smooth with Lenis

**Given** I test on mobile device
**When** I view on iPhone or Android
**Then** animations maintain 45fps or higher
**And** particle system doesn't lag the device
**And** touch scrolling works smoothly
**And** mobile URL bar viewport changes are handled

**Given** images will be added later
**When** I prepare for image lazy loading
**Then** `window.addEventListener("load")` wrapper is in place
**And** ScrollTrigger waits for all images before calculating
**And** fallback is ready if images fail to load

---

## Epic 2: Territory Map WHOA Moment

Visitors witness a stunning particle coalescence animation (200 particles desktop, 50 mobile) that transforms from chaos to order, revealing the Territory Map and helping them discover their current zone on the learning journey.

**FRs covered:** FR3, FR4, FR5, FR6, FR15

### Story 2.0: Build Pre-Map Anticipation Framing

As a visitor,
I want to feel anticipation building as I scroll toward the Territory Map,
So that I experience emotional buildup that makes the WHOA moment feel earned.

**Acceptance Criteria:**

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

---

### Story 2.1: Create Territory Map SVG Structure

As a visitor,
I want to see the Territory Map with 5 distinct zones (0-4),
So that I can understand the learning journey and identify my current position.

**Acceptance Criteria:**

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

---

### Story 2.2: Build Particle Coalescence System

As a visitor,
I want to see 200 particles (desktop) or 50 particles (mobile) coalesce from chaos into the Territory Map shape,
So that I experience a stunning "WHOA moment" that represents transformation.

**Acceptance Criteria:**

**Given** the Territory Map HTML exists
**When** I create `/src/components/TerritoryMap/MapParticles.js`
**Then** a `MapParticleSystem` class is defined
**And** the class accepts a container element
**And** `particleCount` is set based on `isMobile()`:
  - Desktop: 200 particles
  - Mobile: 50 particles
**And** particles are created as div elements with class `.map-particle`

**Given** particles need to be styled
**When** I create `/src/components/TerritoryMap/Map.css`
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
  - `trigger: ".map-formation"`
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
  - Particles have random x/y positions (-500 to 500px)
**And** Phase 2 (Coalesce):
  - Particles animate to `opacity: 1`, `scale: 1`
  - Particles move to `x: 0`, `y: 0` (map positions)
  - Duration is 2s
  - Stagger is `amount: 1.5, from: "random"`
  - Ease is `"power2.inOut"` for gentle motion
**And** the spiral motion path is visible

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

**Experiential Acceptance Criteria:**
**Given** 5 users test this section
**When** the particles coalesce
**Then** 4/5 users should express surprise, wonder, or say "whoa"

---

### Story 2.3: Implement Zone Illumination and Magnetic Hovers

As a visitor,
I want to see zones illuminate sequentially and react to my cursor with magnetic hover effects,
So that I can interact with the map and explore each zone.

**Acceptance Criteria:**

**Given** the particle system is working
**When** I add zone illumination to the timeline
**Then** zones animate in sequence after particle formation
**And** each zone animates with:
  - `from: { opacity: 0, scale: 0.8 }`
  - `duration: 1`
  - `stagger: 0.3` between zones
  - `ease: "back.out(1.7)"` for elastic feel
**And** Zone 4 illuminates with warm ocean mint (#40E0D0)
**And** zones illuminate in order: 0 → 1 → 2 → 3 → 4

**Given** zones need to be interactive
**When** I implement `initZoneHovers()` function
**Then** each zone has mousemove event listener
**And** on mousemove, the zone follows the cursor:
  - Calculate x/y offset from center
  - Move zone by `x / 5`, `y / 5` pixels
  - Scale zone to 1.05
  - Duration: 0.5s
  - Ease: `"power2.out"`
**And** on mouseleave, the zone returns to original position:
  - x: 0, y: 0, scale: 1
  - Duration: 0.5s
  - Smooth transition

**Given** users need guidance on their current zone
**When** I add zone tooltips
**Then** zones 0 and 1 display tooltips on hover:
  - Zone 0 tooltip: "You might be here"
  - Zone 1 tooltip: "You might be here"
  - Tooltips use ocean mint accent (#20B2AA)
  - Tooltips fade in with `opacity: 0 → 1` over 0.3s
  - Tooltips position near the zone with `position: absolute`
**And** zones 2, 3, 4 do not display tooltips (users rarely start there)
**And** tooltips help users identify their starting point
**And** tooltips create personalization and connection

**Given** the anticipatory pin is needed
**When** I configure the ScrollTrigger pin
**Then** `anticipatePin: 1` is set
**And** the background gradually dims before the reveal:
  - From: soft black (#0A0A0A)
  - To: pure black (#000000)
  - Gradual darkness based on scroll progress
**And** the transition feels smooth, not abrupt

**Given** all effects are implemented
**When** I interact with the map
**Then** zones illuminate one by one in sequence
**And** hovering over a zone makes it follow my cursor
**And** the magnetic effect is subtle, not aggressive
**And** Zone 4 stands out with ocean mint glow
**And** the WHOA moment (black screen → particles → zones) feels earned
**And** all animations maintain 60fps desktop / 45fps mobile

---

### Story 2.4: Add Zone 5-7 "Coming Soon" Placeholder

As a visitor,
I want to see that the learning journey continues beyond Zone 4,
So that I understand this is a comprehensive program, not just a one-time course.

**Acceptance Criteria:**

**Given** Zones 0-4 are fully implemented
**When** I add Zone 5-7 placeholders to the Territory Map
**Then** zones 5, 6, 7 are visually distinct from zones 0-4:
  - Zones 5-7 have reduced opacity (0.3-0.4)
  - Zones 5-7 have grayscale styling (no ocean mint color)
  - Zones 5-7 have visual "coming soon" indicator
  - Zones 5-7 are non-interactive (no hover effects, no tooltips)
**And** the visual hierarchy is clear: Zones 0-4 = implemented, Zones 5-7 = future roadmap

**Given** I need to indicate "coming soon" status
**When** I style Zone 5-7 placeholders
**Then** each placeholder zone has:
  - Desaturated color scheme (grayscale or muted tones)
  - "Coming Soon" badge or label near the zone
  - Subtle dashed outline instead of solid border
  - Opacity reduced to 40-50%
  - `pointer-events: none` to disable interaction
**And** users understand these zones are not yet available

**Given** users need context about future zones
**When** I add placeholder zone text
**Then** zones 5-7 display teaser text:
  - Zone 5: "Builder" with "Architect your AI systems (Coming Soon)"
  - Zone 6: "Architect" with "Design thinking with AI (Coming Soon)"
  - Zone 7: "Philosopher" with "Shape the future of AI (Coming Soon)"
**Or** a simplified approach: "Future zones coming soon" label
**And** the language hints at expanded value without overpromising

**Given** the map structure exists
**When** I update TerritoryMap.html
**Then** zones 5-7 are added to the SVG with:
  - `class="zone-placeholder"` for targeting
  - `data-zone="5"`, `data-zone="6"`, `data-zone="7"` attributes
  - Reduced visual prominence compared to zones 0-4
  - Clear visual distinction (grayscale, opacity, dashed borders)
**And** the layout accommodates all 7 zones without crowding

**Given** responsive design is required
**When** I view on mobile devices
**Then** zones 5-7 are:
  - Visible but de-emphasized on mobile (same opacity/grayscale treatment)
  - stacked or positioned to avoid clutter
  - Not interactive (no touch events)
  - Clearly labeled as "coming soon"
**And** mobile users understand zones 5-7 are future content

**Given** accessibility is important
**When** screen readers encounter zones 5-7
**Then** `aria-label` indicates "coming soon" status:
  - "Zone 5: Builder. Coming soon."
  - "Zone 6: Architect. Coming soon."
  - "Zone 7: Philosopher. Coming soon."
**And** zones 5-7 have `tabindex="-1"` to prevent keyboard focus
**And** screen reader users understand these zones are not yet interactive

**Given** future implementation is planned
**When** zones 5-7 are eventually activated
**Then** the placeholder styling can be easily removed:
  - Change `class="zone-placeholder"` to `class="zone"`
  - Remove grayscale/opacity CSS
  - Add interactive hover effects
  - Add tooltips and animations
**And** the transition from placeholder to active is smooth

**Experiential Acceptance Criteria:**
**Given** 5 users view the Territory Map
**When** asked "What do zones 5-7 represent?"
**Then** 5/5 users should understand these are "coming soon" or "future content"
**And** no users should attempt to interact with zones 5-7

---

## Epic 3: Community Preview & Conversion

Visitors see social proof through animated Discord chat bubbles showing real community interactions, and can begin their journey by clicking "Begin Your Journey" to access the Typeform diagnostic.

**FRs covered:** FR7, FR8, FR9, FR16

### Story 3.1: Build Discord Preview Section

As a visitor,
I want to see animated Discord chat bubbles with emoji reactions,
So that I feel the community is alive and active.

**Acceptance Criteria:**

**Given** the Territory Map is complete
**When** I create `/src/components/DiscordPreview/Discord.html`
**Then** a Discord preview section exists with:
  - Section headline: "This isn't a course. It's a cohort."
  - Three chat bubbles with user testimonials:
    - Sarah, Cluster 3: "I just tried explaining my situation first" 💡
    - Marcus, Cluster 1: "AI actually understood what I meant!" 🔥
    - Amani, Cluster 5: "I've never felt this confident before" ❤️
  - Community promise text (63 words)
**And** chat bubbles are structured as distinct elements
**And** each bubble has author name and quote

**Given** testimonials must be authentic
**When** the page launches
**Then** testimonial names are either:
  - Real cohort members who gave written permission, OR
  - Clearly marked as "Future cohort preview" with disclaimer
**And** if using real names, K2M has documented consent on file
**And** if names are fictional, a small disclaimer appears: "Preview of what community conversations look like"
**Note:** Sarah, Marcus, Amani are PLACEHOLDERS - replace with real testimonials before launch

**Given** I need Discord styling
**When** I create `/src/components/DiscordPreview/Discord.css`
**Then** chat bubbles have Discord-like appearance:
  - Rounded corners
  - Subtle borders
  - Background color slightly lighter than pure black
  - Padding for readability
**And** emojis are styled with appropriate size
**And** the section is responsive on mobile

**Given** the section structure exists
**When** I view the page
**Then** all three chat bubbles are visible
**And** author names are distinct from quotes
**And** emojis render correctly (💡🔥❤️)
**And** the community promise text is readable
**And** the layout works on mobile devices

---

### Story 3.2: Animate Chat Bubbles and Emojis

As a visitor,
I want to see chat bubbles animate in with elastic motion and emojis pulse continuously,
So that the community feels alive and dynamic.

**Acceptance Criteria:**

**Given** the Discord HTML structure exists
**When** I create `/src/components/DiscordPreview/Discord.js`
**Then** a `initDiscordAnimations()` function is defined
**And** GSAP targets all `.chat-bubble` elements

**Given** I need elastic bubble animations
**When** I animate chat bubbles appearing
**Then** each bubble animates with:
  - `from: { y: 100, opacity: 0, rotation: 5 }`
  - `to: { y: 0, opacity: 1, rotation: 0 }`
  - `duration: 1`
  - `stagger: { amount: 2, from: "random" }`
  - `ease: "elastic.out(1, 0.5)"` for bouncy feel
**And** ScrollTrigger config:
  - `trigger: ".discord-preview"`
  - `start: "top 70%"`
  - `end: "bottom bottom"`
  - `scrub: 1`
**And** bubbles drift in from bottom, not just appear

**Given** emojis need to pulse
**When** I animate emoji reactions
**Then** each `.emoji-reaction` animates continuously:
  - `scale: 1.2` at peak
  - `duration: 0.8`
  - `yoyo: true` (pulses back and forth)
  - `repeat: -1` (infinite loop)
  - `ease: "power1.inOut"`
  - `stagger: { amount: 1, from: "random" }`
**And** different emojis pulse at different times
**And** the pulse is subtle, not distracting

**Given** all animations are implemented
**When** I scroll to the Discord section
**Then** chat bubbles animate in with elastic motion
**And** emojis pulse continuously
**And** the animation feels organic and alive
**And** performance maintains 60fps desktop / 45fps mobile

---

### Story 3.3: Create CTA Section with Typeform Integration

As a visitor,
I want to see the "Begin Your Journey" button that takes me to the Typeform diagnostic,
So that I can start my journey with K2M.

**Acceptance Criteria:**

**Given** the Discord preview is complete
**When** I create `/src/components/CTA/CallToAction.html`
**Then** a CTA section exists with:
  - Headline: "Let's find your starting point."
  - Subheadline: "15 minutes. No pressure. Just clarity."
  - CTA button: "Begin Your Journey"
  - Micro-copy explaining the process (74 words)
  - Diagnostic positioning: "Not a test. No right answers. This diagnostic IS our first session."
  - Footer with logistics values
**And** all copy matches the final document
**And** the section has generous white space

**Given** I need CTA styling
**When** I create `/src/components/CTA/CTA.css`
**Then** the CTA button has:
  - Ocean mint background (#20B2AA)
  - White text
  - Padding for clickability
  - Rounded corners
  - Hover transition
**And** the section has pure black background
**And** text is centered and readable
**And** white space creates relief

**Given** the button needs to link to Typeform
**When** I add the button href
**Then** the button links to the Typeform diagnostic URL
**And** the Typeform URL is: `https://k2m-edtech.typeform.com/diagnostic`
  - **ACTION REQUIRED:** Trevor must confirm this URL or provide correct one
  - If URL not confirmed by development start, use placeholder that shows error message
**And** the link opens in the same tab (not new tab - reduces friction)
**And** no backend integration is needed (direct link)
**And** Typeform is NOT embedded (avoids mobile keyboard/viewport issues)

**Given** the diagnostic claim must be accurate
**When** CTA says "15 minutes"
**Then** the actual Typeform diagnostic has been tested to take 12-18 minutes
**And** if diagnostic takes longer than 20 minutes, CTA copy is updated
**Note:** Test diagnostic with 3 users before launch to validate timing

**Given** the footer must display logistics
**When** I create the footer section
**Then** the footer displays:
  - Cohort Size: 200 students
  - Start Date: February 14, 2026
  - Duration: 6 weeks
  - Investment: 3,500 KES
**And** all logistics values are prominent, not optional
**And** the footer uses muted text color (--text-muted)
**And** the footer is separated from main CTA with white space

**Given** visitors need a way to ask questions
**When** I add the contact section
**Then** the footer includes: "Questions? Just ask. We're real people."
**And** a contact method is provided (email or WhatsApp link)
**And** contact link uses ocean mint accent for visibility
**And** this builds trust by showing K2M is accessible

**Given** the diagnostic must be positioned correctly
**When** I add diagnostic value proposition text
**Then** the following text appears before the button:
  - "Not a test. No right answers."
  - "This diagnostic IS our first session."
  - "How we meet you where you are—not where we assume you should be."
**And** the positioning emphasizes safety, not evaluation
**And** users understand this is a conversation, not an assessment

**Given** the competitive positioning must be clear
**When** I frame the diagnostic approach
**Then** the positioning differentiates from competitors:
  - Competitors sell: Fear of missing out (FOMO) with urgency tactics
  - K2M sells: Relief of being found with psychological safety
  - This is "less marketing, more therapy session"
  - The diagnostic filters for readiness, not just anyone with money
  - No obligation after diagnostic - user decides if cohort is right for them
**And** the positioning feels generous, not desperate
**And** users feel K2M values fit over conversion
**And** this creates trust and differentiation in the market

**Given** the CTA section exists
**When** I view the page
**Then** the CTA section is the final section
**And** the button stands out visually
**And** all copy is readable
**And** the section feels calm and clear
**And** the layout is responsive on mobile

---

### Story 3.4: Implement CTA Animations and Responsive Design

As a visitor,
I want to see smooth scroll animations on the CTA and have the page work perfectly on all devices,
So that I have a polished experience regardless of how I access the page.

**Acceptance Criteria:**

**Given** the CTA HTML exists
**When** I create `/src/components/CTA/CTA.js`
**Then** a `initCTAAnimations()` function is defined
**And** the CTA section fades in on scroll

**Given** I need CTA section reveal
**When** I animate the CTA section appearing
**Then** the section animates with:
  - `from: { opacity: 0, y: 50 }`
  - `to: { opacity: 1, y: 0 }`
  - `duration: 1.5`
  - `ease: "power3.out"`
**And** ScrollTrigger starts at `"top 80%"`

**Given** the button needs hover effects
**When** I add button interaction
**Then** on `mouseenter`:
  - `scale: 1.05`
  - `boxShadow: "0 0 30px rgba(32, 178, 170, 0.5)"`
  - `duration: 0.3`
  - `ease: "power2.out"`
**And** on `mouseleave`:
  - `scale: 1`
  - `boxShadow: "0 0 0px rgba(32, 178, 170, 0)"`
  - `duration: 0.3`

**Given** responsive design is required
**When** I test on multiple devices
**Then** the page works on:
  - Desktop (1920×1080, 2560×1440)
  - Tablet (iPad Air, Pro)
  - Mobile (iPhone 12+, Samsung Galaxy S21+)
**And** all animations work on mobile
**And** touch interactions work smoothly
**And** no horizontal scrolling occurs
**And** text is readable without zooming

**Given** accessibility is required
**When** I test with screen reader
**Then** all content is accessible via keyboard
**And** all images have alt text
**And** color contrast meets WCAG AA

**Given** users may have motion sensitivities
**When** `prefers-reduced-motion: reduce` is detected
**Then** all GSAP animations are disabled or simplified:
  - Particle coalescence: instant fade-in instead of spiral
  - Text reveals: instant appear instead of stagger
  - Chat bubbles: static display instead of elastic animation
  - Emoji pulse: disabled entirely
  - Lenis smooth scroll: disabled (use native scroll)
**And** the page remains fully functional without animations
**And** all content is still visible and readable

**Given** the page is complete
**When** I run final Lighthouse audit
**Then** Performance score is 90+
**And** Accessibility score is 95+
**And** Best Practices score is 90+
**And** SEO score is 90+
**And** the page is ready for launch

**Experiential Acceptance Criteria:**
**Given** 5 users complete the full scroll experience
**When** asked "Would you click the button?"
**Then** 4/5 users should say yes or express intent to try the diagnostic

---

## Epic 4: Graceful Degradation & Post-Launch

Ensure the page works on all devices, has fallbacks for when things fail, and can be iterated based on real data.

**FRs covered:** (Resilience and iteration)

**User Value:** Even on old phones or slow connections, users can still convert. After launch, we improve based on real data.

### Story 4.1: Implement Graceful Degradation Fallbacks

As a visitor on a low-end device,
I want the page to still work even if fancy animations fail,
So that I can still learn about K2M and start my journey.

**Acceptance Criteria:**

**Given** JavaScript fails to load or errors
**When** the page renders without JS
**Then** all content is visible (HTML/CSS only)
**And** the CTA button still links to Typeform
**And** the page is usable (just not animated)

**Given** the particle system causes performance issues
**When** FPS drops below 30 for 2+ seconds
**Then** a simpler fallback animation triggers:
  - Particles fade in as a static image/SVG
  - Map zones appear with simple CSS transitions
  - No spiral motion path (too expensive)
**And** the WHOA moment is preserved (just simpler)

**Given** Lenis smooth scroll conflicts with device
**When** scroll jank is detected or iOS Safari issues occur
**Then** Lenis is disabled
**And** native browser scroll takes over
**And** ScrollTrigger still works with native scroll

**Given** images fail to load
**When** Territory Map SVG or assets don't load
**Then** alt text describes the content
**And** a fallback message appears: "Imagine your journey from confusion to confidence"
**And** the page doesn't break visually

**Given** Typeform is unreachable
**When** user clicks CTA but Typeform fails
**Then** a fallback message appears with contact email
**And** user can still reach K2M (just not via form)

---

### Story 4.2: Add SEO & Meta Tags

As a search engine,
I want proper meta tags and structured data,
So that K2M ranks for relevant searches and social shares look good.

**Acceptance Criteria:**

**Given** the page needs SEO
**When** I add meta tags
**Then** the following are implemented:
  - `<title>`: "K2M EdTech - From AI Confusion to Confidence in 6 Weeks"
  - `<meta name="description">`: "Join 200 students learning to think with AI. Not prompts that expire, but habits that last. Start with a free 15-minute diagnostic."
  - `<meta name="keywords">`: "AI education, Kenya, students, AI learning, prompt engineering"

**Given** social sharing is important
**When** I add Open Graph tags
**Then** the following are implemented:
  - `og:title`: "K2M EdTech - From AI Confusion to Confidence"
  - `og:description`: "Join 200 students learning to think with AI."
  - `og:image`: Social share image (1200x630px) showing Territory Map
  - `og:url`: Landing page URL
  - `twitter:card`: "summary_large_image"

**Given** structured data helps search engines
**When** I add JSON-LD
**Then** Course schema is implemented with:
  - Course name, description, provider
  - Price (3,500 KES), currency
  - Start date (February 14, 2026)
  - Duration (6 weeks)

---

### Story 4.3: Post-Launch Iteration Framework

As a product owner,
I want a clear process for improving the page after launch,
So that we can optimize based on real user data, not guesses.

**Acceptance Criteria:**

**Given** the page is live
**When** we review analytics weekly
**Then** the following metrics are tracked:
  - Scroll depth by section (where do users drop off?)
  - CTA click rate (is it above 15%?)
  - Time on page (are users reading?)
  - Heatmap hotspots (what are users clicking?)

**Given** a section underperforms
**When** scroll depth drops significantly at a section
**Then** that section is flagged for A/B testing
**And** a variant is created within 1 week
**And** the variant is tested for 2 weeks minimum

**Given** the CTA underperforms
**When** CTA click rate is below 10%
**Then** the following are tested:
  - Button text variants ("Begin Your Journey" vs "Find Your Starting Point")
  - Button position (earlier in scroll?)
  - Price visibility (hide vs show in footer)

**Given** user feedback is collected
**When** diagnostic completers are surveyed
**Then** we ask: "What almost stopped you from clicking?"
**And** insights inform V2 improvements

**Note:** This story defines the PROCESS, not specific changes. Changes come from data.

