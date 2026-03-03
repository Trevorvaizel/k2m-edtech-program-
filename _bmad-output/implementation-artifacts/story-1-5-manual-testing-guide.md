# Story 1.5 Manual Testing Guide

## Quick Verification (Start Here)

### 1. Verify Hero Animations Work

**Open your browser:**
```bash
# Make sure dev server is running
npm run dev
```

Then open: http://localhost:5173

**What you should see:**
- ✅ Title "Using AI but don't feel in control?" visible immediately
- ✅ Subtitle "You're not alone." fades in as you scroll
- ✅ Body text "Most students we meet..." fades in smoothly
- ✅ Ocean mint glow on "in control?" and "Here's what nobody tells you:" glows
- ✅ Console shows "Desktop animations initialized - full complexity"
- ✅ Console shows "Performance: X FPS" logs every second

**Console should show:**
```
✅ Hero section loaded
✅ GSAP + Lenis initialized successfully
✅ Smooth scroll active
Desktop animations initialized - full complexity
Performance: 60 FPS
Performance: 60 FPS
```

### 2. Verify Mobile Responsive

**Resize browser to mobile (375px width):**
- ✅ Layout switches to mobile (text left-aligned)
- ✅ Console shows "Mobile animations initialized - simplified for performance"
- ✅ Animations still work but are faster/simpler
- ✅ No parallax layers (desktop-only feature)

---

## Task 3: Lighthouse Audit (Performance Score 90+)

### Desktop Lighthouse Test

**Step 1: Open Chrome DevTools**
- Press `F12` or right-click → "Inspect"

**Step 2: Go to Lighthouse Tab**
- Click the "Lighthouse" tab (or ">>" → "Lighthouse")

**Step 3: Configure Lighthouse**
- ✅ Check "Performance"
- Uncheck others (Focus, Accessibility, etc.)
- Device: **Desktop**
- Throttling: **No throttling** (simulates fast desktop)

**Step 4: Run Audit**
- Click "Analyze page load"
- Wait 30-60 seconds

**Step 5: Check Results**
```
Target Scores:
├─ Performance: 90+ ✅ PASS
├─ First Contentful Paint: < 1.5s ✅
├─ Time to Interactive: < 3.5s ✅
├─ Cumulative Layout Shift: 0 ✅
├─ Total Blocking Time: < 200ms ✅
└─ Speed Index: < 3.4s ✅
```

**If Performance < 90:**
- Look for "Opportunities" section
- Common fixes:
  - "Reduce JavaScript execution time" → Simplify animations
  - "Eliminate render-blocking resources" → Already done in Story 1.2
  - "Avoid enormous network payloads" → Check bundle size

### Mobile Lighthouse Test

**Repeat Steps 1-5 with:**
- Device: **Mobile**
- Throttling: **Slow 4G** (simulates real mobile)

**Mobile Targets (slightly relaxed):**
- Performance: 85+ (mobile has lower expectations)
- First Contentful Paint: < 1.8s
- Time to Interactive: < 4.0s

**Document Your Results:**
```markdown
## Lighthouse Audit Results

**Desktop:** [Date]
- Performance: [Score]/100
- FCP: [X.X]s
- TTI: [X.X]s
- CLS: [X.X]

**Mobile:** [Date]
- Performance: [Score]/100
- FCP: [X.X]s
- TTI: [X.X]s
- CLS: [X.X]
```

---

## Task 4: Desktop 60fps Performance Testing

### Chrome DevTools Performance Tab

**Step 1: Open Performance Tab**
- DevTools → "Performance" tab

**Step 2: Prepare Recording**
- Check "Screenshots" checkbox (visual reference)
- Uncheck "Network" (faster recording)

**Step 3: Start Recording**
- Click red circle button (or press `Ctrl+E`)

**Step 4: Interact with Page**
- Scroll through Hero section slowly (top to bottom)
- Scroll back up
- Wait 3-5 seconds

**Step 5: Stop Recording**
- Click red square button (or press `Ctrl+E`)

**Step 6: Analyze FPS Graph**
```
What to Look For:
├─ FPS graph (top chart)
│  └─ Should be flat line at 60fps (green)
├─ Long Tasks (red bars in Main thread)
│  └─ Should be NONE (no red bars)
├─ Frames (Main thread section)
│  └─ All should be < 50ms (no yellow/red frames)
└─ System info shows "60 FPS"
```

