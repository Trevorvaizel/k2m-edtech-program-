# The Scroll Choreography Bible

**Date:** 2026-01-17
**Research Compiled By:** Dr. Quinn (Problem Solver) + Trevor
**Purpose:** Meta-reasoning and implementation patterns for Awwwards-level scroll storytelling

---

## Executive Summary

This document captures the **meta-reasoning** behind award-winning scroll animations - the WHY behind the choreography, not just the HOW. Use this as a reference when implementing Territory Map scroll storytelling or any future scroll-driven narratives.

**Key Discovery:** GSAP is now 100% FREE (all plugins) since Webflow acquisition in 2024.

---

## Part 1: The Meta-Reasoning

### Why Choreography Works

The human brain is **wired to notice movement** - it's a survival trait. In web design, we hijack this instinct to:
- **Spotlight** key information
- **Direct** user focus
- **Create** emotional resonance
- **Pace** information absorption

> *"Reading a story no longer needs to be passive. Users become active participants through interaction."* - Webflow

**Critical Insight:** Scroll-triggered animation isn't decoration - it's **communication**.

### The Psychology of Scroll

| Psychological Mechanism | How It Works | Design Application |
|------------------------|--------------|-------------------|
| **Attention Guidance** | Brains track movement automatically | Use motion to direct focus |
| **Cognitive Pacing** | Information overload causes fatigue | Reveal content progressively |
| **Ownership Effect** | Users value what they control | Scrub animations = user controls pace |
| **Anticipation/Reward** | Dopamine release on expected payoff | Build tension, deliver "wow moments" |
| **Spatial Memory** | Position encodes meaning | Parallax creates conceptual hierarchy |

### Performance Impact (Research Data)

- **80% higher engagement** with scroll-triggered vs static content
- **47% longer time on site** with interactive scrolling
- **30-40% higher conversion** with scroll storytelling
- **50 milliseconds** - time users take to form first impression

---

## Part 2: Disney's 12 Principles → UX Choreography

Disney animators developed these principles in the 1930s for emotional engagement. They translate directly to UI:

### Principle 1: ANTICIPATION
**Animation:** Prepare the viewer for what's about to happen
**UI Application:** Hover states, pre-motion cues, visual hints

```javascript
// Example: Button hover anticipates click action
gsap.to(".button", {
  scale: 1.05,
  duration: 0.2,
  ease: "power2.out"
});
```

**Territory Map Use:** Zone 3 "leans toward" Zone 4 before arrival - subtle rotation, glow intensification

### Principle 2: FOLLOW-THROUGH & OVERLAPPING ACTION
**Animation:** Not everything stops at once; parts settle at different times
**UI Application:** Elements overshoot then settle, staggered stops

```javascript
// Particles overshoot target then settle
gsap.to(".particle", {
  x: targetX,
  y: targetY,
  ease: "elastic.out(1, 0.5)", // Overshoot and settle
  duration: 1.2
});
```

**Territory Map Use:** Particles spiral past zone centers, then drift back to settle

### Principle 3: TIMING
**Animation:** Duration determines emotional weight
**UI Application:** 200-600ms for most interactions

| Animation Type | Duration | Rationale |
|---------------|----------|-----------|
| Hover/Feedback | 200-300ms | Quick acknowledgment |
| Reveals/Fades | 400-600ms | Noticeable but not slow |
| Transitions | 500-800ms | Cinematic, meaningful |
| Hero sequences | 1000-1500ms | Dramatic, impactful |

**Critical:** Too fast = missed; Too slow = frustrating

### Principle 4: STAGING
**Animation:** Direct attention to ONE thing at a time
**UI Application:** Sequential reveals, not simultaneous

```
WRONG: All 5 zones animate at once → compete for attention → confusion
RIGHT: Zone 0 first → Zone 1 follows → Zone 2 → etc. → clear hierarchy
```

**The Staging Hierarchy:**
```
1. PRIMARY ELEMENT moves first (initiator)
2. SECONDARY ELEMENTS follow with slight delay (0.1-0.2s)
3. TERTIARY ELEMENTS complete the composition (0.2-0.4s)
```

### Principle 5: OVERLAPPING ACTION (Related Elements)
**Animation:** Related elements move at different rates
**UI Application:** Image first, then title, then description

```javascript
// Staggered reveal of zone content
gsap.from(".zone", {
  y: 30,
  opacity: 0,
  stagger: {
    each: 0.15,
    from: "start" // Sequential from first to last
  }
});
```

