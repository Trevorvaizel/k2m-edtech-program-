# K2M EdTech Landing Page - Analytics Implementation Guide

**Document Version:** 1.0
**Last Updated:** 2026-01-15
**Status:** Implementation Plan Ready
**Related Story:** 0-2-implement-analytics-heatmap-tracking

---

## Executive Summary

This document provides the complete implementation guide for analytics tracking on the K2M EdTech landing page. We're using **Microsoft Clarity** (free, unlimited sessions) to measure the conversion metrics defined in Story 0.1.

**Why Analytics Matter:** Without analytics, we're building blind. Clarity enables us to measure scroll depth, click patterns, and drop-off points - data that informs optimization decisions.

**Platform Choice:** Microsoft Clarity (free, unlimited, lightweight) vs Hotjar (1,000 sessions/month limit)

---

## 1. Platform Selection: Microsoft Clarity

### 1.1 Decision: Use Microsoft Clarity

**Why Clarity Over Hotjar:**

| Feature | Microsoft Clarity | Hotjar (Free Tier) |
|---------|------------------|-------------------|
| **Cost** | Completely free | 1,000 sessions/month |
| **Heatmaps** | ✅ Excellent | ✅ Excellent |
| **Session Recordings** | ✅ Unlimited | ❌ Limited to 1,000 |
| **Performance** | Lightweight script | Heavier script |
| **Privacy Controls** | ✅ Good PII exclusion | ✅ Good controls |
| **Advanced Features** | Basic | More (polls, feedback) |

**Winner:** Microsoft Clarity - Unlimited sessions + better performance for our needs

### 1.2 Clarity Account Setup

**Action Items (When Ready to Implement):**
1. Go to https://clarity.microsoft.com/
2. Sign in with Microsoft account (create free account if needed)
3. Click "New Project"
4. Project name: "K2M Landing Page"
5. Website URL: [Add when landing page is live]
6. Click "Create Project"
7. Copy the tracking script (shown after project creation)

**Tracking Script Format:**
```html
<script type="text/javascript">
  (function(c,l,a,r,i,t,y){
      c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
      t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
  })(window, document, "clarity", "script", "YOUR_PROJECT_ID");
</script>
```

**Store Securely:**
- Save `YOUR_PROJECT_ID` in secure location (password manager or encrypted notes)
- **DO NOT** commit tracking ID to public repository (security risk)
- Document account credentials separately (email/password for Clarity dashboard)

---

## 2. Script Installation: index.html Setup

### 2.1 Add Clarity Script to `<head>`

**File:** `/index.html` (in project root, created during Epic 1)

**Location:** Inside `<head>` tag, before other scripts

**Implementation:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>K2M EdTech - From AI Confusion to Confidence</title>

    <!-- Microsoft Clarity Analytics -->
    <script type="text/javascript">
      (function(c,l,a,r,i,t,y){
          c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
          t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
          y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
      })(window, document, "clarity", "script", "YOUR_PROJECT_ID");
    </script>

    <!-- Other scripts and styles -->
    <!-- ... -->
</head>
<body>
    <!-- Landing page content -->
