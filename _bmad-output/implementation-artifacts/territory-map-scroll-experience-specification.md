# Territory Map Scroll Experience - Technical Specification

**Project**: K2M EdTech Program - AI Proficiency Territory Map
**Date**: 2026-01-17
**Version**: 1.0
**Status**: Design Complete, Ready for Implementation
**Created by**: BMAD Party Mode (Dr. Quinn, Sophia, Sally, Caravaggio, Winston, Victor)

---

## Executive Summary

This specification defines a **seven-zone technique palette** scroll experience that creates the perceptual transformation Trevor experienced when recognizing himself on the Territory Map. The experience uses **zone-specific choreographic signatures** to make users FEEL each zone's psychology rather than just read about it.

**Core Innovation**: Each of the 7 zones has its own animation technique, scrub value, and text treatment—creating emotional differentiation through technical variation.

**Business Objective**: Transform "you're behind" anxiety into "you're on YOUR journey" clarity, driving conversion through the recognition moment.

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Seven-Zone Technique Palette Overview](#seven-zone-technique-palette-overview)
3. [Detailed Zone Specifications](#detailed-zone-specifications)
4. [Technical Architecture](#technical-architecture)
5. [Implementation Roadmap](#implementation-roadmap)
6. [GSAP Code Examples](#gsap-code-examples)
7. [Performance & Mobile Considerations](#performance--mobile-considerations)
8. [Success Metrics](#success-metrics)

---

## Design Philosophy

### Core Principle: Technique IS Teaching

From the GSAP Emotional Choreography Research: *"Motion must support narrative, not compete with it."*

**Application**: The animation technique for each zone isn't just visual—it VALIDATES the user's experience in that zone.

- **Zone 2 (Delegator)** uses snap transitions → Users FEEL the transactional nature
- **Zone 3 (Collaborator)** uses fluid morphing → Users FEEL the conversational flow
- **Zone 4 (Director)** uses mirror pause → Users FEEL the contemplative refinement

### The Recognition-First Approach

**Traditional (Wrong)**: Learn → Remember → Apply
**Territory Map (Right)**: RECOGNIZE yourself → See pathways → Choose transformation

The scroll experience creates Trevor's breakthrough moment: *"Seeing myself through these stages and knowing that I could transform into others is what made me turn."*

### Narrative Structure

```
Wilderness (0-15%)    → Curiosity: "Where am I?"
Mirror Emerges (15-40%) → Understanding: "Oh, these zones exist"
Recognition (40-65%)   → Breakthrough: "That's ME!"
Branching (65-80%)      → Possibility: "I have choices"
Systems View (80-100%)  → Agency: "I can move"
```

---

## Seven-Zone Technique Palette Overview

| Zone | Name | Scroll Range | Scrub Value | Animation Technique | Emotional Beat |
|------|------|--------------|-------------|---------------------|----------------|
| **0-1** | Unaware → Observer | 0-15% | 0.3 (fast) | Particle Drift + Heavy Blur | Mystery → Curiosity |
| **2** | Delegator | 15-30% | 0.5 (snappy) | Snap Transitions | Transactional efficiency |
| **3** | Collaborator | 30-45% | 1.5 (conversational) | Fluid Morphing | Dialogue and flow |
| **4** | Director | 45-60% | 2.0 + pin (contemplative) | Mirror Pause + Hold | The breakthrough moment |
| **5** | Builder | 60-75% | 1.0 + trigger | Spatial Explosion | Choice revealed |
| **6** | Architect | 75-90% | 2.0 (breathing) | System Connections | Whole systems view |
| **7** | Philosopher | 90-100% | 2.0 (meta) | Philosophical Fade | Contemplation |

---

## Detailed Zone Specifications

### Zone 0-1: The Wilderness (Unaware → Observer)

**Scroll Range**: 0-15%
**Scrub Value**: 0.3 (fast, light)
**Duration**: 0.4-0.6s per animation

**Narrative Context**:
- Users start in fog: "AI feels like magic other people do"
- Gradual recognition: "Oh, this is a real thing I could engage with"
- Emotional arc: Confusion → Curiosity → Recognition

**Animation Technique**: Particle Drift + Parallax Layers

```javascript
// Particle system - aimless drift
gsap.to(".particle", {
  x: "random(-50, 50)",
  y: "random(-30, 30)",
  opacity: "random(0.2, 0.6)",
  duration: "random(3, 6)",
  repeat: -1,
  yoyo: true,
  ease: "sine.inOut"
});

// Parallax layers - 3-depth system
ScrollTrigger.create({
  trigger: ".wilderness-section",
  start: "top top",
  end: "bottom top",
  scrub: 0.3,
  onUpdate: (self) => {
    gsap.to(".layer-back", { y: self.progress * 30 });
    gsap.to(".layer-mid", { y: self.progress * 60 });
    gsap.to(".layer-front", { y: self.progress * 100 });
  }
});
```

**Text Treatment**:
- Blur: 12px → 4px → 0px (progressive sharpening)
- Stagger: 0.12s per word (slow, mysterious)
- Easing: `power2.inOut` (gentle)
- Font: Light, slightly expanded tracking

**Inner Monologue Text**:
> *"AI is... somewhere else. Something other people do."*
> *"Magic. Science fiction. Not my world."*
> *"Wait... could this be for me?"*

**Mobile Fallback**: Reduce particle count by 50%, use opacity instead of blur

---

### Zone 2: The Delegator

**Scroll Range**: 15-30%
**Scrub Value**: 0.5 (snappy, responsive)
**Duration**: 0.2-0.4s per animation

**Narrative Context**:
- "I use AI, but it's a vending machine"
- Input → Output transaction
- Frustration when output isn't perfect
- Inner monologue: "This AI is stupid" (blames the tool)

**Animation Technique**: Snap Transitions

```javascript
// Hard in, hard out - transactional feel
gsap.from(".delegator-element", {
  opacity: 0,
  scale: 0.8,
  y: 20,
  duration: 0.2,
  ease: "power2.out", // Snappy
  stagger: 0.05
});

// Input → Output animation
gsap.timeline({ repeat: -1 })
  .to(".input-box", { scale: 1.05, duration: 0.2 })
  .to(".input-box", { scale: 1.0, duration: 0.2 });
```

**Text Treatment**:
- Blur: 0px (sharp)
- Stagger: 0.03s per word (fast, efficient)
- Easing: `power2.out` (snappy)
- Font: Regular, condensed tracking
- Color: High contrast, almost harsh

**Zone Card Content**:
```markdown
## THE DELEGATOR
*"AI is my vending machine."*

You use AI for quick tasks:
- Summarize this report
- Draft that email
- Give me 10 ideas

You copy the output. If it's wrong, the AI failed.

**Inner monologue**: "Why doesn't it understand what I really want?"
```

**Recognition Trigger**: "Does this feel familiar? The frustration when AI 'doesn't get it'?"

---

### Zone 3: The Collaborator

**Scroll Range**: 30-45%
**Scrub Value**: 1.5 (conversational, flowing)
**Duration**: 0.8-1.2s per animation

**Narrative Context**:
- "AI is my thinking partner"
- Rich context, multi-turn conversations
- Uses AI for brainstorming, not just output
- Sees AI as dialogue, not command

**Animation Technique**: Fluid Morphing

```javascript
// Elements respond to each other
gsap.to(".collab-elements", {
  morphSVG: ".connected-shape",
  duration: 1.5,
  ease: "elastic.out(1, 0.5)", // Bouncy, alive
  stagger: 0.1
});

// Conversation flow animation
gsap.from(".message-bubble", {
  scale: 0,
  opacity: 0,
  transformOrigin: "bottom left",
  duration: 0.6,
  ease: "back.out(1.2)",
  stagger: {
    each: 0.2,
    from: "center"
  }
});
```

**Text Treatment**:
- Blur: 0px (sharp)
- Stagger: 0.08s per word (conversational rhythm)
- Easing: `power2.out` (friendly)
- Font: Regular, balanced tracking
- Color: Warm, approachable

**Zone Card Content**:
```markdown
## THE COLLABORATOR
*"AI is my thinking partner."*

You've discovered the secret:
- You provide rich context first
- You have multi-turn conversations
- You use AI for brainstorming, stress-testing ideas
- You see AI as dialogue, not command

**Inner monologue**: "How can I refine this to get exactly what I need?"
```

**Recognition Trigger**: "Do you find yourself having conversations with AI, not just giving commands?"

---

### Zone 4: The Director (BREAKTHROUGH MOMENT)

**Scroll Range**: 45-60%
**Scrub Value**: 2.0 + pin (very slow, contemplative)
**Duration**: 1.5-2.0s per animation + hold

**Narrative Context**:
- "AI is creative raw material"
- Sees AI as clay to sculpt
- Iterates deliberately, tests variables
- **KEY INSIGHT**: "I'm not correcting AI, I'm clarifying my own thinking"
- This is the MIRROR moment

**Animation Technique**: Mirror Pause + Hold

```javascript
// PIN this section - force the user to dwell here
ScrollTrigger.create({
  trigger: ".director-section",
  start: "top center",
  end: "+=200%", // Extra long
  pin: true,
  anticipatePin: 1,
  scrub: 2, // Very slow
  animation: directorTimeline
});

// Mirror flip effect
gsap.to(".director-content", {
  scaleX: -1, // Mirror
  duration: 0.8,
  ease: "power2.inOut",
  yoyo: true,
  repeat: 1
});

// Text STAYS - no exit animation
gsap.to(".mirror-text", {
  opacity: 1,
  filter: "blur(0px)",
  duration: 2,
  // Holds on screen - user must scroll past to dismiss
});
```

**Text Treatment**:
- Blur: 0px (crystallized, permanent)
- Stagger: 0.15s per word (deliberate)
- Easing: `power2.inOut` (balanced)
- Font: Medium, expanded tracking (declarative)
- Color: High contrast with glow effect

**Zone Card Content**:
```markdown
## THE DIRECTOR
*"AI is clay I sculpt."*

You've mastered iteration:
- You test variables systematically
- You refuse 80% quality
- You know exactly which levers to pull
- You control the outcome

**THE BREAKTHROUGH INSIGHT**:
*"I'm not correcting the AI. I'm clarifying my own thinking.

*When the output is ambiguous, the AI is just revealing the ambiguity in my own goals."*

Do you recognize this mirror moment?
```

**Recognition Trigger**: Interactive zone selector (user clicks their zone)

**On Recognition**:
```javascript
// Zone illuminates
gsap.to(".zone-4.selected", {
  scale: 1.15,
  boxShadow: "0 0 60px rgba(255,215,0,0.8)",
  duration: 0.6,
  ease: "elastic.out(1, 0.3)" // Celebration pulse
});

// Other zones dim
gsap.to(".zone:not(.selected)", {
  opacity: 0.3,
  filter: "blur(2px)",
  duration: 0.8
});
```

---

### Zone 5: The Builder (SPATIAL EXPLOSION)

**Scroll Range**: 60-75%
**Scrub Value**: 1.0 (balanced) + special branching trigger
**Duration**: 0.8s for explosion, then variable per path

**Narrative Context**:
- "I can create tools"
- The massive identity shift from user to creator
- Three paths emerge: Maker, Integrator, Analyst
- This is the CHOICE moment

**Animation Technique**: Spatial Explosion (Three Paths Erupt)

```javascript
// TRIGGER: When Zone 5 becomes center viewport
ScrollTrigger.create({
  trigger: ".zone-5",
  start: "top center",
  onEnter: () => {
    // Three paths ERUPT from center
    gsap.from(".path-maker, .path-integrator, .path-analyst", {
      scale: 0,
      opacity: 0,
      rotation: "random(-15, 15)",
      x: (i) => (i - 1) * 150, // Spread horizontally
      stagger: {
        each: 0.2,
        from: "center"
      },
      ease: "back.out(1.7)", // Overshoot for drama
      duration: 0.8
    });
  }
});
```

**Text Treatment**:
- Splits into THREE streams (one per path)
- Each path has different color scheme:
  - Maker: Warm orange (creative)
  - Integrator: Cool blue (systematic)
  - Analyst: Purple (insight)
- Stagger: 0.1s between streams

**Zone Card Content**:
```markdown
## THE BUILDER
*"I can create my own tools."*

You've broken through the identity barrier.
You see yourself as a creator, not just a user.

**Three paths await:**

### 🎨 THE MAKER
Custom GPTs, specialized agents, vibe coding
*"I package my prompting strategies into reusable tools"*

### 🔗 THE INTEGRATOR
APIs, workflows, automation
*"I connect AI into business systems"*

### 🧠 THE ANALYST
Strategic thinking, forecasting
*"I use AI to compress complex decision-making"*

**Which calls to you?**
```

**Pathway Animation**:
```javascript
// SVG pathways DRAW from Zone 5 to destinations
gsap.fromTo(".pathway-svg", {
  strokeDasharray: 1000,
  strokeDashoffset: 1000
}, {
  strokeDashoffset: 0,
  duration: 1.5,
  ease: "power2.inOut",
  stagger: 0.3 // Paths draw one by one
});

// Destination dots pulse in
gsap.from(".destination-dot", {
  scale: 0,
  opacity: 0,
  duration: 0.8,
  ease: "back.out(1.7)",
  stagger: 0.15
});
```

---

### Zone 6: The Architect

**Scroll Range**: 75-90%
**Scrub Value**: 2.0 (breathing room, contemplative)
**Duration**: 1.5-2.0s per animation

**Narrative Context**:
- "I design systems, not features"
- Sees AI as infrastructure
- Orchestrates multiple AI components
- Holistic process view

**Animation Technique**: System Connections

```javascript
// Connection lines draw between all zones
gsap.from(".connection-line", {
  strokeWidth: 0,
  opacity: 0,
  strokeWidth: 2,
  opacity: 0.6,
  duration: 2,
  ease: "power2.inOut",
  stagger: {
    amount: 1,
    from: "random"
  }
});

// Zones gently pulse to show systemic relationship
gsap.to(".zone", {
  scale: 1.02,
  duration: 2,
  yoyo: true,
  repeat: 3,
  ease: "sine.inOut"
});
```

**Text Treatment**:
- Sparse, poetic
- Long dwell time (breathing room)
- Stagger: 0.2s per line (very deliberate)
- Color: Muted, sophisticated

**Zone Card Content**:
```markdown
## THE ARCHITECT
*"I design AI-native systems."*

You see the whole system.
You orchestrate multiple AI components.
You redesign processes from the ground up.

**The invisible layer insight**:
*"AI-native design isn't about adding AI.
It's about fundamentally reimagining what's possible
when intelligence is cheap and pervasive."*

You're not just using AI.
You're architecting with AI.
```

---

### Zone 7: The Philosopher

**Scroll Range**: 90-100%
**Scrub Value**: 2.0 (meta, contemplative)
**Duration**: 2.0s+ (very slow, philosophical)

**Narrative Context**:
- "What does this mean for humanity?"
- Ethical and societal implications
- Meta-level reflection
- The groundedness barrier: "Philosophy doesn't ship"

**Animation Technique**: Philosophical Fade

```javascript
// Content fades slowly, leaving space for contemplation
gsap.to(".philosopher-content", {
  opacity: 1,
  filter: "blur(0px)",
  duration: 3,
  ease: "power2.inOut"
});

// Background elements recede
gsap.to(".background-elements", {
  opacity: 0.3,
  scale: 0.95,
  duration: 2,
  ease: "power2.out"
});
```

**Text Treatment**:
- Minimal text, maximum white space
- Very slow fade-in (3s+)
- No stagger (one unified thought)
- Color: Muted, elegant

**Zone Card Content**:
```markdown
## THE PHILOSOPHER
*"What does it mean that we can build this way?"*

You've transcended the how.
You're engaging with the why.

**Big questions**:
- What happens to human agency when machines can reason?
- How do we ensure knowledge remains grounded?
- Just because we can, should we?

This zone isn't for everyone.
But for leaders, for regulators, for anyone whose decisions shape society...

This reflection is vital.
```

**Final CTA**:
```javascript
gsap.from(".final-cta", {
  y: 50,
  opacity: 0,
  duration: 1.5,
  ease: "power3.out",
  delay: 1
});
```

> *"You're not behind. You're exactly where you need to be."*
> *"And now you can see the path forward."*
>
> **[Begin Your Journey]**

---

## Technical Architecture

### Core Technology Stack

```javascript
// GSAP Plugins
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText"; // For text crystallization

gsap.registerPlugin(ScrollTrigger, SplitText);
```

### Master Timeline Structure

```javascript
// Master timeline coordinates all zones
const masterTimeline = gsap.timeline({
  scrollTrigger: {
    trigger: ".territory-map-container",
    start: "top top",
    end: "bottom bottom",
    scrub: 1.5, // Base scrub - zones override this
  }
});

// Each zone adds its own timeline
masterTimeline
  .add(wildernessTimeline, 0)
  .add(delegatorTimeline, ">-0.5") // 0.5s overlap
  .add(collaboratorTimeline, ">-0.5")
  .add(directorTimeline, ">-0.3") // Less overlap (pin section)
  .add(builderTimeline, ">-0.5")
  .add(architectTimeline, ">-0.5")
  .add(philosopherTimeline, ">-0.5");
```

### Zone Configuration Object

```javascript
const zoneConfig = {
  0: { scrub: 0.3, duration: 0.5, ease: "power2.inOut", name: "wilderness" },
  1: { scrub: 0.3, duration: 0.5, ease: "power2.inOut", name: "wilderness" },
  2: { scrub: 0.5, duration: 0.3, ease: "power2.out", name: "delegator" },
  3: { scrub: 1.5, duration: 1.0, ease: "power2.out", name: "collaborator" },
  4: { scrub: 2.0, pin: true, duration: 2.0, ease: "power2.inOut", name: "director" },
  5: { scrub: 1.0, trigger: true, duration: 0.8, ease: "back.out(1.7)", name: "builder" },
  6: { scrub: 2.0, duration: 1.5, ease: "power2.inOut", name: "architect" },
  7: { scrub: 2.0, duration: 3.0, ease: "power2.inOut", name: "philosopher" }
};
```

### Performance Optimization

**GPU Acceleration Only**:
```javascript
// GOOD - Transforms (GPU-accelerated)
gsap.to(element, { x: 100, y: 50, scale: 1.1, rotation: 15 });

// BAD - Layout properties (causes reflow)
gsap.to(element, { width: "100%", top: "50px", left: "100px" });
```

**will-change Hint**:
```css
.zone-card {
  will-change: transform, opacity, filter;
}
```

**Particle Optimization** (Zone 0-1):
- Desktop: 50 particles
- Tablet: 30 particles
- Mobile: 15 particles

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)

**Tasks**:
1. Set up GSAP + ScrollTrigger project structure
2. Create HTML skeleton for all 7 zones
3. Implement basic CSS for zone cards
4. Set up master timeline structure
5. Test basic scroll triggering

**Deliverable**: Zones appear on scroll, no animations yet

### Phase 2: Zones 0-2 (Week 2)

**Tasks**:
1. Implement Zone 0-1 particle system
2. Add parallax layers (3-depth)
3. Build Zone 2 snap transitions
4. Create text crystallization effect
5. Test responsive behavior

**Deliverable**: Wilderness → Delegator fully functional

### Phase 3: Zones 3-4 (Week 3)

**Tasks**:
1. Implement Zone 3 fluid morphing
2. Build conversation flow animations
3. Create Zone 4 pin section
4. Implement mirror pause + hold
5. Build zone recognition selector

**Deliverable**: Collaborator → Director fully functional (BREAKTHROUGH MOMENT)

### Phase 4: Zone 5 Branching (Week 4)

**Tasks**:
1. Create spatial explosion animation
2. Draw three pathway SVGs
3. Animate path splitting
4. Add destination interactivity
5. Test all three path experiences

**Deliverable**: Builder zone with branching reveal

### Phase 5: Zones 6-7 (Week 5)

**Tasks**:
1. Implement Zone 6 system connections
2. Add zone pulse animation
3. Create Zone 7 philosophical fade
4. Build final CTA
5. End-to-end testing

**Deliverable**: Complete scroll experience

### Phase 6: Polish & Optimize (Week 6)

**Tasks**:
1. Performance testing (60fps validation)
2. Mobile optimization (blur fallbacks)
3. Accessibility audit (screen readers, keyboard nav)
4. Cross-browser testing
5. User acceptance testing

**Deliverable**: Production-ready implementation

---

## GSAP Code Examples

### Complete Zone 4 (Director) Implementation

```javascript
// Zone 4: The Director - BREAKTHROUGH MOMENT
const directorTimeline = gsap.timeline({
  scrollTrigger: {
    trigger: ".zone-4",
    start: "top center",
    end: "+=200%", // Extra long for dwell time
    pin: true, // HOLD user here
    anticipatePin: 1, // Smooth entry
    scrub: 2, // Very slow, contemplative
    toggleActions: "play none none reverse"
  }
});

// Mirror flip effect
directorTimeline
  .from(".mirror-content", {
    scaleX: -1,
    duration: 0.8,
    ease: "power2.inOut"
  })
  .to(".mirror-content", {
    scaleX: 1,
    duration: 0.8,
    ease: "power2.inOut"
  });

// Text crystallizes and HOLDS
const splitText = new SplitText(".mirror-text", { type: "words" });
directorTimeline.from(splitText.words, {
  filter: "blur(8px)",
  opacity: 0.3,
  stagger: 0.15,
  duration: 2,
  ease: "power2.inOut"
});

// Zone recognition trigger
const recognitionSelector = document.querySelector('.zone-selector');
recognitionSelector.addEventListener('change', (e) => {
  const selectedZone = e.target.value;

  // Highlight selected zone
  gsap.to(`.zone-${selectedZone}`, {
    scale: 1.15,
    boxShadow: "0 0 60px rgba(255,215,0,0.8)",
    duration: 0.6,
    ease: "elastic.out(1, 0.3)"
  });

  // Dim other zones
  gsap.to(".zone:not(.selected)", {
    opacity: 0.3,
    filter: "blur(2px)",
    duration: 0.8,
    ease: "power2.out"
  });

  // Show zone-specific content
  gsap.from(`.zone-${selectedZone} .insight-content`, {
    y: 30,
    opacity: 0,
    duration: 1,
    ease: "power2.out"
  });
});
```

### Zone 5 Branching Animation

```javascript
// Zone 5: The Builder - Spatial Explosion
const builderTimeline = gsap.timeline({
  scrollTrigger: {
    trigger: ".zone-5",
    start: "top center",
    end: "bottom center",
    scrub: 1,
    onEnter: () => triggerBranching(),
    onLeaveBack: () => resetBranching()
  }
});

function triggerBranching() {
  // Three paths ERUPT from center
  gsap.fromTo(".path-maker, .path-integrator, .path-analyst", {
    scale: 0,
    opacity: 0,
    rotation: (i) => (i - 1) * 15, // Spread angles
    x: (i) => (i - 1) * 200, // Spread horizontally
  }, {
    scale: 1,
    opacity: 1,
    rotation: (i) => (i - 1) * 15,
    x: (i) => (i - 1) * 200,
    stagger: {
      each: 0.2,
      from: "center"
    },
    ease: "back.out(1.7)", // Overshoot for drama
    duration: 0.8
  });

  // Pathway SVG lines DRAW
  gsap.fromTo(".pathway-svg", {
    strokeDasharray: 1000,
    strokeDashoffset: 1000
  }, {
    strokeDashoffset: 0,
    duration: 1.5,
    ease: "power2.inOut",
    stagger: 0.3
  });

  // Destination dots pulse in
  gsap.from(".destination-dot", {
    scale: 0,
    opacity: 0,
    scale: 1.2,
    ease: "back.out(1.7)",
    stagger: 0.15,
    duration: 0.8
  });
}

function resetBranching() {
  gsap.to(".path-maker, .path-integrator, .path-analyst", {
    scale: 0,
    opacity: 0,
    duration: 0.5
  });
}
```

---

## Performance & Mobile Considerations

### Desktop Performance Targets

- **Frame Rate**: Consistent 60fps
- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3s
- **Cumulative Layout Shift**: < 0.1

### Mobile Optimizations

**Blur Fallback** (Zone 0-1):
```javascript
const isMobile = window.innerWidth < 768;
const blurAmount = isMobile ? 0 : 12; // No blur on mobile
const blurDuration = isMobile ? 0.3 : 1.5; // Faster on mobile
```

**Particle Reduction**:
```javascript
const particleCount = isMobile ? 15 : 50;
```

**Simplify Pinning** (Zone 4):
```javascript
pin: isMobile ? false : true, // No pin on mobile (too janky)
scrub: isMobile ? 1 : 2 // Faster scrub on mobile
```

### Progressive Enhancement

```javascript
// Check for reduced motion preference
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

if (prefersReducedMotion.matches) {
  // Disable all animations
  // Show static content
} else {
  // Full animation experience
}
```

---

## Success Metrics

### Primary Metrics

1. **Recognition Rate**: % of users who complete zone selector
   - Target: > 70%
   - Measurement: Analytics event on zone selection

2. **Scroll Completion**: % of users who reach final CTA
   - Target: > 60%
   - Measurement: Scroll depth tracking

3. **Transformation Intent**: % who click "Begin Your Journey"
   - Target: > 40%
   - Measurement: CTA click rate

### Secondary Metrics

4. **Time in Zone 4**: Dwell time on breakthrough moment
   - Target: > 30 seconds
   - Measurement: Scroll position over time

5. **Branching Exploration**: % who explore multiple Zone 5 paths
   - Target: > 50%
   - Measurement: Path hover/click tracking

### Qualitative Metrics

6. **User Feedback**: "This is exactly how I feel" comments
   - Target: Collect 20 user testimonials
   - Measurement: Post-experience survey

7. **Social Sharing**: % who share experience
   - Target: > 15%
   - Measurement: Social share tracking

---

## Appendix: Design Principles

### The 10 Commandments Applied

1. ✅ **Motion = Narrative**: Each zone's technique tells its story
2. ✅ **Vary Timing**: Scrub values 0.3 → 2.0 create rhythm
3. ✅ **Staging Over Simultaneity**: Staggered reveals throughout
4. ✅ **Anticipate Reveals**: Particle drift builds anticipation
5. ✅ **Overlap Transitions**: Sections overlap by 0.3-0.5s
6. ✅ **User Control = Ownership**: Scrub creates participation
7. ✅ **Ease for Emotion**: Match easing to zone psychology
8. ✅ **80/20 Punctuation**: 80% subtle, 20% bold (Zone 4)
9. ✅ **Respect Breathing Room**: Zone 7 provides contemplation
10. ✅ **Test on Real Devices**: Mobile fallbacks specified

### Alignment with GSAP Research

**Anti-Patterns Avoided**:
- ❌ Uniform timing (prevented by variable scrub values)
- ❌ Animation without purpose (each technique serves zone psychology)
- ❌ Hard cuts (overlap transitions create flow)
- ❌ Missing emotional punctuation (Zone 4 is the bold climax)
- ❌ Linear easing (all animations use eased timing)

**Best Practices Applied**:
- ✅ GPU-accelerated properties only (transforms, no layout)
- ✅ Scrub for user control (zones 0-7)
- ✅ Staggered reveals (0.03-0.2s range)
- ✅ Breathing room (Zone 7)
- ✅ Mobile adaptations (blur fallback, particle reduction)

---

## Conclusion

This specification defines a **masterpiece-level scroll experience** that:

1. **Creates Trevor's breakthrough moment** for every user
2. **Applies GSAP research principles** comprehensively
3. **Matches Awwwards sophistication** (Working Stiff Films, Britive level)
4. **Provides modular architecture** for phased implementation
5. **Delivers strategic differentiation** in the AI education market

**The technique palette IS the Territory Map made visible.**

Every zone feels different because every zone IS different. Users don't just learn about zones—they EXPERIENCE them through choreography.

**Result**: Transformation through recognition, not education.

---

**Document Status**: Complete and Ready for Implementation
**Next Step**: Phase 1 - Foundation Setup
**Estimated Timeline**: 6 weeks to production
**Team Required**: Frontend Developer (GSAP specialist), UX Designer, Copywriter

---

*Generated by BMAD Party Mode - Dr. Quinn, Sophia, Sally, Caravaggio, Winston, Victor*
*Date: 2026-01-17*