**Success Criteria:**
- ✅ FPS graph stays at 60fps (green line, no drops)
- ✅ No long tasks (>50ms) in flame graph
- ✅ No jank or stutter during scroll
- ✅ Scroll feels smooth (Lenis effect working)

**If FPS Drops Below 55:**
- Check for "Long Tasks" (red bars)
- Look at "Main" thread → What's causing delay?
- Common issues:
  - Too many elements animating at once
  - Large images loading (not applicable yet)
  - Third-party scripts (not applicable yet)

### Cross-Browser Desktop Testing

**Test on Multiple Browsers:**

**Chrome (Primary)**
```bash
# Already tested above
# Should be 60fps ✅
```

**Firefox**
```bash
# Open http://localhost:5173 in Firefox
# Press F12 → Performance → Record
# Scroll through Hero section
# Target: 60fps (may vary slightly)
```

**Safari (macOS only)**
```bash
# Open in Safari
# Develop → Show Web Inspector
# Timelines tab → Record
# Scroll through Hero section
# Target: 60fps
# Watch for GSAP/Lenis conflicts
```

**Document Your Results:**
```markdown
## Desktop FPS Testing

**Chrome:** [Date]
- Average FPS: [X]
- Min FPS: [X]
- Max FPS: [X]
- Jank observed: [Yes/No]

**Firefox:** [Date]
- Average FPS: [X]
- Min FPS: [X]
- Max FPS: [X]
- Jank observed: [Yes/No]

**Safari:** [Date] (if applicable)
- Average FPS: [X]
- Min FPS: [X]
- Max FPS: [X]
- Jank observed: [Yes/No]
```

---

## Task 5: Mobile 45fps+ Performance Testing

### Option 1: Real Device Testing (Best)

**iOS Safari Testing (iPhone 12+)**

**Step 1: Enable Web Inspector on iPhone**
- iPhone: `Settings` → `Safari` → `Advanced` → `Web Inspector: ON`

**Step 2: Connect iPhone to Mac**
- Use USB cable
- Mac: `Develop` → `[Your iPhone]` → `[Your Page]`

**Step 3: Open Safari Web Inspector**
- Similar to Chrome DevTools
- Go to "Timelines" tab

**Step 4: Record Performance**
- Click "Record" (red circle)
- Scroll through Hero section on iPhone
- Click "Stop"

**Step 5: Check FPS**
- Target: 45fps or higher
- Look for "Frames" section in timeline
- Check for dropped frames (red/yellow)

**Step 6: Test Touch Scrolling**
- Scroll with finger (not mouse)
- Should feel smooth
- No "stutter" or "skip"
- Mobile URL bar should hide/show smoothly

**Android Chrome Testing (Samsung Galaxy S21+)**

**Step 1: Enable USB Debugging on Android**
- Android: `Settings` → `Developer Options` → `USB Debugging: ON`

**Step 2: Connect Android to Computer**
- Use USB cable
- Computer: Chrome → `chrome://inspect`

**Step 3: Select Device and Page**
- Find your device under "Remote Target"
- Click "inspect"

**Step 4: Use Chrome DevTools**
- Same as desktop DevTools
- Go to "Performance" tab

**Step 5: Record & Test**
- Record performance
- Scroll on Android device
- Check FPS graph

**Step 6: Test Touch Scrolling**
- Smooth scrolling with finger
- No jank or lag
- Check mobile URL bar behavior
  - Scroll to bottom → bar should hide
  - No layout shift when bar hides

### Option 2: Chrome DevTools Device Emulation (Quick Test)

**Step 1: Enable Device Mode**
- DevTools → Click "Device Toggle" (Ctrl+Shift+M)

**Step 2: Select Mobile Device**
- Dropdown: "iPhone 12 Pro" or "Samsung Galaxy S21+"

**Step 3: Set Network Throttling**
- Network tab → Dropdown: "Fast 3G" (or "Slow 4G")
- This simulates mobile network

**Step 4: Test Performance**
- Performance tab → Record
- Scroll in mobile viewport (375px width)
- Check FPS (target: 45fps+)
- Not as accurate as real device, but quick test