---

## Part 3: The Six Core Scroll Patterns

### Pattern 1: PARALLAX LAYERS

**What:** Elements move at different speeds creating depth illusion
**Psychology:** Creates spatial relationships between concepts
**Best For:** Background atmosphere, depth perception, visual hierarchy

```javascript
// Using ScrollSmoother data attributes
<div data-speed="0.3">Background layer (slow)</div>
<div data-speed="1.0">Content layer (normal)</div>
<div data-speed="1.5">Foreground accent (fast)</div>

// Or programmatically with ScrollTrigger
gsap.to(".background", {
  y: -100,
  scrollTrigger: {
    scrub: true,
    start: "top bottom",
    end: "bottom top"
  }
});
```

**Territory Map Application:**
- SVG background path moves slower than zone cards
- Particles move at varied speeds during coalescence

---

### Pattern 2: PROGRESSIVE REVEALS

**What:** Content fades/slides in as user scrolls past threshold
**Psychology:** Paces information absorption, creates reading rhythm
**Best For:** Text content, section entries, feature showcases

```javascript
gsap.from(".zone", {
  y: 30,
  opacity: 0,
  duration: 1.5,
  ease: "power2.out",
  scrollTrigger: {
    trigger: ".zone",
    start: "top 80%", // Trigger when element reaches 80% down viewport
    toggleActions: "play none none reverse"
  }
});
```

**Trigger Point Guidelines:**
- `top 90%` - Early reveal, subtle
- `top 80%` - Standard reveal timing
- `top 70%` - Later reveal, more deliberate
- `top 50%` - Dramatic, user must scroll to it

**Territory Map Application:**
- Zone cards reveal progressively as user approaches
- Text within zones staggers word-by-word

---

### Pattern 3: SCRUB (Scroll-Bound Animation)

**What:** Animation progress syncs directly to scroll position
**Psychology:** User CONTROLS the pace - creates ownership and engagement
**Best For:** Transformations, progress indicators, cinematic sequences

```javascript
gsap.to(".element", {
  x: 500,
  rotation: 360,
  scrollTrigger: {
    trigger: ".container",
    start: "top center",
    end: "bottom center",
    scrub: 2  // 2 second smoothing delay
  }
});
```

**Scrub Values:**
| Value | Feel | Use Case |
|-------|------|----------|
| `scrub: true` | 1:1 instant | Direct manipulation feel |
| `scrub: 0.5` | Quick, snappy | Energetic sections |
| `scrub: 1` | Smooth | Standard cinematic |
| `scrub: 2` | Luxurious, cinematic | Premium experiences |
| `scrub: 3+` | Very smooth, laggy | Dreamy, atmospheric |

**Territory Map Application:**
- Particle coalescence scrub: 2 for cinematic feel
- Zone opacity/blur transitions scrub: 1

---

### Pattern 4: PINNING

**What:** Section locks in place while internal timeline progresses
**Psychology:** Forces focus on key content, controls narrative pacing
**Best For:** Key transformation moments, "WHOA" reveals, hero sections

```javascript
gsap.timeline({
  scrollTrigger: {
    trigger: ".territory-map",
    start: "top top",
    end: "+=200%", // Pin for 2x viewport height of scroll
    pin: true,
    anticipatePin: 1, // Smooth entry into pin state
    scrub: 1
  }
})
.to(".particles", { opacity: 1, scale: 1 })
.to(".zones", { opacity: 1 }, "-=0.5");
```

**anticipatePin Values:**
- `anticipatePin: 0` - No anticipation (can feel jarring)
- `anticipatePin: 1` - Standard smooth entry (recommended)
- `anticipatePin: 2` - Extra smooth for long pins

**Territory Map Application:**
- Pin Territory Map section during particle coalescence
- User scrolls to control particle animation while section stays fixed

---

### Pattern 5: STAGGERED TEXT REVEALS

**What:** Characters/words/lines animate sequentially
**Psychology:** Creates reading rhythm, guides eye movement, builds anticipation
**Best For:** Headlines, key messages, dramatic reveals

