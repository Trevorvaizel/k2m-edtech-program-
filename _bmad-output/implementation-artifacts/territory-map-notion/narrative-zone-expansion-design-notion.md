# 🌐 Narrative-Driven Zone Expansion System
## 🎬 GSAP-Inspired Territory Map Transformation

> **Date:** 2026-01-17
> **Author:** Dev Agent + Trevor (Collaborative Design)
> **Status:** Design Proposal - Ready for Review

---

## 📊 1. Current State Analysis

### What We Have
- **Static Map:** 5 zones positioned absolutely along a diagonal path
- **All Visible:** Zones 0-4 displayed simultaneously with opacity gradient (0.3 → 1.0)
- **Particle System:** MapParticles.js creates particles around zones (Story 2.2)
- **Box Layout:** Fixed 220px boxes positioned at SVG coordinates
- **Mobile Fallback:** Vertical stack on mobile (no diagonal path)

### 🎬 What's Missing (GSAP Inspiration)
- ❌ No narrative progression (zones don't "tell a story")
- ❌ No dynamic expand/collapse behavior
- ❌ No big animated text reveals
- ❌ No playful morphing animations
- ❌ No scroll-driven zone-by-zone journey
- ❌ Zones feel like "boxes" not "milestones"

---

## 📖 2. Vision: From Static Map to Narrative Journey

### Core Concept
**"Zone Zero → Expand → Collapse → Next Zone"**

Transform the territory map from a static infographic into a scroll-driven narrative where:

1. **Zone 0 starts EXPANDED** (full viewport, big text)
2. User scrolls → Zone 0 collapses, Zone 1 expands
3. Progressive journey through all 5 zones
4. Each zone has its own "moment" with unique animations
5. Big animated text that crystallizes from blur
6. Playful elements: morphing shapes, rolling balls, paper planes

### 💭 Emotional Arc per Zone

| Zone | Emotion | Animation Style | Text Treatment |
|------|---------|-----------------|----------------|
| **Zone 0** | Overwhelmed | Heavy fog, particles drifting | Heavy blur → sharp |
| **Zone 1** | Curiosity | Gentle spark, particles coalesce | Medium blur → sharp |
| **Zone 2** | Exploration | Rolling elements, horizontal motion | Light blur → sharp |
| **Zone 3** | Confidence | Spiral motion, vertical expansion | Sharp from start |
| **Zone 4** | Mastery | Paper planes, celebration, big text | HUGE text, glow |

---

## 🔧 3. Technical Approach

### 🌐 3.1 Scroll-Driven Zone Transitions

**Pattern:** Pin & Expand (GSAP ScrollTrigger)

```javascript
// Pseudo-code
gsap.timeline({
  scrollTrigger: {
    trigger: '.territory-map',
    start: 'top top',
    end: '+=5000', // 5 sections × 1000px each
    pin: true,
    scrub: 1
  }
})

// Zone 0: Full screen → collapse
.to('.zone-0', {
  scale: 0.3,
  opacity: 0.3,
  duration: 1
})

// Zone 1: Expand → collapse
.to('.zone-1', {
  scale: 1,
  opacity: 1,
  duration: 1
}, '-=0.5')
.to('.zone-1', {
  scale: 0.3,
  opacity: 0.3,
  duration: 1
})

// ... repeat for all zones
```

### 🌐 3.2 Zone State Management

**Three States per Zone:**

1. **Collapsed** (scale: 0.3, opacity: 0.3, blur: 12px)
   - Previous zones stay collapsed
   - Positioned in original SVG path positions

2. **Active** (scale: 1, opacity: 1, blur: 0px)
   - Centered in viewport
   - Full text reveal
   - Unique playful animation

3. **Future** (opacity: 0, scale: 0)
   - Hidden until their turn
   - Fade in when approaching

### ⚙️ 3.3 Big Animated Text System

**Text Reveal Pattern:** Heavy Blur → Sharp + Scale Up

```javascript
// For each zone title
gsap.fromTo('.zone-title', {
  filter: 'blur(20px)',
  scale: 0.5,
  opacity: 0
}, {
  filter: 'blur(0px)',
  scale: 1,
  opacity: 1,
  duration: 1.5,
  ease: 'power2.out'
})
```

**Zone 4 Special Treatment:**
- Scale: 2.0 (HUGE text)
- Glow effect
- Ocean mint color (#40E0D0)
- Text: "I CONTROL THE QUALITY"

---

## 🌐 4. Playful Animations per Zone

### 🌐 Zone 0: "The Fog" (Overwhelmed)
- **Particles:** Chaos → Order (already implemented in MapParticles.js)
- **Text:** Heavy blur (20px) → sharp
- **Motion:** Gentle horizontal drift
- **Duration:** 1s (slower, feels heavy)

### 🌐 Zone 1: "The Spark" (Curiosity)
- **Particles:** Coalesce into clusters
- **Text:** Medium blur (10px) → sharp
- **Motion:** Gentle pulsing glow
- **Special:** Small particles orbit the zone
- **Duration:** 0.8s (faster, more excited)

### 🌐 Zone 2: "The Exploration" (Discovery)
- **Particles:** Horizontal lines connecting to next zone
- **Text:** Light blur (5px) → sharp
- **Motion:** Rolling elements (balls moving horizontally)
- **Special:** Particles form "bridge" to Zone 3
- **Duration:** 0.6s (momentum building)

### 🌐 Zone 3: "The Confidence" (Mastery)
- **Particles:** Spiral motion (vortex effect)
- **Text:** Sharp from start (no blur)
- **Motion:** Vertical expansion (zone grows upward)
- **Special:** Particles stream upward like a fountain
- **Duration:** 0.5s (fast, confident)

### 🌐 Zone 4: "The Summit" (Celebration)
- **Particles:** Paper planes flying outward + celebration burst
- **Text:** HUGE (scale: 2.0), ocean mint glow
- **Motion:** Explosive celebration, particles radiating outward
- **Special:** All previous zones pulse in rhythm
- **Duration:** 1.5s (grand finale, slower)

---

## 5. Component Architecture

### 🏗️ New File Structure

```
src/components/TerritoryMap/
├── TerritoryMap.html          (Update: Zone state containers)
├── TerritoryMap.css           (Update: Zone states, transitions)
├── TerritoryMap.js            (NEW: Main controller)
├── ZoneExpansionSystem.js     (NEW: Pin & expand logic)
├── TextReveals.js             (NEW: Big text animations)
└── PlayfulAnimations.js       (NEW: Zone-specific playful effects)
```

### Key Classes

**1. ZoneExpansionSystem**
- Manages pin & expand behavior
- Controls zone state transitions (collapsed → active → collapsed)
- Handles scroll-triggered timeline
- Mobile responsive: Vertical stack without pin

**2. TextReveals**
- Blur → sharp animations
- Scale up effects
- Zone 4 special HUGE text treatment
- Staggered reveals for multi-line text

**3. PlayfulAnimations**
- Zone-specific animation patterns
- Particle motion variations (horizontal, spiral, etc.)
- Rolling elements, paper planes, celebration effects
- Performance optimizations (reduced motion fallback)

---

## ⚙️ 6. Implementation Phases

### 🏛️ Phase 1: Foundation (Setup)
- [ ] Update TerritoryMap.html with zone state containers
- [ ] Add CSS classes for zone states (collapsed, active, future)
- [ ] Create TerritoryMap.js main controller
- [ ] Setup basic ScrollTrigger pin configuration

### 🌐 Phase 2: Zone Expansion Logic
- [ ] Implement ZoneExpansionSystem class
- [ ] Create scroll-driven timeline for all 5 zones
- [ ] Test zone state transitions (collapsed → active → collapsed)
- [ ] Add mobile fallback (vertical stack, no pin)

### 📋 Phase 3: Big Text Reveals
- [ ] Implement TextReveals class
- [ ] Create blur → sharp animations for each zone
- [ ] Add scale up effects
- [ ] Implement Zone 4 HUGE text treatment
- [ ] Test text timing with zone transitions

### 🎭 Phase 4: Playful Animations
- [ ] Implement PlayfulAnimations class
- [ ] Create Zone 0 fog animation
- [ ] Create Zone 1 spark + orbit effect
- [ ] Create Zone 2 rolling elements + bridge
- [ ] Create Zone 3 spiral + fountain
- [ ] Create Zone 4 paper planes + celebration

### 🧪 Phase 5: Polish & Testing
- [ ] Performance testing (FPS monitoring)
- [ ] Reduced motion accessibility
- [ ] Mobile responsive testing
- [ ] Cross-browser testing
- [ ] Visual regression tests (screenshots)

---

## 🎬 7. GSAP Techniques We'll Use

### From Research Findings

1. **Pin & Spacer** (k72.ca style)
   - Sections pinned during expansion
   - Pin spacing pushes scroll position

2. **ScrollTrigger Accordion**
   - Zones expand/collapse based on scroll
   - Only one zone active at a time

3. **Scrub Animation**
   - Timeline scrubbing synchronized with scroll
   - Smooth forward/backward control

4. **Height Animations**
   - Animate zone height during expansion
   - Smooth transitions to auto height

5. **Timeline Management**
   - Multiple ScrollTrigger instances on common timeline
   - Overlapping animations for "stitch pattern"

---

## ⚡ 8. Performance Considerations

### Optimizations
- **Will-change:** GPU acceleration for transforms
- **Particle Reduction:** Mobile = 50% fewer particles
- **FPS Monitoring:** Kill animations if < 30 FPS
- **Reduced Motion:** Instant appearance fallback
- **Lazy Loading:** Animate only when in viewport

### 📱 Mobile Strategy
- **No Pin:** Let content flow naturally
- **Vertical Stack:** Zones stack vertically
- **Simplified Animations:** Remove complex particle effects
- **Faster Durations:** 50% shorter animations

---

## 🧪 9. Testing Strategy

### 👁️ Visual Tests
- [ ] Zone 0 expanded state screenshot
- [ ] Zone 1 expanded state screenshot
- [ ] Zone 2 expanded state screenshot
- [ ] Zone 3 expanded state screenshot
- [ ] Zone 4 expanded state screenshot (HUGE text)
- [ ] Transition states (Zone 0 → 1, Zone 1 → 2, etc.)

### ⚡ Performance Tests
- [ ] FPS > 55 on desktop
- [ ] FPS > 30 on mobile
- [ ] Scroll latency < 16ms
- [ ] Memory leak checks (cleanup methods)

### Accessibility Tests
- [ ] Reduced motion preference works
- [ ] Screen reader announces zone transitions
- [ ] Keyboard navigation works
- [ ] Color contrast passes WCAG AA

---

## ➡️ 10. Next Steps

### Option A: Full Rewrite (Recommended)
- Start fresh with narrative-driven architecture
- Abandon static "boxes on map" approach
- Build scroll-driven zone expansion system from scratch
- More work, but matches GSAP-inspired vision

### Option B: Incremental Evolution
- Keep existing map structure
- Add expand/collapse on top of current layout
- Faster to implement, but less dramatic transformation
- May feel like "bolted on" rather than native

### Option C: Hybrid (Best of Both)
- Keep particle system (Story 2.2 work is good)
- Redesign zone layout for expand/collapse
- Reuse MapParticles.js but reposition for new zone states
- Balance innovation with existing work

---

## 🎙️ 11. Questions for Trevor

1. **Preferred Approach:** Option A (rewrite), B (incremental), or C (hybrid)?

2. **Zone Copy:** Do you want to involve Sophia (copywriter) to refine the zone text for the new narrative approach?

3. **Animation Complexity:** Should we go full GSAP (paper planes, spirals, etc.) or keep it simpler for MVP?

4. **Mobile Experience:** Should mobile have the same expand/collapse behavior (vertical) or a simplified version?

5. **Performance Priority:** How important is 60 FPS vs. animation complexity? (Can reduce particle count for smoother experience)

6. **Timeline:** When do you want this implemented? (Affects testing depth and polish level)

---

## 12. Reference Materials

### 🎬 GSAP Examples to Study
- [Scroll-based accordion](https://gsap.com/community/forums/topic/27806-scroll-based-accordion/)
- [Sections stacked and expanding](https://gsap.com/community/forums/topic/37657-how-to-sections-stacked-of-each-other-and-expanding-one-by-one-with-example/)
- [ScrollTrigger Showcase](https://codepen.io/collection/DkvGzg)
- [Building Scroll-Driven Text Animation](https://tympanus.net/codrops/2026/01/15/building-a-scroll-driven-dual-wave-text-animation-with-gsap/)

### ⚙️ Current Implementation
- TerritoryMap.html:108 (zone structure)
- TerritoryMap.css:50 (zone positioning)
- MapParticles.js:18 (particle system - reuse this!)

---

**Ready to proceed with implementation pending your feedback on the questions above.** 🚀