</body>
</html>
```

**Key Points:**
- ✅ Script is `async` (non-blocking)
- ✅ Placed in `<head>` (loads early)
- ✅ Replace `YOUR_PROJECT_ID` with actual project ID from Clarity dashboard
- ✅ Script loads from Clarity CDN (fast, reliable)

### 2.2 Verify Script Loads Correctly

**Testing Steps:**
1. Open landing page in browser (after Epic 1 implementation)
2. Open Chrome DevTools → Console
3. Type: `clarity`
4. Should see Clarity object (not `undefined`)
5. Check Network tab: Should see `clarity.ms` request
6. Open Clarity dashboard → Should see "Active now" user

**Expected Result:**
- ✅ Script loads without errors
- ✅ Console shows no warnings
- ✅ Clarity dashboard shows live user

---

## 3. Built-in Features: Scroll Depth, Heatmaps, Session Recordings

### 3.1 Scroll Depth Tracking (Automatic)

**Good News:** Clarity tracks scroll depth **automatically** - no custom code needed!

**Automatic Metrics:**
- Scroll depth to 25%, 50%, 75%, 100%
- Scroll depth heatmap shows where users stop
- "Scroll depth" dashboard shows distribution

**Viewing Scroll Data:**
1. Open Clarity dashboard
2. Click "Heatmaps" → "Scrolling"
3. See percentage of users who reach each depth
4. Identify drop-off points (where users leave)

**Testing:**
- Scroll through landing page (after Epic 3 completion)
- Wait 5-10 minutes for Clarity to process data
- Check dashboard: Should see scroll depth recorded

### 3.2 Click Heatmaps (Automatic)

**Good News:** Clarity tracks clicks **automatically** - no custom code needed!

**Automatic Metrics:**
- All clicks recorded (on buttons, links, text, images)
- Heatmap overlay shows hot/cold click zones
- "Dead clicks" show elements users click but nothing happens

**Viewing Click Heatmaps:**
1. Open Clarity dashboard
2. Click "Heatmaps" → "Click maps"
3. Select page (e.g., "Landing Page")
4. See heatmap overlay on page screenshot

**Testing:**
- Click various elements on landing page
- Wait 5-10 minutes for Clarity to process
- Check dashboard: Should see click heatmap

### 3.3 Session Recordings (Automatic, But Configurable)

**Good News:** Clarity records sessions **automatically** - no custom code needed!

**Recording Configuration:**
- **Default:** 100% of sessions recorded (recommended for launch)
- **Reduction:** Can reduce to 50%, 25%, 10% if needed (cost or privacy)
- **Exclusion:** Can exclude IP addresses (for team members)

**Configuring Recording Rate:**
1. Open Clarity dashboard
2. Click Settings (gear icon)
3. Project Settings → Recording
4. Adjust "Recording percentage" (100% → lower if needed)

**Viewing Session Recordings:**
1. Open Clarity dashboard
2. Click "Recordings"
3. Filter by date, device, browser
4. Watch recordings: See cursor movement, scrolls, clicks

**Testing:**
- Browse landing page for 2-3 minutes
- Wait 5-10 minutes for processing
- Check dashboard: Should see recording

---

## 4. Custom Event Tracking: CTA Button Events

### 4.1 Event Tracking Overview

**Why Custom Events?** Clarity's automatic tracking captures **what** users click, but not **why**. Custom events add semantic meaning:
- `cta_button_click` vs generic "click on button element"
- `map_zone_hover` vs generic "mouse movement"
- `map_entered_viewport` vs generic "scroll"

**Event Naming Convention:**
- `{section}_visible`: Element enters viewport (e.g., `cta_button_visible`)
- `{element}_{action}`: User interaction (e.g., `cta_button_hover`)
- `{section}_time_spent`: Duration tracking (e.g., `map_time_spent`)

### 4.2 Create Analytics Helper Module

**File:** `/src/utils/analytics.js` (create during Epic 1)

```javascript
/**
 * Analytics Helper Module
 * Provides functions to track custom events in Microsoft Clarity
 */

/**
 * Track CTA button visibility
 * Fires when CTA section enters viewport
 */
export function trackCTAVisible() {
  if (window.clarity) {
    window.clarity('event', 'cta_button_visible');
    console.log('📊 Analytics: CTA button visible');
  }
}

/**
 * Track CTA button hover
 * Fires when user hovers over CTA button
 */
export function trackCTAHover() {
  if (window.clarity) {
    window.clarity('event', 'cta_button_hover');
    console.log('📊 Analytics: CTA button hover');
  }
}

/**
 * Track CTA button click
 * Fires when user clicks CTA button
 */
export function trackCTAClick() {
  if (window.clarity) {
    window.clarity('event', 'cta_button_click');
    console.log('📊 Analytics: CTA button clicked');
  }
}

/**
 * Track Typeform open
 * Fires when Typeform diagnostic loads
 */
export function trackTypeformOpened() {
  if (window.clarity) {
    window.clarity('event', 'typeform_opened');
    console.log('📊 Analytics: Typeform opened');
  }
}

/**
 * Track Map section visible
 * Fires when Territory Map enters viewport
 */