```javascript
// Split text into animatable units
const split = new SplitText(".headline", {
  type: "chars, words, lines",
  charsClass: "char",
  wordsClass: "word",
  linesClass: "line"
});

// Character-by-character reveal
gsap.from(split.chars, {
  y: 100,
  opacity: 0,
  duration: 0.8,
  stagger: 0.03,  // 30ms between each character
  ease: "power2.out",
  scrollTrigger: {
    trigger: ".headline",
    start: "top 70%"
  }
});

// Word-by-word reveal (more readable)
gsap.from(split.words, {
  y: 50,
  opacity: 0,
  duration: 0.6,
  stagger: 0.08,
  ease: "power3.out"
});

// Line-by-line reveal (paragraphs)
gsap.from(split.lines, {
  y: 30,
  opacity: 0,
  duration: 0.5,
  stagger: 0.15,
  ease: "power2.out"
});
```

**Stagger Values:**
| Effect | Stagger | Feel |
|--------|---------|------|
| Rapid cascade | 0.02-0.03s | Energetic, typewriter |
| Quick reveal | 0.05-0.08s | Snappy, modern |
| Rhythmic flow | 0.10-0.15s | Readable, deliberate |
| Dramatic sequence | 0.20-0.30s | Weighty, important |

**Stagger "from" Options:**
```javascript
stagger: {
  each: 0.05,
  from: "start"   // Left to right
  // from: "end"     // Right to left
  // from: "center"  // Explode outward
  // from: "edges"   // Close inward
  // from: "random"  // Organic, chaotic
}
```

**Territory Map Application:**
- Zone titles: word-by-word reveal with `from: "start"`
- Zone 4 "I control the quality": character reveal for emphasis

---

### Pattern 6: HORIZONTAL SCROLLING

**What:** Content moves sideways instead of down
**Psychology:** Breaks expectations, signals temporal progression, gallery feel
**Best For:** Timelines, journeys, portfolio showcases

```javascript
const sections = gsap.utils.toArray(".panel");

gsap.to(sections, {
  xPercent: -100 * (sections.length - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".container",
    pin: true,
    scrub: 1,
    snap: 1 / (sections.length - 1), // Snap to each panel
    end: () => "+=" + document.querySelector(".container").offsetWidth
  }
});
```

**Territory Map Application:**
- Could be used for Zone 0 → Zone 4 as horizontal journey
- Alternative to vertical scroll for territory progression

---

## Part 4: Easing Psychology

Easing defines the CHARACTER of motion - how it accelerates and decelerates.

### Easing Reference

| Ease | Feel | Use For |
|------|------|---------|
| `"none"` / `"linear"` | Mechanical, robotic | Progress bars, scrub sync |
| `"power1.out"` | Gentle stop | Subtle reveals |
| `"power2.out"` | Natural, settling | Most reveals (default choice) |
| `"power3.out"` | Snappy entrance | Bold statements, hero text |
| `"power4.out"` | Very snappy | Dramatic entrances |
| `"power2.inOut"` | Smooth journey | Scrub animations, transitions |
| `"elastic.out"` | Bouncy, playful | Delightful moments, success states |
| `"back.out"` | Overshoot & settle | Attention-grabbing |
| `"bounce.out"` | Bouncy landing | Playful, cartoonish |

### Easing Combos for Narrative

```javascript
// ARRIVAL: Dramatic entrance → gentle settle
gsap.from(".hero", { y: 100, ease: "power3.out" });

// DEPARTURE: Gentle start → quick exit
gsap.to(".element", { y: -50, ease: "power2.in" });

// TRANSFORMATION: Smooth throughout
gsap.to(".morph", { scale: 1.5, ease: "power2.inOut" });

// CELEBRATION: Playful bounce
gsap.from(".success", { scale: 0, ease: "elastic.out(1, 0.5)" });
```

---

## Part 5: Narrative Arc Through Scroll

### The Emotional Journey Structure

```
ACT 1: HOOK (0-20% scroll)
├── Intrigue with initial motion
├── Establish visual language
├── Create curiosity ("what happens if I scroll?")
└── First micro-reward for scrolling

ACT 2: BUILD (20-70% scroll)
├── Progressive complexity
├── VARY animation vocabulary (different patterns!)
├── Maintain rhythm with breathing room
├── Strategic "wow moments" as scroll rewards
└── Build toward climax

ACT 3: CLIMAX (70-85% scroll)
├── Most dramatic animation
├── Payoff for the journey
├── The "WHOA moment"
└── Peak emotional engagement

ACT 4: RESOLUTION (85-100% scroll)
├── Settle and clarify
├── Clear call to action
├── Sense of completion
└── Invitation to act
```

