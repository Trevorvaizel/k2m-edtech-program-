# Story 1.1: Frontend Form Component (7 Sections)

**Epic:** Landing Page Forms Integration
**Story:** 1.1 - Frontend Form Component
**Status:** ready-for-dev
**Created:** 2026-02-16
**Purpose:** Implement seamless branded diagnostic form on K2M landing page with 7 sections, mobile-responsive design, and real-time validation

---

## Story

As a **Prospective Student**,
I want **a beautifully designed, easy-to-complete diagnostic form on the K2M landing page**,
so that **I can apply to the cohort without leaving the website and feel confident in a seamless, professional experience**.

---

## Acceptance Criteria

1. **Form Library Setup** - React Hook Form or Formik installed and configured with proper validation
2. **7 Form Sections Implemented** - Age Verification, Basic Info, Zone Assessment (2-part), Emotional Baseline, Goals, Parent Contact, Consent Preferences
3. **Progressive Disclosure** - Multi-step form with progress indicator ("Step 1 of 7"), showing one section at a time
4. **Mobile-Responsive Design** - Tested on mobile devices with single-column layout, touch targets ≥44px, thumb-friendly navigation
5. **Real-Time Validation** - Phone format validation as user types, email format validation, immediate error feedback
6. **Privacy Assurance First Screen** - Privacy notice displayed BEFORE first question (per Story 5.4 Guardrails)
7. **Psychological Safety Design** - Optional emotional questions clearly marked, "skip if you're not ready" messaging, supportive language
8. **Kenya Crisis Resources** - Displayed gently at form end with stigma-reducing language
9. **Form Submission Handler** - POST request to backend API endpoint (endpoint URL from Story 1.2)
10. **Loading & Error States** - Loading spinner during submission, error messages for API failures

---

## Tasks / Subtasks