export function trackMapVisible() {
  if (window.clarity) {
    window.clarity('event', 'map_entered_viewport');
    console.log('📊 Analytics: Map section visible');
  }
}

/**
 * Track Map zone hover
 * @param {number} zoneNumber - Zone number (0-4)
 */
export function trackMapZoneHover(zoneNumber) {
  if (window.clarity) {
    window.clarity('event', 'map_zone_hover', `zone_${zoneNumber}`);
    console.log(`📊 Analytics: Map zone ${zoneNumber} hover`);
  }
}

/**
 * Track Time Spent in Map Section
 * @param {number} seconds - Duration in seconds
 */
export function trackMapTimeSpent(seconds) {
  if (window.clarity) {
    window.clarity('event', 'map_time_spent', `${seconds}s`);
    console.log(`📊 Analytics: Map time spent: ${seconds}s`);
  }
}
```

### 4.3 Integrate CTA Tracking (Epic 3 - Story 3.3/3.4)

**File:** `/src/components/CTA/CTA.js` (create during Epic 3)

```javascript
import { trackCTAVisible, trackCTAHover, trackCTAClick } from '../../utils/analytics.js';

/**
 * Initialize CTA Analytics Tracking
 * Call this when CTA component mounts
 */
export function initCTAAnalytics() {
  // Track CTA visibility when it enters viewport
  // Using GSAP ScrollTrigger (configured during Epic 1)
  const ctaSection = document.querySelector('.cta-section');

  if (ctaSection) {
    // Method 1: Use Intersection Observer (simpler)
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          trackCTAVisible();
          observer.unobserve(entry.target); // Track once
        }
      });
    }, { threshold: 0.5 }); // Fire when 50% visible

    observer.observe(ctaSection);

    // Method 2: Use GSAP ScrollTrigger (if already using ScrollTrigger)
    // ScrollTrigger.create({
    //   trigger: '.cta-section',
    //   start: 'top 80%',
    //   onEnter: () => trackCTAVisible(),
    //   once: true
    // });
  }

  // Track CTA button hover
  const ctaButton = document.querySelector('.cta-button');
  if (ctaButton) {
    ctaButton.addEventListener('mouseenter', () => {
      trackCTAHover();
    });
  }

  // Track CTA button click
  if (ctaButton) {
    ctaButton.addEventListener('click', () => {
      trackCTAClick();
    });
  }
}
```

### 4.4 Track Typeform Open

**File:** `/src/components/CTA/CTA.js` (Epic 3)

```javascript
import { trackTypeformOpened } from '../../utils/analytics.js';

// If Typeform is embedded (iframe/modal):
const typeformEmbed = document.querySelector('#typeform-embed');
if (typeformEmbed) {
  typeformEmbed.addEventListener('load', () => {
    trackTypeformOpened();
  });
}

// If Typeform is external link (more likely):
const ctaButton = document.querySelector('.cta-button');
if (ctaButton) {
  ctaButton.addEventListener('click', () => {
    // Track click first
    trackCTAClick();

    // Then track Typeform open after short delay
    setTimeout(() => {
      trackTypeformOpened();
    }, 100);
  });
}
```

### 4.5 Testing CTA Events

**Test Steps:**
1. Implement CTA tracking code (after Epic 3)
2. Open landing page in browser
3. Open Chrome DevTools → Console
4. Scroll to CTA section → Should see: `📊 Analytics: CTA button visible`
5. Hover over CTA button → Should see: `📊 Analytics: CTA button hover`
6. Click CTA button → Should see: `📊 Analytics: CTA button clicked`
7. Open Clarity dashboard → Custom Events → Should see events

**Verification:**
- ✅ All events fire in correct order
- ✅ Console shows tracking logs
- ✅ Clarity dashboard shows events under "Custom Events"

---

## 5. Custom Event Tracking: Territory Map Events

### 5.1 Map Tracking Overview

**Territory Map Events:**
- `map_entered_viewport`: Map section becomes visible
- `map_zone_hover`: User hovers over zone (0-4)
- `map_time_spent`: Duration spent in map section

### 5.2 Integrate Map Tracking (Epic 2 - Story 2.1/2.3)

**File:** `/src/components/TerritoryMap/TerritoryMap.js` (create during Epic 2)

```javascript
import { trackMapVisible, trackMapZoneHover, trackMapTimeSpent } from '../../utils/analytics.js';