### The Breathing Room Principle

> *"Animations provide a nice break from text, signaling new content blocks and preventing fatigue."*

**Not every scroll position needs animation.** Strategic pauses create rhythm.

```
[Animation] → [Rest] → [Animation] → [Rest] → [BIG Animation] → [Rest]
```

---

## Part 6: Territory Map Choreography Translation

### Current State (What Was Built)
- Same `y: 30, opacity: 0` pattern repeated everywhere
- No variation in animation vocabulary
- No emotional choreography
- Static zone positioning with CSS-only opacity/blur

### Target State (The Vision)

| Zone Transition | Emotional Beat | Animation Pattern | Specific Technique |
|----------------|----------------|-------------------|-------------------|
| **Entry → Zone 0** | "Where am I?" (confusion) | Emergence from void | Particles from `opacity: 0, scale: 0`, blur: 4px → 2px |
| **Zone 0 → 1** | "Maybe..." (first hope) | Upward drift, brightening | `y: 20 → 0`, blur: 2px → 1.5px, stagger from: "random" |
| **Zone 1 → 2** | "Getting it" (recognition) | Structure forming | Snap into place, stagger from: "center", blur: 1.5px → 1px |
| **Zone 2 → 3** | "Almost there" (anticipation) | Magnetic pull | Subtle rotation toward Zone 4, glow intensifies, blur: 1px → 0.5px |
| **Zone 3 → 4** | **"WHOA!"** (revelation) | ARRIVAL | Scale pulse, radial glow explosion, particles settle, blur: 0, full opacity |

### Implementation Specifications

**Particle Coalescence (Story 2.2):**
```javascript
// Phase 1: Chaos
gsap.set('.map-particle', {
  opacity: 0,
  scale: 0,
  x: () => Math.random() * 1000 - 500,
  y: () => Math.random() * 1000 - 500
});

// Phase 2: Coalesce with spiral
gsap.to('.map-particle', {
  opacity: 1,
  scale: 1,
  x: (i, target) => target.targetX,
  y: (i, target) => target.targetY,
  duration: 2,
  stagger: { amount: 1.5, from: "random" },
  ease: "power2.inOut",
  scrollTrigger: {
    trigger: ".territory-map",
    start: "top center",
    end: "center center",
    scrub: 2,
    anticipatePin: 1
  }
});
```

**Zone Text Reveals:**
```javascript
// Split zone titles
const zoneTitles = gsap.utils.toArray(".zone h3");
zoneTitles.forEach((title, i) => {
  const split = new SplitText(title, { type: "words" });

  gsap.from(split.words, {
    y: 30,
    opacity: 0,
    duration: 0.6,
    stagger: 0.08,
    ease: "power2.out",
    scrollTrigger: {
      trigger: title,
      start: "top 75%"
    }
  });
});
```

**Zone 4 Arrival (The WHOA Moment):**
```javascript
const zone4Timeline = gsap.timeline({
  scrollTrigger: {
    trigger: ".zone-4",
    start: "top 60%",
    toggleActions: "play none none reverse"
  }
});

zone4Timeline
  .from(".zone-4", {
    scale: 0.8,
    opacity: 0,
    duration: 0.8,
    ease: "power3.out"
  })
  .to(".zone-4-glow", {
    scale: 1.5,
    opacity: 0.8,
    duration: 1,
    ease: "power2.out"
  }, "-=0.4")
  .from(".zone-4 h3", {
    y: 20,
    opacity: 0,
    duration: 0.6,
    ease: "power2.out"
  }, "-=0.6");
```

---

## Part 7: The Golden Rules

### Rule 1: PURPOSE-DRIVEN MOTION
> *"Don't animate just to animate. Use motion to highlight information, draw focus, or evoke emotion."*

**Every animation must answer:** What does this COMMUNICATE?

### Rule 2: STAGING OVER SIMULTANEITY
Never let elements compete for attention. Choreograph hierarchy:
- ONE focal point at a time
- Supporting elements follow, don't lead
- Use stagger to create visual priority

### Rule 3: VARY THE VOCABULARY
**WRONG:** Same fade-in pattern for every section
**RIGHT:** Different techniques for different emotional beats
- Reveals for content entry
- Scrub for transformations
- Pin for key moments
- Parallax for atmosphere