- [ ] **1. Setup Form Library & Project Structure** (AC: #1)
  - [ ] 1.1 Choose between React Hook Form vs Formik (evaluate project needs)
  - [ ] 1.2 Install form library: `npm install react-hook-form` OR `npm install formik`
  - [ ] 1.3 Create form component directory: `k2m-landing/src/components/StudentDiagnosticForm/`
  - [ ] 1.4 Create main form component: `StudentDiagnosticForm.jsx`
  - [ ] 1.5 Create section subdirectory: `sections/`
  - [ ] 1.6 Create validation utility: `validation.js`

- [ ] **2. Create Form Layout with Progress Indicator** (AC: #3)
  - [ ] 2.1 Implement progress indicator ("Step X of 7: [Section Name]")
  - [ ] 2.2 Create navigation buttons (Previous, Next, Submit)
  - [ ] 2.3 Implement step state management (currentStep, completedSteps)
  - [ ] 2.4 Add conditional rendering for each section
  - [ ] 2.5 Celebrate micro-completions ("Great! 30% done")

- [ ] **3. Implement Privacy Assurance First Screen** (AC: #6, Story 5.4 requirement)
  - [ ] 3.1 Create PrivacyAssurance component (sections/PrivacyAssurance.jsx)
  - [ ] 3.2 Display privacy notice BEFORE first question (mandatory first step)
  - [ ] 3.3 Include all Story 5.4 privacy assurances (confidential, encrypted, 6-month retention, never shared)
  - [ ] 3.4 Add "I understand and consent" checkbox (required to proceed)
  - [ ] 3.5 Style with supportive, non-intimidating language

- [ ] **4. Implement AgeVerification Section** (AC: #2, Section 1)
  - [ ] 4.1 Create AgeVerification.jsx component (sections/AgeVerification.jsx)
  - [ ] 4.2 Add multiple choice: 16 or under, 17, 18, 19 or over
  - [ ] 4.3 Implement conditional logic: if age ≤17, show minors consent question
  - [ ] 4.4 Validate: Age selection is required
  - [ ] 4.5 Add supportive language about parental notification

- [ ] **5. Implement BasicInfo Section** (AC: #2, Section 2)
  - [ ] 5.1 Create BasicInfo.jsx component (sections/BasicInfo.jsx)
  - [ ] 5.2 Add First Name field (required, text input)
  - [ ] 5.3 Add Last Name field (required, text input, for cluster assignment)
  - [ ] 5.4 Add Email Address field (required, email validation)
  - [ ] 5.5 Add Discord Username field (optional, text input)
  - [ ] 5.6 Implement real-time validation (email format check)

- [ ] **6. Implement ZoneAssessment Section (2-Part Verification)** (AC: #2, Section 3, Story 5.4 requirement)
  - [ ] 6.1 Create ZoneAssessment.jsx component (sections/ZoneAssessment.jsx)
  - [ ] 6.2 Part 1: Self-assessment multiple choice (Zone 0-4 descriptions in simple language)
  - [ ] 6.3 Part 2: Scenario-based verification (situational questions)
  - [ ] 6.4 Use Story 5.4 exact zone descriptions and scenarios
  - [ ] 6.5 Validate: Both parts required
  - [ ] 6.6 Add explanatory language: "No wrong answers, this helps us support you"

- [ ] **7. Implement EmotionalBaseline Section** (AC: #2, #7, Section 4)
  - [ ] 7.1 Create EmotionalBaseline.jsx component (sections/EmotionalBaseline.jsx)
  - [ ] 7.2 Add "How are you feeling about AI right now?" checkboxes (Curious, Anxious, Excited, Overwhelmed, etc.)
  - [ ] 7.3 Add anxiety level 1-10 scale with anchors (1=Calm, 5=Nervous, 10=Panicked)
  - [ ] 7.4 Add confidence level multiple choice (Not at all → Very confident)
  - [ ] 7.5 Add motivation free text ("What brings you to this cohort?")
  - [ ] 7.6 Add goals free text ("What do you hope to achieve?")
  - [ ] 7.7 Add 4 Habits pre-assessment checkboxes (Pause, Context, Iterate, Think First, None yet)
  - [ ] 7.8 Mark ALL emotional questions as OPTIONAL with "You can skip this" messaging
  - [ ] 7.9 Add normalization language: "Many students feel this way"

- [ ] **8. Implement ParentContact Section** (AC: #2, Section 5)
  - [ ] 8.1 Create ParentContact.jsx component (sections/ParentContact.jsx)
  - [ ] 8.2 Add Parent/Guardian Name field (required, text input)
  - [ ] 8.3 Add Parent Phone Number field (required, phone validation, international formats)
  - [ ] 8.4 Add Parent Email Address field (required, email validation)
  - [ ] 8.5 Add Emergency Contact Backup field (optional, phone number)
  - [ ] 8.6 Add crisis protocol explanation: "When would we contact your parent?"
  - [ ] 8.7 Use Story 5.4 exact language about crisis intervention
  - [ ] 8.8 Implement real-time phone validation (country codes, formats)

- [ ] **9. Implement ConsentPreferences Section** (AC: #2, Section 6)
  - [ ] 9.1 Create ConsentPreferences.jsx component (sections/ConsentPreferences.jsx)
  - [ ] 9.2 Add weekly updates multiple choice: Yes/No/Not sure yet
  - [ ] 9.3 For "Yes": Explain what we share (habit practice, NOT private DMs)
  - [ ] 9.4 For "No": Explain privacy until Week 8
  - [ ] 9.5 For "Not sure": Explain no pressure, can decide later
  - [ ] 9.6 Add student autonomy messaging
  - [ ] 9.7 Validate: Choice is required

- [ ] **10. Add Kenya Crisis Resources** (AC: #8, Story 5.4 requirement)
  - [ ] 10.1 Create CrisisResources component (sections/CrisisResources.jsx)
  - [ ] 10.2 Display resources at form end (after completion message)
  - [ ] 10.3 Include Story 5.4 resources: Befriending Kenya, Mental Health Kenya, Youth Crisis Hotline, Emergency
  - [ ] 10.4 Use stigma-reducing, supportive language
  - [ ] 10.5 Add "You can always DM Trevor if you need support"

- [ ] **11. Implement Real-Time Validation** (AC: #5)
  - [ ] 11.1 Add email format validation (regex pattern)
  - [ ] 11.2 Add phone number validation (Kenya +254XXXXXXXXX, International +XXXXXXXXXX)
  - [ ] 11.3 Implement "Looks good!" micro-interactions
  - [ ] 11.4 Show error messages immediately on blur
  - [ ] 11.5 Disable Next button until required fields valid
  - [ ] 11.6 Add visual feedback (green checkmarks, red borders)

- [ ] **12. Implement Mobile-Responsive Design** (AC: #4)
  - [ ] 12.1 Test form on mobile viewport (375px width)
  - [ ] 12.2 Implement single-column layout on mobile
  - [ ] 12.3 Ensure touch targets ≥44px (buttons, inputs)
  - [ ] 12.4 Test thumb-friendly navigation (buttons at bottom)
  - [ ] 12.5 Verify font sizes readable on mobile (min 16px)
  - [ ] 12.6 Test on actual mobile devices (iPhone, Android)

- [ ] **13. Implement Form Submission & Loading States** (AC: #9, #10)
  - [ ] 13.1 Create form submission handler (POST to /api/submit-diagnostic)
  - [ ] 13.2 Add loading spinner during submission
  - [ ] 13.3 Show success message after completion
  - [ ] 13.4 Display next steps: "Join Discord server", "Check #welcome", "Week 1 starts Monday"
  - [ ] 13.5 Add error handling: Display error message if API fails
  - [ ] 13.6 Implement retry mechanism on submission failure
  - [ ] 13.7 Add form data transformation (format for backend API)

---

## Dev Notes

### Strategic Context (From Story 5.4: Google Forms Diagnostic)

**This form replaces Google Forms with a custom branded experience on the landing page.**

**Why This Matters:**
- Seamless UX (no redirect to Google)
- Brand control and data ownership
- Higher conversion rates (less friction)
- Better mobile experience

**Story 5.4 Requirements Integration:**

**1. Privacy & Safety (Guardrails #3, #8, #10):**
- Privacy assurance BEFORE first question
- All emotional questions OPTIONAL
- No forced disclosure
- Supportive, non-judgmental language
- Data stored securely (encrypted Google Sheets)

**2. Zone Assessment (Guardrails #2, #7, #11):**
- Two-part verification (self-assessment + scenarios)
- Use Story 5.4 EXACT descriptions and scenarios
- No comparison to peers
- Multiple valid starting points honored

**3. Emotional Baseline (JTBD Emotional Job):**
- Anxiety scale 1-10 with anchors
- Belonging cues: "Do you feel like everyone else gets it except you?"
- Normalization: "Many students feel this way"
- Escalation flags: Anxiety ≥8 triggers Trevor outreach

**4. Parent/Guardian Contact (Level 4 Crisis Protocol):**
- Required fields (name, phone, email)
- Crisis protocol explanation (when we contact parents)
- International phone format support
- Emergency contact backup

**5. Weekly Updates Consent (JTBD Social Job):**
- Student choice: Yes/No/Not sure yet
- No pressure either way
- Weekly emails OR privacy until Week 8

**6. Kenya Crisis Resources:**
- Display at form end
- Stigma-reducing language
- Befriending Kenya: +254 722 178 177
- Mental Health Kenya: +254 733 111 000
- Youth Crisis Hotline: +254 1199
- Emergency: 999 or 112

### Technical Architecture

**Form Library Choice:**

**React Hook Form (Recommended):**
- Pros: Lightweight, better performance, less re-rendering
- Built-in validation
- Easy to integrate with existing React setup
- Smaller bundle size

**Formik (Alternative):**
- Pros: More mature, larger community
- Built-in error messaging
- Easier for complex forms

**Decision:** Evaluate project setup in k2m-landing/package.json and choose based on existing dependencies.

**Component Structure:**
```
k2m-landing/src/components/StudentDiagnosticForm/
├── StudentDiagnosticForm.jsx (main form, step management)
├── sections/
│   ├── PrivacyAssurance.jsx (step 0, required first)
│   ├── AgeVerification.jsx (step 1)
│   ├── BasicInfo.jsx (step 2)
│   ├── ZoneAssessment.jsx (step 3, 2-part)
│   ├── EmotionalBaseline.jsx (step 4, optional questions)
│   ├── GoalsExpectations.jsx (step 5)
│   ├── ParentContact.jsx (step 6, required)
│   ├── ConsentPreferences.jsx (step 7)
│   └── CrisisResources.jsx (display at end)
├── validation.js (validation rules, schemas)
└── form.css (styling, mobile-responsive)
```

**State Management:**
- Current step (0-8, where 0=privacy, 8=complete)
- Form data (formData state object)
- Validation errors (errors state)
- Loading state (isLoading boolean)
- Submission status (success/error)

**API Integration (Story 1.2):**
- Submit to: `/api/submit-diagnostic` (Vercel serverless function)
- Method: POST
- Format: JSON
- Keys: Match Story 5.4 column names (first_name, last_name, zone_self_assessment, etc.)

**Mobile-First Design:**
- Start with mobile layout (375px viewport)
- Progressive enhancement for desktop
- Touch targets ≥44px
- Thumb-friendly navigation (buttons at bottom on mobile)
- Single column on mobile, multi-column on desktop if appropriate

**Validation Strategy:**
- Real-time validation on blur (field loses focus)
- Disable Next button until current section valid
- Show error messages immediately below fields
- Success feedback (green checkmarks, "Looks good!")
- Phone validation: Support Kenya (+254XXXXXXXXX) and international formats

**Accessibility:**
- ARIA labels for form fields
- Keyboard navigation (Tab, Enter, Arrow keys)
- Screen reader support
- Focus management (return to form after errors)
- Error messages linked to inputs (aria-describedby)

**Psychological Safety Design:**
- Language: "You can skip this" on optional questions
- Visual distinction: Optional fields clearly marked
- Progress indicator: Shows how far along, NOT how much remains
- Micro-completions: Celebrate progress ("Great! 30% done")
- Privacy first: Assurance BEFORE any questions

### Foundation Documents Integration

**Guardrails Compliance (Story 5.4, Epic 1.1):**
- ✅ Guardrail #1: No prescriptive paths ("Where are YOU starting from?")
- ✅ Guardrail #2: No "should" language
- ✅ Guardrail #3: No comparison/ranking (self-assessment only)
- ✅ Guardrail #6: Agent purity expectations
- ✅ Guardrail #7: No zone skipping (honest assessment)
- ✅ Guardrail #8: Discord safety (privacy assured)
- ✅ Guardrail #10: Revolutionary Hope tone, Level 1-2 language
- ✅ Guardrail #11: JTBD-relevant examples (university, career)

**JTBD Integration (Story 5.4, Epic 1.2):**
- ✅ Emotional Job: Anxiety reduction, belonging cues ("Many students feel this way")
- ✅ Social Job: Parent email capture, weekly updates consent
- ✅ Identity Shifts: Zone baseline (Outsider → Observer → Experimenter → Collaborator → Director)

**4 Habits Branding (Story 5.4, Epic 1.4):**
- ✅ Brief mention in privacy or intro
- ✅ Pre-assessment question ("Which habits do you ALREADY use?")
- ✅ Builds confidence before cohort starts

### Existing Project Context

**Project Location:** `k2m-landing/`

**Check existing setup:**
- Framework: React (Vite-based, from package.json)
- Styling: CSS (Tailwind mentioned in git status, verify usage)
- Build tool: Vite
- Hosting: Vercel (vercel.json exists)

**Integration Points:**
- Add form to landing page route (likely `/apply` or `/cohort-application`)
- Update navigation to include "Apply" CTA
- Ensure form matches existing brand design (colors, fonts, voice)

---

## Dev Agent Record

### Implementation Plan

**Phase 1: Setup & Structure (Tasks 1-3)**
- Install form library (React Hook Form recommended)
- Create component directory structure
- Build form layout with progress indicator
- Implement privacy assurance first screen (mandatory)

**Phase 2: Form Sections (Tasks 4-10)**
- Build each section component following Story 5.4 specifications
- Use EXACT language from Story 5.4 for questions and options
- Mark optional questions clearly (Emotional Baseline)
- Implement conditional logic (age ≤17 shows minors consent)

**Phase 3: Validation & UX (Tasks 11-13)**
- Real-time validation (email, phone)
- Mobile-responsive testing
- Loading and error states
- Form submission handler

**Phase 4: Testing & Polish**
- Test on mobile devices (iPhone, Android)
- Verify all validations work
- Test form submission flow
- Accessibility audit (keyboard navigation, screen reader)

### Debug Log

*Implementation starts: 2026-02-16*

### Completion Notes

*To be filled during implementation*

---

## File List

*To be updated during implementation*

---

## Change Log

*To be updated during implementation*

---

## Status

**Current Status:** ready-for-dev
**Last Updated:** 2026-02-16
**Ready for Development:** All acceptance criteria defined, tasks broken down, Dev Notes comprehensive with Story 5.4 integration