let mapStartTime = null;

/**
 * Initialize Map Analytics Tracking
 * Call this when Map component mounts
 */
export function initMapAnalytics() {
  // Track Map visibility when it enters viewport
  const mapSection = document.querySelector('.map-section');

  if (mapSection) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          trackMapVisible();

          // Start time tracking
          mapStartTime = Date.now();

          observer.unobserve(entry.target); // Track once
        }
      });
    }, { threshold: 0.5 });

    observer.observe(mapSection);
  }

  // Track Zone hover events
  const zones = document.querySelectorAll('.map-zone');
  zones.forEach((zone, index) => {
    zone.addEventListener('mouseenter', () => {
      trackMapZoneHover(index);
    });
  });

  // Track Time Spent when user leaves map section
  if (mapSection) {
    const exitObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting && mapStartTime) {
          // Calculate time spent
          const timeSpentSeconds = Math.round((Date.now() - mapStartTime) / 1000);
          trackMapTimeSpent(timeSpentSeconds);

          // Reset timer
          mapStartTime = null;
        }
      });
    }, { threshold: 0 });

    exitObserver.observe(mapSection);
  }
}
```

### 5.3 Testing Map Events

**Test Steps:**
1. Implement Map tracking code (after Epic 2)
2. Open landing page in browser
3. Open Chrome DevTools → Console
4. Scroll to Map section → Should see: `📊 Analytics: Map section visible`
5. Hover over Zone 0 → Should see: `📊 Analytics: Map zone 0 hover`
6. Hover over Zones 1-4 → Should see zone numbers
7. Scroll away from Map → Should see: `📊 Analytics: Map time spent: Xs`
8. Open Clarity dashboard → Custom Events → Should see all events

**Verification:**
- ✅ All zone hover events track correctly (0-4)
- ✅ Time spent calculates accurately
- ✅ Clarity dashboard shows map engagement data

---

## 6. Privacy & GDPR Compliance

### 6.1 No PII Collection

**Clarity Privacy Settings:**
1. Open Clarity dashboard
2. Click Settings (gear icon)
3. Privacy → Masking
4. Enable:
   - ✅ Mask all text elements (default)
   - ✅ Exclude numeric input (default)
   - ✅ Mask email addresses
   - ✅ Mask credit card numbers

**What Gets Masked:**
- User input fields (emails, names)
- Numeric inputs (phone, credit card)
- Sensitive text content

**What Gets Tracked:**
- Clicks, scrolls, cursor movement (safe)
- Page views, session duration (safe)
- Custom events (safe - no PII)

### 6.2 GDPR Compliance (If Targeting EU)

**Kenya Context:** GDPR **not required** for Kenyan market only

**Global Users:** If targeting EU users, implement cookie consent:

**Cookie Consent Banner (Optional):**
```html
<!-- Add to index.html if targeting EU users -->
<div id="cookie-consent" style="display: none; position: fixed; bottom: 0; background: #000; padding: 1rem; width: 100%; z-index: 1000;">
  <p>We use analytics to improve your experience. By continuing, you agree to our <a href="/privacy">Privacy Policy</a>.</p>
  <button onclick="acceptCookies()">Accept</button>
</div>

<script>
function acceptCookies() {
  localStorage.setItem('cookies-accepted', 'true');
  document.getElementById('cookie-consent').style.display = 'none';
}