### Rule 4: USER CONTROL = ENGAGEMENT
Scrub animations give users ownership of pace. They become **participants, not spectators.**

### Rule 5: QUALITY > QUANTITY
One perfectly choreographed animation beats ten mediocre ones.
**Poor timing destroys trust instantly.**

### Rule 6: RESPECT THE BREATHING ROOM
Not every scroll position needs animation.
Strategic pauses create rhythm and prevent fatigue.

### Rule 7: TEST ON REAL DEVICES
Chrome DevTools throttling doesn't capture real device feel.
Test on actual phones and tablets.

---

## Part 8: GSAP Plugin Reference (All Free!)

### Available Plugins (Post-Webflow Acquisition)

| Plugin | Purpose | Key Use Case |
|--------|---------|--------------|
| **ScrollTrigger** | Scroll-linked animations | Everything scroll-related |
| **ScrollSmoother** | Smooth scrolling + parallax | Silky scroll, data-speed parallax |
| **SplitText** | Text splitting for animation | Character/word/line reveals |
| **MotionPath** | Curved motion paths | Spiral particle movement |
| **DrawSVG** | SVG stroke animation | Path drawing effects |
| **MorphSVG** | Shape morphing | Zone shape transformations |
| **ScrambleText** | Text scramble effects | Glitch/decode reveals |
| **Flip** | Layout transition animations | Smooth reflows |
| **Draggable** | Drag interactions | Interactive elements |
| **Inertia** | Momentum physics | Natural drag feel |

### Installation
```bash
npm install gsap
```

```javascript
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ScrollSmoother } from "gsap/ScrollSmoother";
import { SplitText } from "gsap/SplitText";

gsap.registerPlugin(ScrollTrigger, ScrollSmoother, SplitText);
```

---

## Part 9: Reference Resources

### Official GSAP Resources
- [ScrollTrigger Docs](https://gsap.com/docs/v3/Plugins/ScrollTrigger/)
- [ScrollTrigger Showcase (CodePen)](https://codepen.io/collection/DkvGzg)
- [GSAP Scroll Collection (CodePen)](https://codepen.io/collection/bNPYOw)
- [GSAP Learning Center](https://gsap.com/resources/)

### Inspiration & Patterns
- [Awwwards GSAP Sites](https://www.awwwards.com/websites/gsap/)
- [Made With GSAP](https://madewithgsap.com/)
- [FreeFrontend SplitText Examples](https://freefrontend.com/split-text-js/)

### Educational Articles
- [Scroll Like a Pro - DEV.to](https://dev.to/okoye_ndidiamaka_5e3b7d30/scroll-like-a-pro-how-scroll-triggered-animations-turn-websites-into-interactive-stories-bp2)
- [Webflow Scrollytelling Guide](https://webflow.com/blog/scrollytelling-guide)
- [Disney's 12 Principles for UI - Dribbble](https://dribbble.com/stories/2020/07/27/disney-principles-of-animation-ui-interactions)
- [UX Choreography Principles - freeCodeCamp](https://www.freecodecamp.org/news/the-principles-of-ux-choreography-69c91c2cbc2a/)
- [Halo Lab Scroll Animations](https://www.halo-lab.com/blog/scroll-animations-for-your-website)

---

## Appendix: Quick Reference Cheat Sheet

### ScrollTrigger Defaults
```javascript
scrollTrigger: {
  trigger: ".element",      // What element triggers
  start: "top 80%",         // When to start (element top at 80% viewport)
  end: "bottom 20%",        // When to end
  scrub: 1,                 // Smooth scrub (1 second)
  pin: false,               // Don't pin by default
  anticipatePin: 1,         // Smooth pin entry
  markers: true,            // Debug markers (remove in production)
  toggleActions: "play none none reverse"
}
```

### Common toggleActions
- `"play none none none"` - Play once, never reverse
- `"play none none reverse"` - Play on enter, reverse on leave
- `"play pause resume reverse"` - Full control
- `"restart none none reverse"` - Restart each time

### Stagger Presets
```javascript
// Quick cascade
stagger: { each: 0.03, from: "start" }

// Center explosion
stagger: { each: 0.05, from: "center" }

// Random organic
stagger: { amount: 1.5, from: "random" }

// Grid pattern
stagger: { each: 0.1, grid: [rows, cols], from: "center" }
```

---

*Generated by BMAD Creative Intelligence Suite - Problem Solving Workflow*
*Research compiled: 2026-01-17*
