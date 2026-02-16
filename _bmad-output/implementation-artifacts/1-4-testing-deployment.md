# Story 1.4: Testing + Deployment

**Epic:** Landing Page Forms Integration
**Story:** 1.4 - Testing + Deployment
**Status:** ready-for-dev
**Created:** 2026-02-16
**Purpose:** Comprehensive testing and production deployment of the diagnostic form system

---

## Story

As a **Quality Assurance Engineer**,
I want **comprehensive testing and smooth deployment of the diagnostic form system to production**,
so that **students can successfully apply to the cohort and Trevor receives accurate data in his workflow**.

---

## Acceptance Criteria

1. **Unit Tests Written** - All form validation logic tested with edge cases
2. **Integration Tests Pass** - Form submission → API → Google Sheets flow verified
3. **Mobile Testing Complete** - Form works on iPhone, Android, various screen sizes
4. **Security Audit Passed** - HTTPS, environment variables, input validation verified
5. **Production Deployment** - Frontend + backend deployed to Vercel
6. **Smoke Tests Pass** - End-to-end test confirms live system works

---

## Tasks / Subtasks

- [ ] **1. Write Unit Tests for Validation** (AC: #1)
  - [ ] 1.1 Test email validation (valid, invalid, edge cases)
  - [ ] 1.2 Test phone validation (Kenya format, international, invalid)
  - [ ] 1.3 Test age validation (16, 17, 18, 19+)
  - [ ] 1.4 Test required field validation (missing required fields)
  - [ ] 1.5 Test optional fields (can skip emotional questions)
  - [ ] 1.6 Test zone assessment validation (both parts required)
  - [ ] 1.7 Test consent validation (weekly updates choice)

- [ ] **2. Write Integration Tests** (AC: #2)
  - [ ] 2.1 Test form submission flow (frontend → API)
  - [ ] 2.2 Test API writes to Google Sheets
  - [ ] 2.3 Test error handling (API failure, network timeout)
  - [ ] 2.4 Test rate limiting (multiple submissions)
  - [ ] 2.5 Test CORS configuration
  - [ ] 2.6 Test data transformation (form fields → Sheet columns)
  - [ ] 2.7 Verify all 26 columns populated correctly

- [ ] **3. Mobile Browser Testing** (AC: #3)
  - [ ] 3.1 Test on iPhone (Safari, 375px width)
  - [ ] 3.2 Test on Android (Chrome, 360px width)
  - [ ] 3.3 Test on tablet (iPad, 768px width)
  - [ ] 3.4 Test touch targets ≥44px
  - [ ] 3.5 Test single-column layout on mobile
  - [ ] 3.6 Test thumb-friendly navigation (buttons at bottom)
  - [ ] 3.7 Test font sizes readable (min 16px)
  - [ ] 3.8 Test form scrolling on long forms

- [ ] **4. Desktop Browser Testing** (AC: #2)
  - [ ] 4.1 Test Chrome (latest version)
  - [ ] 4.2 Test Firefox (latest version)
  - [ ] 4.3 Test Safari (macOS)
  - [ ] 4.4 Test Edge (latest version)
  - [ ] 4.5 Test responsive breakpoints (mobile, tablet, desktop)
  - [ ] 4.6 Test form validation across browsers
  - [ ] 4.7 Test accessibility (keyboard navigation, screen reader)

- [ ] **5. Security Audit** (AC: #4)
  - [ ] 5.1 Verify HTTPS enabled (automatic on Vercel)
  - [ ] 5.2 Verify environment variables not committed to git
  - [ ] 5.3 Verify .env.local in .gitignore
  - [ ] 5.4 Verify input sanitization (prevent XSS)
  - [ ] 5.5 Verify rate limiting prevents abuse
  - [ ] 5.6 Verify CORS restricted to production domain
  - [ ] 5.7 Verify error messages don't leak sensitive info
  - [ ] 5.8 Verify Sheet NOT publicly accessible

- [ ] **6. Accessibility Testing** (AC: #2, #3)
  - [ ] 6.1 Test keyboard navigation (Tab, Enter, Arrow keys)
  - [ ] 6.2 Test screen reader compatibility (NVDA, JAWS, VoiceOver)
  - [ ] 6.3 Verify ARIA labels on form fields
  - [ ] 6.4 Verify error messages linked to inputs (aria-describedby)
  - [ ] 6.5 Test focus management (return to form after errors)
  - [ ] 6.6 Verify color contrast ratios (WCAG AA)
  - [ ] 6.7 Test form with keyboard only (no mouse)

- [ ] **7. Performance Testing** (AC: #2)
  - [ ] 7.1 Test form load time (<3 seconds)
  - [ ] 7.2 Test API response time (<2 seconds)
  - [ ] 7.3 Test concurrent submissions (10 simultaneous)
  - [ ] 7.4 Test with slow network (3G simulation)
  - [ ] 7.5 Verify loading states display correctly
  - [ ] 7.6 Verify no memory leaks (Chrome DevTools)

- [ ] **8. Deploy Frontend to Vercel** (AC: #5)
  - [ ] 8.1 Push code to git repository
  - [ ] 8.2 Verify Vercel connected to repository
  - [ ] 8.3 Trigger Vercel deployment
  - [ ] 8.4 Monitor build logs for errors
  - [ ] 8.5 Verify deployment successful
  - [ ] 8.6 Test production URL: `https://your-domain.vercel.app`
  - [ ] 8.7 Verify custom domain configured (if applicable)

- [ ] **9. Deploy Backend to Vercel** (AC: #5)
  - [ ] 9.1 Verify API files in `api/` directory
  - [ ] 9.2 Verify environment variables set in Vercel dashboard
  - [ ] 9.3 Trigger Vercel deployment (if not automatic)
  - [ ] 9.4 Monitor build logs for errors
  - [ ] 9.5 Test API endpoint: `https://your-domain.vercel.app/api/submit-diagnostic`
  - [ ] 9.6 Verify CORS headers correct
  - [ ] 9.7 Verify error responses correct

- [ ] **10. Production Smoke Tests** (AC: #6)
  - [ ] 10.1 Navigate to production form URL
  - [ ] 10.2 Fill out form with test data
  - [ ] 10.3 Submit form successfully
  - [ ] 10.4 Verify data appears in Google Sheets
  - [ ] 10.5 Verify formulas calculate (Cluster, Crisis Flag, Priority)
  - [ ] 10.6 Test validation errors (try to submit invalid data)
  - [ ] 10.7 Test loading states display
  - [ ] 10.8 Test on mobile device (real hardware)

- [ ] **11. User Acceptance Testing** (AC: #2, #3, #6)
  - [ ] 11.1 Trevor tests form submission workflow
  - [ ] 11.2 Trevor verifies data appears in Sheets correctly
  - [ ] 11.3 Trevor tests dashboard views (Cohort Overview, High-Priority)
  - [ ] 11.4 Test crisis flag workflow (submit high-anxiety test)
  - [ ] 11.5 Test parent email notification (if implemented)
  - [ ] 11.6 Document any issues or feedback
  - [ ] 11.7 Address critical issues before launch

- [ ] **12. Create Deployment Runbook** (AC: #5, #6)
  - [ ] 12.1 Document deployment process
  - [ ] 12.2 Document rollback procedure
  - [ ] 12.3 Document monitoring setup (Vercel logs)
  - [ ] 12.4 Document backup location (Google Sheets backup)
  - [ ] 12.5 Document troubleshooting common issues
  - [ ] 12.6 Share runbook with Trevor

---

## Dev Notes

### Strategic Context (Story 5.4 Integration)

**Why Testing Matters:**
- This is the primary data capture for the entire cohort
- Errors here = missing students = crisis interventions missed
- Trevor's 10% workflow depends on accurate data
- Parent contact information MUST be correct for Level 4 interventions

**Critical Test Scenarios:**

**1. High-Anxiety Student (Crisis Detection):**
- Submit test with anxiety = 8
- Verify Crisis Flag = "HIGH ANXIETY"
- Verify Intervention Priority = "LEVEL 3"
- Trevor should see this in High-Priority Students view

**2. Crisis Keywords (Suicide Prevention):**
- Submit test with motivation = "I feel hopeless"
- Verify Crisis Flag = "CRISIS"
- Verify SafetyFilter would detect (if Discord bot implemented)

**3. Zone 0 Student (Targeted Support):**
- Submit test with Zone 0, anxiety = 6
- Verify Intervention Priority = "LEVEL 2: Monitor + DM"
- Verify Trevor can identify Zone 0 students

**4. Mobile User (Real-World Scenario):**
- Test on actual iPhone (not simulator)
- Verify all fields accessible
- Verify keyboard doesn't hide inputs
- Verify submission works

### Technical Architecture

**Unit Testing Strategy:**

**Form Validation Tests:**
```javascript
// Example: test validation.js
describe('Email Validation', () => {
  test('valid email passes', () => {
    expect(validateEmail('test@example.com')).toBe(true);
  });

  test('invalid email fails', () => {
    expect(validateEmail('not-an-email')).toBe(false);
  });

  test('edge case: empty string fails', () => {
    expect(validateEmail('')).toBe(false);
  });
});
```

**Integration Testing Strategy:**

**End-to-End Flow:**
1. Frontend form submits data
2. API receives POST request
3. API validates data
4. API writes to Google Sheets
5. Verify row appears in Sheet
6. Verify formulas calculate

**Mobile Testing Matrix:**
- **iPhone:** Safari (iOS 15+, 375px width)
- **Android:** Chrome (Android 10+, 360px width)
- **Tablet:** iPad Safari (768px width)
- **Small screen:** iPhone SE (320px width)
- **Large phone:** iPhone Pro Max (428px width)

**Security Checklist:**
- ✅ HTTPS only (automatic on Vercel, verify in browser)
- ✅ Environment variables in Vercel dashboard (not in code)
- ✅ .env.local in .gitignore (verify git doesn't track it)
- ✅ Input sanitization (test XSS: `<script>alert('xss')</script>`)
- ✅ Rate limiting (submit 5 times rapidly, should get 429)
- ✅ CORS headers (test from unauthorized domain, should fail)
- ✅ Sheet not public (try to access without auth, should fail)

**Accessibility Testing:**

**Keyboard Navigation:**
- Tab through all fields (order should be logical)
- Press Enter to submit (should work)
- Arrow keys for dropdowns
- Escape to close modals (if any)

**Screen Reader Testing:**
- NVDA (Windows, free)
- JAWS (Windows, paid)
- VoiceOver (macOS, built-in)
- TalkBack (Android, built-in)

**ARIA Labels:**
```html
<label for="email">Email Address</label>
<input
  id="email"
  type="email"
  aria-required="true"
  aria-invalid="false"
  aria-describedby="email-error"
>
<span id="email-error" role="alert"></span>
```

**Performance Benchmarks:**
- Form load time: <3 seconds (3G connection)
- API response time: <2 seconds (p95)
- Time to interactive: <5 seconds
- No layout shifts (CLS <0.1)

### Deployment Strategy

**Vercel Deployment:**
- Automatic deployment on push to main branch
- Preview deployments for pull requests
- Production deployment: merge to main branch
- Zero-downtime deployments (Vercel handles this)

**Environment-Specific Configuration:**
- Development: `.env.local` (local testing)
- Preview: Vercel environment variables (preview deployments)
- Production: Vercel environment variables (production)

**Deployment Checklist:**
- ✅ All tests pass locally
- ✅ Code pushed to git
- ✅ Environment variables set in Vercel
- ✅ Google Sheet shared with service account
- ✅ Form tested on staging/preview URL
- ✅ Trevor approved for production

**Rollback Plan:**
- Vercel automatically keeps previous deployments
- Rollback: Vercel dashboard → Deployments → Select previous → "Promote to Production"
- Document rollback in runbook

### Monitoring & Troubleshooting

**Vercel Logs:**
- Real-time logs: Vercel dashboard → Logs
- Filter by function: `/api/submit-diagnostic`
- Look for: 4xx errors (client issues), 5xx errors (server issues)

**Google Sheets Monitoring:**
- Check Sheet daily for new submissions
- Verify formulas calculating correctly
- Check for duplicate submissions (rate limiting issue)

**Common Issues:**

**1. Form submission fails:**
- Check browser console for errors
- Check network tab for API response
- Check Vercel logs
- Verify environment variables set

**2. Data not appearing in Sheet:**
- Verify service account has Editor access
- Verify Sheet ID correct
- Check Vercel logs for API errors
- Test API directly with Postman

**3. Form not loading:**
- Check browser console
- Check Vercel deployment logs
- Verify all files deployed
- Test on different browser

**4. Mobile issues:**
- Test on real device (not emulator)
- Check viewport meta tag
- Verify touch targets ≥44px
- Check font sizes

---

## Dev Agent Record

### Implementation Plan

**Phase 1: Unit Testing (Task 1)**
- Write validation tests
- Test edge cases
- Achieve >80% code coverage

**Phase 2: Integration Testing (Task 2)**
- Test complete flow
- Verify API integration
- Test error scenarios

**Phase 3: Manual Testing (Tasks 3-7)**
- Mobile testing (real devices)
- Desktop testing (multiple browsers)
- Security audit
- Accessibility testing
- Performance testing

**Phase 4: Deployment (Tasks 8-9)**
- Deploy to Vercel
- Configure environment variables
- Test production deployment

**Phase 5: Acceptance & Documentation (Tasks 10-12)**
- Smoke tests
- User acceptance testing
- Create runbook

### Debug Log

*Story created: 2026-02-16*

### Completion Notes

*To be filled during implementation*

---

## File List

*To be updated during implementation*

---

## Change Log

*To be filled during implementation*

---

## Status

**Current Status:** ready-for-dev
**Last Updated:** 2026-02-16
**Dependencies:** Stories 1.1, 1.2, 1.3 must be complete
**Critical Path:** Yes (blocks production launch)