// Show banner if not accepted
if (!localStorage.getItem('cookies-accepted')) {
  document.getElementById('cookie-consent').style.display = 'block';
}
</script>
```

**Recommendation:** Skip for now (Kenya market only). Add later if expanding globally.

### 6.3 Data Retention

**Clarity Default:** 30 days (adjustable)

**Changing Retention:**
1. Clarity dashboard → Settings
2. Project Settings → Data management
3. Adjust "Data retention period" (30 days default)
4. Options: 7 days, 30 days, 90 days, 180 days

**Recommendation:** Keep 30 days (sufficient for optimization cycles)

---

## 7. Performance Testing

### 7.1 Lighthouse Audit with Analytics

**Test Steps (After Epic 1 Implementation):**
1. Open landing page in Chrome
2. Open DevTools → Lighthouse
3. Run Lighthouse audit (Performance mode)
4. Verify metrics:
   - Performance score: **> 90** ✅
   - FCP: **< 1.5s** ✅
   - TTI: **< 3.5s** ✅
   - No blocking scripts detected

**If Score < 90:**
- Check: Is Clarity script `async`? (yes → good)
- Check: Is script in `<head>` or `<body>`? (head = better)
- Check: Are other scripts blocking?
- Solution: Defer non-critical scripts

### 7.2 Async Loading Verification

**Test Steps:**
1. Open DevTools → Network tab
2. Reload landing page
3. Find `clarity.ms` request
4. Check: Does it have "(from disk cache)" or status 200?
5. Check: Is timing in "waterfall" non-blocking?

**Expected Result:**
- ✅ Clarity script loads asynchronously (doesn't block FCP)
- ✅ Page renders before Clarity finishes loading
- ✅ No "block main thread" warnings

### 7.3 Mobile Performance Testing

**Test Steps:**
1. Open Chrome DevTools → Device Toolbar (Ctrl+Shift+M)
2. Select device: iPhone 12 Pro or Galaxy S21
3. Enable: "Network throttling" → Fast 3G
4. Reload landing page
5. Run Lighthouse audit
6. Verify: Performance score > 85 (mobile), FCP < 2s

**Target:**
- Desktop: 60fps maintained with analytics
- Mobile: 45fps+ maintained with analytics

---

## 8. Clarity Dashboard Setup

### 8.1 Custom Events Dashboard

**Viewing Custom Events:**
1. Open Clarity dashboard
2. Click "Custom Events" (left sidebar)
3. See all tracked events:
   - `cta_button_visible`
   - `cta_button_hover`
   - `cta_button_click`
   - `typeform_opened`
   - `map_entered_viewport`
   - `map_zone_hover`
   - `map_time_spent`

**Event Details:**
- **Count:** How many times event fired
- **Users:** Unique users who triggered event
- **Trend:** Line graph over time
- **Funnel:** Conversion from visible → click (for CTA)

### 8.2 Key Metrics Dashboard

**Link to Story 0.1 Metrics:**

| Story 0.1 Metric | Clarity Measurement |
|------------------|---------------------|
| CTA click rate | `cta_button_click` / unique visitors |
| Scroll depth 80% | Heatmaps → Scrolling (at 80% mark) |
| Time on page 90s | Session recordings → Average duration |
| Map zone identification | `map_zone_hover` events (zones 0-4) |

**Dashboard Configuration:**
1. Clarity dashboard → "Dashboards"
2. Create custom dashboard: "K2M Conversion Metrics"
3. Add widgets:
   - Custom Events: `cta_button_click` (count, trend)
   - Heatmaps: Scroll depth distribution
   - Recordings: Filter by CTA clickers
   - Funnel: CTA visible → hover → click

---

## 9. Implementation Timeline

### 9.1 When to Implement Each Task

| Task | Implement During Epic | Reason |
|------|----------------------|--------|
| **Task 1:** Set up Clarity account | **Now** (foundation) | Get tracking ID ready |
| **Task 2:** Install script in index.html | Epic 1, Story 1.1 | Add during project initialization |
| **Task 3:** Scroll depth tracking | **Automatic** | Clarity handles automatically |
| **Task 4:** Heatmaps & recordings | **Automatic** | Clarity handles automatically |
| **Task 5:** CTA event tracking | Epic 3, Story 3.3/3.4 | Add when CTA section built |
| **Task 6:** Map event tracking | Epic 2, Story 2.1/2.3 | Add when Map section built |
| **Task 7:** Privacy & GDPR | **Now** (configure) | Set up privacy settings |
| **Task 8:** Performance testing | Epic 1, Story 1.5 | Test after Hero complete |
| **Task 9:** Document analytics | **This document** | ✅ Complete |

### 9.2 Immediate Action Items (Before Epic 1)

**Do Now:**
- ✅ Create Microsoft Clarity account
- ✅ Generate tracking script and project ID
- ✅ Store project ID securely (password manager)
- ✅ Configure privacy settings (mask PII)
- ✅ Review Clarity dashboard features

**Do During Epic 1 (Project Setup):**
- Add Clarity script to `index.html` `<head>`
- Create `/src/utils/analytics.js` helper module
- Test script loads without blocking
- Run Lighthouse audit (verify > 90 score)

**Do During Epic 2 (Map Implementation):**
- Integrate map event tracking (`map_entered_viewport`, `map_zone_hover`, `map_time_spent`)
- Test map events fire correctly
- Verify Clarity dashboard shows map data

**Do During Epic 3 (CTA Implementation):**
- Integrate CTA event tracking (`cta_button_visible`, `cta_button_hover`, `cta_button_click`, `typeform_opened`)
- Test CTA events fire correctly
- Verify Clarity dashboard shows CTA funnel

---

## 10. Testing Checklist

### 10.1 Desktop Testing

After Epic 3 completion (full landing page):

- [ ] **Script Loads Correctly**
  - [ ] Open DevTools → Console → Type `clarity` → Should return object (not undefined)
  - [ ] DevTools → Network → Should see `clarity.ms` request
  - [ ] No console errors related to Clarity

- [ ] **Scroll Depth Works**
  - [ ] Scroll to 25%, 50%, 75%, 100% of page
  - [ ] Wait 10 minutes
  - [ ] Check Clarity dashboard → Heatmaps → Scrolling → Should see distribution

- [ ] **Click Heatmaps Work**
  - [ ] Click various elements (buttons, links, text)
  - [ ] Wait 10 minutes
  - [ ] Check Clarity dashboard → Heatmaps → Click maps → Should see heatmap

- [ ] **Session Recordings Work**
  - [ ] Browse page for 2-3 minutes
  - [ ] Wait 10 minutes
  - [ ] Check Clarity dashboard → Recordings → Should see session

- [ ] **CTA Events Work**
  - [ ] Scroll to CTA → Console: "📊 Analytics: CTA button visible"
  - [ ] Hover CTA button → Console: "📊 Analytics: CTA button hover"
  - [ ] Click CTA button → Console: "📊 Analytics: CTA button clicked"
  - [ ] Check Clarity → Custom Events → Should see all 3 events

- [ ] **Map Events Work**
  - [ ] Scroll to Map → Console: "📊 Analytics: Map section visible"
  - [ ] Hover Zone 0 → Console: "📊 Analytics: Map zone 0 hover"
  - [ ] Hover Zones 1-4 → Console shows zone numbers
  - [ ] Scroll away → Console: "📊 Analytics: Map time spent: Xs"
  - [ ] Check Clarity → Custom Events → Should see all events

### 10.2 Mobile Testing

Test on real device or Chrome DevTools device emulation:

- [ ] **Script Loads on Mobile**
  - [ ] Open on iPhone or Android
  - [ ] DevTools → Remote Debugging → Console → Type `clarity` → Should work
  - [ ] Check Clarity dashboard → Should see mobile session

- [ ] **Performance Maintained**
  - [ ] Run Lighthouse mobile audit
  - [ ] Performance score: **> 85** ✅
  - [ ] FCP: **< 2s** ✅
  - [ ] No blocking scripts

- [ ] **Touch Events Work**
  - [ ] Tap CTA button → Should track hover/click (touch devices treat tap as both)
  - [ ] Touch Map zones → Should track hover
  - [ ] Check Clarity → Should see mobile events

---

## 11. Troubleshooting

### 11.1 Common Issues

**Issue:** Clarity script doesn't load
- **Cause:** Script not added to `<head>` or missing `async` attribute
- **Fix:** Check `index.html` has script in `<head>` with `async` attribute

**Issue:** Custom events not appearing in dashboard
- **Cause:** Events firing before Clarity loads, or `window.clarity` undefined
- **Fix:** Add `if (window.clarity)` check in analytics helper functions

**Issue:** Events firing multiple times
- **Cause:** Event listeners not cleaned up, or multiple observers
- **Fix:** Use `observer.unobserve()` after tracking once, or `once: true` in ScrollTrigger

**Issue:** Lighthouse score dropped after adding Clarity
- **Cause:** Script blocking main thread (missing `async`)
- **Fix:** Ensure script has `async` attribute, or move to bottom of `<body>`

**Issue:** Heatmaps not showing data
- **Cause:** Not enough data yet (needs 5-10+ sessions)
- **Fix:** Wait 24-48 hours, or test more extensively yourself

### 11.2 Debug Mode

**Enable Verbose Logging:**
```javascript
// In analytics.js, add debug mode
const DEBUG = true; // Set to false in production