**Success Criteria:**
- ✅ Animations maintain 45fps or higher
- ✅ Occasional drops to 30fps are acceptable
- ✅ No extended periods below 30fps
- ✅ Touch scrolling feels smooth
- ✅ No horizontal scrolling
- ✅ Mobile URL bar hides/shows without layout shift

**Document Your Results:**
```markdown
## Mobile FPS Testing

**iPhone 12+ (iOS Safari):** [Date]
- Average FPS: [X]
- Min FPS: [X]
- Max FPS: [X]
- Touch scroll smooth: [Yes/No]
- URL bar issue: [Yes/No]

**Android (Chrome):** [Date]
- Average FPS: [X]
- Min FPS: [X]
- Max FPS: [X]
- Touch scroll smooth: [Yes/No]
- URL bar issue: [Yes/No]
```

---

## Summary Checklist

**Task 3: Lighthouse Audit**
- [ ] Desktop Performance: 90+
- [ ] Desktop FCP: < 1.5s
- [ ] Desktop TTI: < 3.5s
- [ ] Desktop CLS: 0
- [ ] Mobile Performance: 85+
- [ ] Mobile FCP: < 1.8s
- [ ] Mobile TTI: < 4.0s

**Task 4: Desktop 60fps Testing**
- [ ] Chrome: 60fps consistent
- [ ] Firefox: 60fps (tested if available)
- [ ] Safari: 60fps (tested if available)
- [ ] No long tasks (>50ms)
- [ ] No jank/stutter
- [ ] Lenis smooth scroll working

**Task 5: Mobile 45fps+ Testing**
- [ ] iOS Safari: 45fps+ (or tested via emulation)
- [ ] Android Chrome: 45fps+ (or tested via emulation)
- [ ] Touch scrolling smooth
- [ ] No horizontal scrolling
- [ ] Mobile URL bar works correctly

---

## Common Issues & Fixes

**Issue 1: Animations not visible on page load**
- **Symptom:** Text stays invisible (opacity: 0)
- **Cause:** ScrollTrigger not firing
- **Fix:** Already fixed in commit 45583f7
- **Verify:** Refresh page, text should fade in on load

**Issue 2: Low FPS (< 30)**
- **Symptom:** Choppy animations
- **Cause:** Too many animations running
- **Fix:** Check parallax layers (desktop only, 3 layers max)
- **Verify:** Mobile should skip parallax

**Issue 3: Console logs not showing**
- **Symptom:** No "Performance: X FPS" logs
- **Cause:** monitorPerformance() not called
- **Fix:** Check Hero.js:152 has `monitorPerformance()`
- **Verify:** Open console, should see FPS logs every second

**Issue 4: Lighthouse Performance < 90**
- **Symptom:** Low Lighthouse score
- **Cause:** Large JS bundle or slow animations
- **Fix:** Check bundle size (should be < 200KB gzipped)
- **Verify:** Run `npm run build` → Check dist folder size

---

## Next Steps After Testing

**If All Tests Pass:**
1. Update Story 1.5 file to mark Tasks 3-5 complete
2. Add screenshots of Lighthouse reports
3. Document baseline FPS metrics
4. Story is ready for "done" status

**If Tests Fail:**
1. Document what's failing (FPS score, Lighthouse metrics)
2. Identify bottleneck (use Performance tab flame graph)
3. Fix issue (simplify animations, reduce parallax, etc.)
4. Re-test until all criteria met
5. Update story with findings

---

## Quick Reference Commands

```bash
# Start dev server
npm run dev

# Run Playwright tests
npx playwright test

# Build for production (test bundle size)
npm run build

# Check bundle size
du -sh dist/

# Open in browser
# Chrome: http://localhost:5173
# Firefox: http://localhost:5173
# Safari: http://localhost:5173
```

---

## Questions?

If anything is unclear or tests are failing in unexpected ways:
1. Check console for errors (F12 → Console tab)
2. Verify animations are running (should see "Desktop animations initialized" or "Mobile animations initialized")
3. Check FPS logs (should see "Performance: X FPS" every second)
4. Compare with expected behavior in Story 1.5 file
5. Document what you see vs. what you expect
