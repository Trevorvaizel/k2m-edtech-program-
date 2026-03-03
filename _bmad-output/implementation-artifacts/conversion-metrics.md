# K2M EdTech Landing Page - Conversion Metrics & Success Criteria

**Document Version:** 1.0
**Last Updated:** 2026-01-15
**Status:** Baseline Established
**Related Story:** 0-1-define-conversion-baseline-success-metrics

---

## Executive Summary

This document defines the conversion baseline and success metrics for the K2M EdTech Awwwards-Level Landing Page. Our objective is to build a landing page that **converts visitors to diagnostic completers**, not just to win design awards. Every pixel built must serve these conversion goals.

**Primary Success Metric:** Diagnostic form click rate > 15% of visitors

---

## 1. Primary Conversion Metric

### Diagnostic Form Click Rate
- **Target:** > 15% of unique visitors
- **Measurement:** Number of unique visitors who click "Begin Your Journey" CTA button / Total unique visitors
- **Baseline:** 0% (page doesn't exist yet)
- **Stretch Goal:** 20%+ (exceptional conversion)
- **Minimum Viable:** 10% (page is working, needs optimization)
- **Failure Threshold:** < 5% (major redesign needed)

#### Measurement Methodology
- **Tool:** Microsoft Clarity (Story 0.2 will implement)
- **Event Tracking:** `cta_button_click` event fires on CTA button click
- **Calculation:** `unique_clicks / unique_visitors * 100`
- **Reporting:** Dashboard shows conversion rate with trend line (daily, weekly, monthly)

#### Why This Metric Matters
The CTA click is the **make-or-break moment** for the landing page. If users don't click, the page fails regardless of how pretty it is. This metric directly measures business impact: diagnostic completions = potential cohort enrollments.

#### Success Indicators
- ✅ **Success:** > 15% click rate sustained for 2 weeks after launch
- ⚠️ **Caution:** 10-15% click rate (optimize, not rebuild)
- ❌ **Failure:** < 10% click rate for 4+ weeks (major iteration needed)

---

## 2. Secondary Conversion Metrics

### 2.1 Scroll Depth to CTA Section
- **Target:** > 80% of visitors reach CTA section
- **Measurement:** Scroll depth tracking at CTA section viewport entry
- **Baseline:** 0% (page doesn't exist yet)
- **Stretch Goal:** 90%+ (nearly everyone sees the CTA)
- **Minimum Viable:** 70% (majority see the CTA)
- **Failure Threshold:** < 50% (half drop off before CTA)

#### Measurement Methodology
- **Tool:** Microsoft Clarity scroll depth heatmap
- **Event Tracking:** `cta_button_visible` event when CTA section enters viewport
- **Reporting:** Funnel visualization showing drop-off at each section

#### Why This Metric Matters
If users don't scroll to the CTA, they can't click it. This metric identifies **content engagement** and **scroll friction**. Low scroll depth indicates:
- Content is not engaging
- Page is too long
- Technical issues (slow load, broken scroll)
- Wrong audience targeting

#### Success Indicators
- ✅ **Success:** > 80% scroll depth sustained
- ⚠️ **Caution:** 70-80% (identify drop-off sections)
- ❌ **Failure:** < 70% (analyze where users drop off)

### 2.2 Time on Page
- **Target:** > 90 seconds (enough time to read all 326 words)
- **Measurement:** Average session duration
- **Baseline:** 0 seconds (page doesn't exist yet)
- **Stretch Goal:** 120+ seconds (deep engagement)
- **Minimum Viable:** 60 seconds (skimmed content)
- **Failure Threshold:** < 30 seconds (bounce, no engagement)

#### Measurement Methodology
- **Tool:** Microsoft Clarity session recordings + analytics
- **Calculation:** Average time from page load to page exit
- **Reporting:** Distribution graph (30s, 60s, 90s, 120s+)

#### Why This Metric Matters
Time on page indicates **content consumption** and **emotional resonance**. If users stay > 90 seconds, they're reading the copy, not just skimming. This validates the "You're not alone" emotional connection.

#### Success Indicators
- ✅ **Success:** > 90s average time on page
- ⚠️ **Caution:** 60-90s (some engagement, but not deep)
- ❌ **Failure:** < 60s (content not resonating)

### 2.3 Diagnostic Completion Rate
- **Target:** > 70% of those who start diagnostic complete it
- **Measurement:** Typeform completion rate (diagnostic start → finish)
- **Baseline:** N/A (Typeform not launched yet)
- **Stretch Goal:** 80%+ (compelling diagnostic experience)
- **Minimum Viable:** 60% (acceptable, but can improve)
- **Failure Threshold:** < 50% (diagnostic too long/complex)

#### Measurement Methodology
- **Tool:** Typeform analytics dashboard
- **Calculation:** `completions / starts * 100`
- **Reporting:** Conversion funnel showing drop-off points in diagnostic

#### Why This Metric Matters
This measures **diagnostic quality** and **user motivation**. High completion rate indicates:
- Diagnostic length is appropriate (~15 minutes as stated)
- Questions are relevant and engaging
- User understands the value (job prospects, AI skills)
- Technical issues don't block completion

#### Success Indicators
- ✅ **Success:** > 70% completion rate
- ⚠️ **Caution:** 60-70% (optimize diagnostic questions)
- ❌ **Failure:** < 60% (diagnostic needs major work)

---

## 3. Performance Metrics

### 3.1 Lighthouse Performance Score
- **Target:** > 90 (green rating)
- **Measurement:** Google Lighthouse audit (Performance category)
- **Baseline:** N/A (page not built yet)
- **Stretch Goal:** 95+ (exceptional performance)
- **Minimum Viable:** 85 (acceptable, yellow rating)
- **Failure Threshold:** < 80 (red rating, major issues)

#### Measurement Methodology
- **Tool:** Google Lighthouse (Chrome DevTools or PageSpeed Insights)
- **Frequency:** Run Lighthouse after each Epic completion (1, 2, 3)
- **Reporting:** Score trends over time + specific metric breakdown (FCP, LCP, TTI)

#### Why This Metric Matters
Lighthouse score predicts **user experience** and **SEO ranking**. Low performance = frustrated users = lower conversion. This is especially critical for:
- Mobile users (slow devices, 3G connections)
- Kenyan market (variable internet speeds)
- Animation-heavy page (GSAP, Lenis, particles)

#### Success Indicators
- ✅ **Success:** > 90 Lighthouse Performance score
- ⚠️ **Caution:** 85-90 (optimize animations, images)
- ❌ **Failure:** < 85 (major performance work needed)

### 3.2 First Contentful Paint (FCP)
- **Target:** < 1.5 seconds
- **Measurement:** Lighthouse "First Contentful Paint" metric
- **Baseline:** N/A (page not built yet)
- **Stretch Goal:** < 1.0s (instant feel)
- **Minimum Viable:** < 2.0s (acceptable but sluggish)
- **Failure Threshold:** > 2.5s (feels broken)

#### Measurement Methodology
- **Tool:** Google Lighthouse (Performance section)
- **Definition:** Time from navigation to first text/image rendered
- **Reporting:** FCP score distribution (fast < 1s, moderate 1-2.5s, slow > 2.5s)

#### Why This Metric Matters
FCP is the **first impression** metric. If users see a blank screen for > 2 seconds, they bounce. Fast FCP creates immediate trust and engagement.

#### Success Indicators
- ✅ **Success:** FCP < 1.5s on 3G connection
- ⚠️ **Caution:** FCP 1.5-2.0s (optimize critical CSS)
- ❌ **Failure:** FCP > 2.0s (page feels broken)

### 3.3 Frames Per Second (FPS)
- **Target Desktop:** 60fps consistent
- **Target Mobile:** 45fps+ consistent
- **Measurement:** FPS monitoring during animations (particle system, scroll)
- **Baseline:** N/A (page not built yet)
- **Stretch Goal:** 60fps mobile (smooth everywhere)
- **Minimum Viable:** 45fps desktop / 30fps mobile (acceptable jank)
- **Failure Threshold:** < 30fps (animations stutter, feels broken)

#### Measurement Methodology
- **Tool:** Chrome DevTools Performance monitor (FPS meter)
- **Frequency:** Test after each Epic (Hero animations, Map particles, Discord bubbles)
- **Reporting:** FPS graph over time, identifying jank points

#### Why This Metric Matters
FPS measures **animation quality** and **luxurious feel**. The "WHOA moment" (particle coalescence) fails if animations stutter. Low FPS = cheap feel = lower conversion.

#### Success Indicators
- ✅ **Success:** 60fps desktop / 45fps+ mobile
- ⚠️ **Caution:** 45fps desktop / 30fps mobile (acceptable jank)
- ❌ **Failure:** < 30fps (animations broken)

---

## 4. Emotional Success Criteria (Qualitative Metrics)

### 4.1 Hero Section: "Seen" or "Validated"
**Target Emotional Response:** User reports feeling "seen," "understood," or "this is about me"

#### Measurement Methodology
- **Tool:** User testing (Story 0.3 protocol)
- **Question:** "How does this opening make you feel?"
- **Target Verbatim:** "That's me," "I feel seen," "They understand my struggle," "Not alone"

#### Success Indicators
- ✅ **Success:** 4/5 users report feeling "seen" or "validated"
- ⚠️ **Caution:** 3/5 users (emotional connection weak)
- ❌ **Failure:** < 3/5 users (Hero section not resonating)

### 4.2 Territory Map: Identify Current Zone (0-4)
**Target Emotional Response:** User can clearly identify their current position on the learning journey

#### Measurement Methodology
- **Tool:** User testing (Story 0.3 protocol)
- **Question:** "Which zone do you think you're in? Why?"
- **Target Behavior:** User points to specific zone (0, 1, 2, 3, or 4) and explains reasoning

#### Success Indicators
- ✅ **Success:** 4/5 users can identify their zone with confidence
- ⚠️ **Caution:** 3/5 users (map needs better explanation)
- ❌ **Failure:** < 3/5 users (map confusing or unclear)

### 4.3 Discord Section: "Belonging" or "Community"
**Target Emotional Response:** User feels they would belong to this community

#### Measurement Methodology
- **Tool:** User testing (Story 0.3 protocol)
- **Question:** "Would you want to join this community?"
- **Target Verbatim:** "Yes," "These are my people," "I'd fit in," "Looks supportive"

#### Success Indicators
- ✅ **Success:** 4/5 users say "yes" to joining community
- ⚠️ **Caution:** 3/5 users (community preview weak)
- ❌ **Failure:** < 3/5 users (not feeling belonging)

### 4.4 CTA Section: "Relief" Not "Pressure"
**Target Emotional Response:** User feels invited, not pressured or desperate

#### Measurement Methodology
- **Tool:** User testing (Story 0.3 protocol)
- **Question:** "Does this feel like pressure or an invitation?"
- **Target Verbatim:** "Invitation," "Low pressure," "I can try this," "Not forced"

#### Success Indicators
- ✅ **Success:** 4/5 users report feeling "invited" not "pressured"
- ⚠️ **Caution:** 3/5 users (tone needs adjustment)
- ❌ **Failure:** < 3/5 users (feels salesy or desperate)

---

## 5. Metrics Tracking Plan

### 5.1 Measurement Tools
| Metric | Tool | Implementation Story |
|--------|------|---------------------|
| CTA click rate | Microsoft Clarity | Story 0.2 |
| Scroll depth | Microsoft Clarity heatmap | Story 0.2 |
| Time on page | Microsoft Clarity analytics | Story 0.2 |
| Diagnostic completion | Typeform analytics | Story 3.3 |
| Lighthouse score | Google Lighthouse | Story 1.5 |
| FCP | Google Lighthouse | Story 1.5 |
| FPS | Chrome DevTools | Story 1.5, 2.2 |
| Emotional response | User testing (Story 0.3) | Story 0.3 |

### 5.2 Post-Launch Review Cadence
- **Week 1-4:** Daily review of conversion metrics (primary focus: CTA click rate)
- **Month 2:** Weekly review (stabilization period)
- **Month 3+:** Monthly review (ongoing optimization)

**Review Questions:**
1. Is CTA click rate > 15%? If no, what's blocking?
2. Is scroll depth > 80%? If no, where do users drop off?
3. Is time on page > 90s? If no, is content not resonating?
4. Is diagnostic completion > 70%? If no, is diagnostic too long?
5. Are emotional criteria met (user testing)? If no, what's missing?

### 5.3 Decision Framework: Iterate vs Rebuild

#### When to ITERATE (Optimization)
- CTA click rate: 10-15% (close to target)
- Scroll depth: 70-80% (minor friction points)
- Time on page: 60-90s (content needs polish)
- Lighthouse score: 85-90 (minor optimizations)
- Emotional criteria: 3/5 users (tone adjustments)

**Iteration Actions:**
- A/B test CTA button copy/color
- Optimize animations for performance
- Refine copy for clarity
- Improve mobile responsiveness
- Add testimonials/social proof

#### When to REBUILD (Major Changes)
- CTA click rate: < 10% (fundamental issue)
- Scroll depth: < 70% (major content/structure problem)
- Time on page: < 60s (not resonating at all)
- Lighthouse score: < 85 (technical debt)
- Emotional criteria: < 3/5 users (wrong emotional approach)

**Rebuild Actions:**
- Rethink value proposition
- Restructure content flow
- Redesign key sections (Hero, Map, CTA)
- New copy direction
- Different emotional hook

### 5.4 Success vs Failure Indicators

#### SUCCESS 🎉 (Launch + 4 Weeks)
- **Primary Metric:** CTA click rate > 15% ✅
- **Secondary Metrics:**
  - Scroll depth > 80% ✅
  - Time on page > 90s ✅
  - Diagnostic completion > 70% ✅
- **Performance:** Lighthouse > 90, FCP < 1.5s, 60fps desktop / 45fps mobile ✅
- **Emotional:** 4/5 users feel validated, can identify zone, feel belonging, feel invited ✅

**Result:** Page is converting. Move to scaling (traffic, paid ads, SEO).

#### CAUTION ⚠️ (Launch + 4 Weeks)
- **Primary Metric:** CTA click rate 10-15% (close)
- **Secondary Metrics:** Mixed (some hit, some miss)
- **Performance:** Lighthouse 85-90 (acceptable)
- **Emotional:** 3/5 users meet criteria

**Result:** Page is working but needs optimization. Run 2-4 week iteration sprint focused on weakest metric.

#### FAILURE ❌ (Launch + 4 Weeks)
- **Primary Metric:** CTA click rate < 10% (not converting)
- **Secondary Metrics:** Most miss targets
- **Performance:** Lighthouse < 85 (technical issues)
- **Emotional:** < 3/5 users (not resonating)

**Result:** Page is not working. Major rebuild needed. Revisit PRD, talk to users, pivot approach.

### 5.5 Minimum Viable Conversion Rate

**Definition:** "What's the lowest conversion rate before we say the page is 'working'?"

- **Minimum Viable:** 10% CTA click rate sustained for 4 weeks
- **Rationale:** 10% = 1 in 10 visitors convert. For 1,000 visitors/month → 100 diagnostic starts → 70 completions (70% rate) → ~10-14 cohort enrollments (15-20% conversion from diagnostic to cohort).

**Below 10%:** Page is not working. Major iteration or rebuild needed.

---

## 6. Integration with Epic 1-4

### 6.1 Story 0.2: Analytics Implementation
- Story 0.1 **defines** these metrics (this document)
- Story 0.2 **implements** tracking for these metrics (Microsoft Clarity setup)
- **Dependency:** Story 0.2 cannot be completed without these metrics defined

**Cross-Reference:**
- CTA click events → Story 0.2 Task 5 (CTA button event tracking)
- Map engagement events → Story 0.2 Task 6 (Territory Map engagement tracking)
- Scroll depth tracking → Story 0.2 Task 3 (Configure scroll depth milestones)

### 6.2 Epic 1: Foundation & Hero Experience
**Performance Metrics Alignment:**
- Lighthouse > 90 → Story 1.5 (Optimize Hero Performance)
- FCP < 1.5s → Story 1.5 (First Contentful Paint target)
- 60fps desktop / 45fps mobile → Story 1.5 (FPS targets)

**Emotional Criteria Alignment:**
- Hero: "seen/validated" → Story 1.3 (Hero copy) and Story 1.4 (Hero text reveal animations)

### 6.3 Epic 2: Territory Map WHOA Moment
**Emotional Criteria Alignment:**
- Map: identify zone (0-4) → Story 2.1 (Territory Map SVG structure) and Story 2.3 (Zone illumination)

**Performance Metrics Alignment:**
- 60fps desktop / 45fps mobile → Story 2.2 (Particle coalescence system) - critical due to 200 desktop particles / 50 mobile particles

### 6.4 Epic 3: Community Preview & Conversion
**Primary Metric Alignment:**
- CTA click rate > 15% → Story 3.3 (CTA section with Typeform integration)

**Emotional Criteria Alignment:**
- Discord: "belonging" → Story 3.1 (Discord preview section) and Story 3.2 (Chat bubble animations)
- CTA: "relief not pressure" → Story 3.3 (CTA copy and positioning)

### 6.5 Story 0.3: User Testing Protocol
- Story 0.1 **defines** emotional success criteria
- Story 0.3 **implements** testing to validate emotional response
- **Dependency:** Story 0.3 uses these criteria for testing questions

**Cross-Reference:**
- Hero "seen/validated" → Story 0.3 Task 2 (section-specific validation questions)
- Map zone identification → Story 0.3 Task 2 (Map question)
- Discord belonging → Story 0.3 Task 2 (Discord question)
- CTA relief not pressure → Story 0.3 Task 2 (CTA question)

---

## 7. Dependencies and Sequence

### Prerequisite Stories (Must Complete First)
- **Story 0.1** (this story): Define conversion baseline and success metrics ✅ YOU ARE HERE

### Dependent Stories (Require This Story First)
- **Story 0.2:** Implement analytics and heatmap tracking (needs metrics to track)
- **Story 0.3:** Establish user testing protocol (needs emotional criteria to test)
- **Epic 1-4:** All implementation stories must align with these metrics

### Recommended Execution Order
1. ✅ Story 0.1: Define conversion metrics (THIS STORY)
2. Story 0.2: Implement analytics tracking
3. Story 0.3: Define user testing protocol
4. Epic 1: Build Hero section (test emotional criteria after Epic 1)
5. Epic 2: Build Territory Map (test emotional criteria after Epic 2)
6. Epic 3: Build Discord & CTA (test emotional criteria after Epic 3 - final validation)
7. Epic 4: Graceful degradation & post-launch (use metrics for iteration decisions)

---

## 8. Baseline vs Stretch Goals

### Baseline Targets (Minimum Viable Product)
| Metric | Baseline | Rationale |
|--------|----------|-----------|
| CTA click rate | 15% | Industry standard for high-intent landing pages |
| Scroll depth | 80% | Majority should see the CTA |
| Time on page | 90s | Enough to read all 326 words |
| Diagnostic completion | 70% | Typeform benchmark for 15-min form |
| Lighthouse | 90 | Green rating, good UX |
| FCP | 1.5s | Feels fast |
| FPS desktop | 60fps | Smooth animations |
| FPS mobile | 45fps+ | Acceptable mobile performance |
| Emotional response | 4/5 users | Strong emotional connection |

### Stretch Goals (Exceptional Performance)
| Metric | Stretch Goal | Impact |
|--------|-------------|--------|
| CTA click rate | 20%+ | High-converting page, scale aggressively |
| Scroll depth | 90%+ | Nearly everyone sees CTA |
| Time on page | 120s+ | Deep engagement, highly resonant |
| Diagnostic completion | 80%+ | Compelling diagnostic experience |
| Lighthouse | 95+ | Exceptional performance, SEO superpower |
| FCP | 1.0s | Instant feel, competitive advantage |
| FPS mobile | 60fps | Luxurious feel even on mobile |
| Emotional response | 5/5 users | Perfect emotional resonance |

### Failure Thresholds (Major Rebuild Needed)
| Metric | Failure Threshold | Action |
|--------|------------------|--------|
| CTA click rate | < 10% | Rebuild: value prop, copy, CTA |
| Scroll depth | < 70% | Rebuild: content structure, length |
| Time on page | < 60s | Rebuild: emotional hook, copy |
| Diagnostic completion | < 60% | Rebuild: diagnostic questions, length |
| Lighthouse | < 85 | Rebuild: performance optimization |
| FCP | > 2.0s | Rebuild: critical CSS, loading strategy |
| FPS desktop | < 30fps | Rebuild: animation strategy |
| FPS mobile | < 30fps | Rebuild: particle count, effects |
| Emotional response | < 3/5 users | Rebuild: emotional approach |

---

## 9. Summary

### What Success Looks Like
After 4 weeks of launch, the K2M landing page is successful if:

1. **15%+ of visitors click "Begin Your Journey"** (primary metric)
2. **80%+ scroll to the CTA** (content engagement)
3. **90s+ average time on page** (reading all content)
4. **70%+ complete the diagnostic** (compelling offer)
5. **Lighthouse score > 90** (fast, polished)
6. **60fps desktop / 45fps mobile** (smooth animations)
7. **4/5 users report correct emotional responses** (validated, belonging, invited)

### What Failure Looks Like
After 4 weeks of launch, the page needs major rebuild if:

1. **< 10% CTA click rate** (not converting)
2. **< 70% scroll depth** (half drop off early)
3. **< 60s time on page** (not engaging)
4. **Lighthouse < 85** (technical issues)
5. **< 3/5 users feel correct emotions** (wrong approach)

### Next Steps
1. ✅ **Story 0.1 Complete** - This document establishes the baseline
2. **Story 0.2** - Install Microsoft Clarity to track these metrics
3. **Story 0.3** - Define user testing to validate emotional criteria
4. **Epic 1-3** - Build landing page aligned with these metrics
5. **Launch** - Measure real performance against baseline
6. **Week 1-4** - Daily review, optimize weakest metrics
7. **Decision Point** - Iterate (if close) or rebuild (if far)

---

**Document Status:** ✅ Baseline established, ready for implementation
**Next Review:** After Story 0.2 (analytics implementation) to validate tracking setup
**Owner:** Product Owner (Trevor)
**Maintained By:** Product Owner (update metrics as learnings emerge)
