# Animation Assessment Workflow - K2M Landing Page

**Created:** 2026-02-15
**Purpose:** Systematic detection and prioritization of animation improvements
**Target:** Award-winning (Awwwards-level) scroll animations

---

## Part 1: Quick Visual Assessment Protocol (Team Meeting)

### Setup: Team Review Session
1. **Start dev server:** `npm run dev` (usually http://localhost:5173)
2. **Screen share** on large monitor
3. **Open browser DevTools:**
   - Press F12
   - Enable "Rendering" tab (Esc → More tools → Rendering)
   - Check "Frame rate" and "Scrolling performance issues"
4. **Devices to test:**
   - Desktop (1920×1080)
   - Laptop (1366×768)
   - Tablet (768×1024)
   - Mobile (375×812)

### 5-Minute Visual Checklist

**Scroll through page top to bottom, note:**

#### ✅ **FEELS SMOOTH & CINEMATIC?**
- [ ] Scroll feels buttery smooth (no jank)
- [ ] Animations have breathing room (not constant motion)
- [ ] User feels in control (scrub animations respond to scroll speed)
- [ ] Each section has distinct emotional feel
- [ ] There's a "WHOA moment" that makes you gasp

#### ❌ **FEELS GENERIC OR JANKY?**
- [ ] Repetitive fade-ins everywhere
- [ ] Animations trigger too late/early
- [ ] Scroll feels disconnected from animation
- [ ] All zones feel the same
- [ ] No memorable moments

---

## Part 2: Automated Detection (Technical Assessment)

### Detection Script: Run in Console
```javascript
// Paste in DevTools Console during team review

const issues = [];

// 1. Check ScrollTrigger scrub values
ScrollTrigger.getAll().forEach(st => {
  if (st.scrub === true || st.scrub < 1) {
    issues.push({
      type: 'FAST_SCRUB',
      trigger: st.trigger?.className || st.trigger?.id || 'unknown',
      scrub: st.scrub,
      severity: 'MEDIUM',
      fix: 'Change scrub to 1-2 for cinematic feel'
    });
  }
});

// 2. Check for missing pin on key sections
const territoryMap = document.querySelector('.territory-map');
if (territoryMap) {
  const st = ScrollTrigger.getByTrigger(territoryMap);
  if (!st || !st.pin) {
    issues.push({
      type: 'MISSING_PIN',
      section: 'Territory Map',
      severity: 'HIGH',
      fix: 'Add pin: true with end: "+=200%" for cinematic particle coalescence'
    });
  }
}

// 3. Check for identical animation patterns
const zoneAnimations = new Map();
document.querySelectorAll('.resonance-zone').forEach(zone => {
  const echoes = zone.querySelectorAll('.echo');
  const pattern = JSON.stringify({
    count: echoes.length,
    hasScale: true,
    hasOpacity: true
  });
  zoneAnimations.set(pattern, (zoneAnimations.get(pattern) || 0) + 1);
});

zoneAnimations.forEach((count, pattern) => {
  if (count > 2) {
    issues.push({
      type: 'REPETITIVE_PATTERN',
      pattern: pattern,
      sections: count,
      severity: 'HIGH',
      fix: 'Vary animation technique per zone (drift, snap, rotate, pulse)'
    });
  }
});

// 4. Check progress bar functionality
const progressNav = document.querySelector('.progress-nav');
if (progressNav) {
  const dots = progressNav.querySelectorAll('.progress-dot');
  let working = 0;
  dots.forEach(dot => {
    if (dot.classList.contains('active')) working++;
  });
  if (dots.length > 0 && working === 0) {
    issues.push({
      type: 'BROKEN_FEATURE',
      feature: 'Progress Navigation',
      severity: 'HIGH',
      fix: 'Progress dots not updating on scroll - check event handlers'
    });
  }
}

// 5. Check for missing text reveals
const zoneTitles = document.querySelectorAll('.resonance-zone h3, .constellation-zone h2');
if (zoneTitles.length > 0) {
  const hasTextAnimations = Array.from(zoneTitles).some(title => {
    return title.dataset.splitText === 'true' || gsap.isTweening(title);
  });
  if (!hasTextAnimations) {
    issues.push({
      type: 'MISSING_FEATURE',
      feature: 'Text Reveals',
      severity: 'MEDIUM',
      fix: 'Add SplitText staggered reveals for zone titles'
    });
  }
}

// 6. Check Zone 4 special treatment
const zone4 = document.querySelector('[data-zone="4"]');
if (zone4) {
  const hasSpecialTreatment = zone4.querySelector('.zone-4-glow') ||
                           zone4.dataset.special === 'true';
  if (!hasSpecialTreatment) {
    issues.push({
      type: 'MISSING_CLIMAX',
      section: 'Zone 4',
      severity: 'HIGH',
      fix: 'Zone 4 needs scale pulse + radial glow (the WHOA moment)'
    });
  }
}

// Output results
console.table(issues);
console.log(`Found ${issues.length} issues`);
```

### Performance Detection
```javascript
// Check for performance issues
const fps = [];
let lastTime = performance.now();
let frames = 0;

function measureFPS() {
  frames++;
  const currentTime = performance.now();
  if (currentTime >= lastTime + 1000) {
    fps.push(frames);
    frames = 0;
    lastTime = currentTime;
  }
  requestAnimationFrame(measureFPS);
}

measureFPS();

// Scroll through entire page, then check:
setTimeout(() => {
  const avgFPS = fps.reduce((a, b) => a + b, 0) / fps.length;
  const minFPS = Math.min(...fps);
  console.log(`Average FPS: ${avgFPS.toFixed(1)}`);
  console.log(`Minimum FPS: ${minFPS}`);

  if (avgFPS < 55) {
    console.warn('⚠️ Average FPS below 55 - optimize animations');
  }
  if (minFPS < 30) {
    console.error('❌ Minimum FPS below 30 - critical jank detected');
  }
}, 10000);
```

---

## Part 3: My Improvement Plan (Priority Order)

### **P0: CRITICAL (Must Fix for Awards)**

#### 1. Fix Progress Navigation Bar
**Current Issue:** Dots not updating on scroll
**Impact:** Users don't know where they are in journey
**Effort:** 1 hour
**File:** `src/components/ProgressNav/ProgressNav.js`

```javascript
// Fix: Ensure ScrollTrigger updates dots
ScrollTrigger.create({
  trigger: zone,
  start: 'top 55%',
  end: 'bottom 45%',
  onEnter: () => {
    updateProgressDot(index); // ← THIS MUST WORK
  }
});
```

#### 2. Add Territory Map Pinning
**Current Issue:** Particles coalesce while scrolling past too fast
**Impact:** No cinematic moment, particles go by unnoticed
**Effort:** 2 hours
**File:** `src/components/TerritoryMap/MapParticles.js:172-180`

```javascript
// Change scrub: 0.3 → scrub: 2
// Add pin: true
this.timeline = gsap.timeline({
  scrollTrigger: {
    trigger: '.territory-map',
    start: 'top top',      // ← CHANGE from 'top center'
    end: '+=200%',         // ← ADD THIS (pin for 2x viewport)
    pin: true,             // ← ADD THIS
    scrub: 2,              // ← CHANGE from 0.3
    anticipatePin: 1
  }
});
```

#### 3. Zone 4 "WHOA Moment"
**Current Issue:** Zone 4 feels same as others
**Impact:** No emotional climax
**Effort:** 3 hours
**File:** `src/components/ResonanceZone/resonanceZone.js:73-107`

```javascript
// Add special treatment for zone 4
function activateZone(zone, index, echoes, progressDots) {
  // ... existing code ...

  if (index === 4) {
    // Zone 4 special: Scale pulse + radial glow
    gsap.fromTo(zone, {
      scale: 0.95,
      filter: 'brightness(1)'
    }, {
      scale: 1,
      filter: 'brightness(1.3)',
      duration: 0.8,
      ease: 'power3.out'
    });

    // Add radial glow element
    const glow = document.createElement('div');
    glow.className = 'zone-4-glow';
    glow.style.cssText = `
      position: absolute;
      inset: -50%;
      background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
      opacity: 0;
      pointer-events: none;
    `;
    zone.appendChild(glow);

    gsap.to(glow, {
      opacity: 1,
      scale: 1.5,
      duration: 1,
      ease: 'power2.out'
    });
  }
}
```

---

### **P1: HIGH (Significant Quality Boost)**

#### 4. Emotional Differentiation per Zone
**Current Issue:** All zones use same animation pattern
**Impact:** Feels repetitive, not award-winning
**Effort:** 6 hours
**File:** `src/components/ResonanceZone/resonanceZone.js:73-107`

**Zone-by-Zone Plan:**

```javascript
// Zone 0 (Confusion → Curiosity)
// Drifting, uncertain motion
gsap.to(echoes, {
  y: (i) => Math.sin(i * 0.5) * 10, // Gentle wave
  opacity: 1,
  scale: (i) => 0.95 + Math.random() * 0.1, // Slight size variation
  duration: 0.8,
  stagger: { amount: 1.5, from: 'random' },
  ease: 'power1.inOut' // Gentle, uncertain
});

// Zone 1 (Curiosity → Recognition)
// Quick, energetic reveals
gsap.to(echoes, {
  y: 0,
  opacity: 1,
  scale: 1,
  duration: 0.4,
  stagger: { each: 0.05, from: 'start' },
  ease: 'power2.out' // Snappy
});

// Zone 2 (Recognition → Understanding)
// Snap into place, structured
gsap.fromTo(echoes, {
  y: -20,
  opacity: 0,
  scale: 1.1
}, {
  y: 0,
  opacity: 1,
  scale: 1,
  duration: 0.5,
  stagger: { each: 0.08, from: 'center' }, // Explode from center
  ease: 'back.out(1.7)' // Overshoot then settle
});

// Zone 3 (Understanding → Collaboration)
// Magnetic pull, rotation toward zone 4
gsap.to(echoes, {
  y: 0,
  opacity: 1,
  rotation: (i) => (i - echoes.length/2) * 5, // Slight rotation
  duration: 0.6,
  stagger: { amount: 1.0, from: 'edges' }, // Close inward
  ease: 'power2.inOut'
});

// Zone 4 (Collaboration → Confidence)
// THE WHOA MOMENT (already covered in P0)
```

#### 5. Text Reveals with SplitText
**Current Issue:** Text appears instantly with zones
**Impact:** Less polished, missing storytelling opportunity
**Effort:** 4 hours
**File:** `src/components/ResonanceZone/resonanceZone.js`

```javascript
// Add to activateZone function
const zoneTitle = zone.querySelector('h3');
if (zoneTitle && !zoneTitle.dataset.splitText) {
  // Split text into words
  const words = zoneTitle.textContent.split(' ');
  zoneTitle.innerHTML = words.map((word, i) =>
    `<span class="word" style="display:inline-block; opacity:0; transform:translateY(30px); transition:all 0.6s ${i * 0.08}s ease-out;">${word}</span>`
  ).join(' ');
  zoneTitle.dataset.splitText = 'true';
}

// Animate words
const wordSpans = zoneTitle.querySelectorAll('.word');
gsap.to(wordSpans, {
  y: 0,
  opacity: 1,
  duration: 0.6,
  stagger: 0.08,
  ease: 'power2.out'
});
```

---

### **P2: MEDIUM (Polish & Delight)**

#### 6. Breathing Room Between Zones
**Current Issue:** Every zone animates constantly
**Impact:** Fatigue, no rhythm
**Effort:** 2 hours
**File:** `src/components/ResonanceZone/resonanceZone.js`

```javascript
// Add delay between zones
zones.forEach((zone, index) => {
  if (index > 0) {
    const prevZone = zones[index - 1];
    const gap = zone.offsetTop - prevZone.offsetTop - prevZone.offsetHeight;

    // If gap < 300px, add breathing room
    if (gap < 300) {
      zone.style.marginTop = `${300 - gap}px`;
    }
  }
});
```

#### 7. Hover Micro-interactions
**Current Issue:** Echoes have basic hover
**Impact:** Missing delightful moments
**Effort:** 3 hours
**File:** `src/components/ResonanceZone/resonanceZone.js:65-68`

```javascript
echo.addEventListener('mouseenter', () => {
  gsap.to(echo, {
    scale: 1.05,
    filter: 'brightness(1.2)',
    duration: 0.2,
    ease: 'power2.out'
  });
});

echo.addEventListener('mouseleave', () => {
  gsap.to(echo, {
    scale: 1,
    filter: 'brightness(1)',
    duration: 0.3,
    ease: 'power2.out'
  });
});
```

---

## Part 4: My Workflow for Team Reviews

### **Step 1: Quick Health Check (5 min)**
1. Run automated detection script (above)
2. Check console for issues
3. Note severity counts (HIGH/MEDIUM/LOW)

### **Step 2: Visual Scroll-Through (10 min)**
1. Team watches single scroll-through
2. Each person notes 3 things:
   - 😍 "Love this" (what's working)
   - 😕 "Confusing" (what's unclear)
   - 😐 "Boring" (what needs punch)
3. Vote on top 3 improvements

### **Step 3: A/B Testing (15 min)**
1. Pick 1 HIGH-severity issue
2. Implement quick fix
3. Test side-by-side (before/after)
4. Decide: ship or iterate

### **Step 4: Performance Validation (5 min)**
1. Run FPS measurement script
2. Scroll through on worst device (mobile)
3. If FPS < 45, optimize before adding more

### **Step 5: Award Criteria Checklist (5 min)**
Against Awwwards winners:
- [ ] Emotional journey clear?
- [ ] Animation vocabulary varied?
- [ ] User control feels responsive?
- [ ] Performance > 55 FPS?
- [ ] Memorable moment exists?
- [ ] Accessible (reduced motion)?

---

## Part 5: Quick Win Fixes (Under 1 Hour Each)

### Fix 1: Add Smooth Scroll Duration (15 min)
**File:** `src/utils/lenis-config.js`
```javascript
// Change smoothness
lenis = new Lenis({
  duration: 1.2, // ← Increase from default 1.0
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t),
  direction: 'vertical',
  gestureDirection: 'vertical',
  smooth: true,
  mouseMultiplier: 1,
  smoothTouch: false,
  touchMultiplier: 2,
  infinite: false,
});
```

### Fix 2: Add Scroll Progress Indicator (30 min)
**File:** `src/main.js`
```javascript
// Add to main.js
const scrollProgress = document.createElement('div');
scrollProgress.style.cssText = `
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(to right, #6366f1, #8b5cf6);
  width: 0%;
  z-index: 9999;
  pointer-events: none;
`;
document.body.appendChild(scrollProgress);

gsap.to(scrollProgress, {
  width: '100%',
  ease: 'none',
  scrollTrigger: {
    start: 'top top',
    end: 'bottom bottom',
    scrub: 0.3
  }
});
```

### Fix 3: Optimize Particle Count (15 min)
**File:** `src/components/TerritoryMap/MapParticles.js:48`
```javascript
// Reduce particle count for better performance
this.articleCount = this.isMobile ? 70 : 200; // ← Was 105/300
```

---

## Summary: What I'd Do First

If given this site today to push to award-winning:

1. **Morning (3 hours):**
   - Fix progress navigation (P0)
   - Add Territory Map pinning (P0)
   - Test FPS on mobile

2. **Afternoon (4 hours):**
   - Zone 4 WHOA moment (P0)
   - Zone emotional differentiation (P1)
   - Text reveals (P1)

3. **Next Day (4 hours):**
   - Breathing room (P2)
   - Hover micro-interactions (P2)
   - Performance optimization
   - Team review & iteration

**Total Effort:** ~11 hours over 2-3 days
**Expected Result:** 80-90% toward award-winning quality

---

**Next Step for Team:**
1. Run Part 1 (Visual Assessment) together
2. Run Part 2 (Detection Script) - note issues
3. Prioritize based on severity
4. Pick ONE P0 fix, implement, test
5. Repeat until all P0s done