export function trackCTAClick() {
  if (window.clarity) {
    window.clarity('event', 'cta_button_click');
    if (DEBUG) console.log('📊 Analytics: CTA button clicked');
  } else if (DEBUG) {
    console.warn('⚠️ Analytics: Clarity not loaded');
  }
}
```

---

## 12. Success Criteria

### 12.1 Technical Success (Story 0.2 AC)

All acceptance criteria met:

- [ ] **AC #1:** Microsoft Clarity installed ✅
  - [ ] Scroll depth tracking enabled (automatic)
  - [ ] Click heatmaps recording (automatic)
  - [ ] Session recordings enabled

- [ ] **AC #2:** CTA events tracked ✅
  - [ ] `cta_button_visible`
  - [ ] `cta_button_hover`
  - [ ] `cta_button_click`
  - [ ] `typeform_opened`

- [ ] **AC #3:** Map events tracked ✅
  - [ ] `map_entered_viewport`
  - [ ] `map_zone_hover`
  - [ ] `map_time_spent`

- [ ] **AC #4:** Privacy respected ✅
  - [ ] No PII collected (masking enabled)
  - [ ] GDPR consent if needed
  - [ ] Script loads asynchronously (non-blocking)

### 12.2 Business Success (Story 0.1 Metrics)

After 4 weeks of launch:

- [ ] **Primary Metric:** CTA click rate > 15%
- [ ] **Secondary:** Scroll depth 80%, Time on page 90s, Diagnostic completion 70%
- [ ] **Performance:** Lighthouse > 90, FCP < 1.5s, 60fps/45fps
- [ ] **Emotional:** 4/5 users feel validated, identify zone, feel belonging, feel invited

---

## 13. Summary

### What's Been Documented

✅ **Platform Selection:** Microsoft Clarity (free, unlimited, lightweight)
✅ **Account Setup:** Step-by-step Clarity account creation
✅ **Script Installation:** Add to `<head>` in `index.html` (async)
✅ **Built-in Features:** Scroll depth, heatmaps, recordings (automatic)
✅ **CTA Tracking:** 4 events (visible, hover, click, typeform_opened)
✅ **Map Tracking:** 3 events (visible, zone hover, time spent)
✅ **Privacy Compliance:** No PII, GDPR optional (Kenya doesn't require)
✅ **Performance Testing:** Lighthouse > 90, async loading verification
✅ **Dashboard Setup:** Custom events dashboard, metrics linking
✅ **Implementation Timeline:** What to do when (Now, Epic 1, Epic 2, Epic 3)
✅ **Testing Checklist:** Desktop and mobile verification
✅ **Troubleshooting:** Common issues and fixes

### Next Steps

1. ✅ **Story 0.2 Complete** - This implementation guide is ready
2. **Immediate Action:** Create Clarity account, get tracking ID
3. **Epic 1:** Add script to `index.html`, create `analytics.js`
4. **Epic 2:** Integrate Map tracking events
5. **Epic 3:** Integrate CTA tracking events
6. **Launch:** Monitor Clarity dashboard, optimize based on data

---

**Document Status:** ✅ Implementation plan complete, ready for Epic 1-3 execution
**Maintained By:** Product Owner (Trevor) + Dev Agent (implementation)
**Related Documents:** conversion-metrics.md (Story 0.1), user-testing-protocol.md (Story 0.3)
