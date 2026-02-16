# Story 1.2: Backend API + Google Sheets Integration

**Epic:** Landing Page Forms Integration
**Story:** 1.2 - Backend API + Google Sheets Integration
**Status:** ready-for-dev
**Created:** 2026-02-16
**Purpose:** Create Vercel serverless API endpoint to receive form submissions and push data to Google Sheets

---

## Story

As a **Backend Developer**,
I want **a secure API endpoint that receives diagnostic form submissions and writes them to Google Sheets**,
so that **Trevor can review student data in the existing Sheets workflow with all formulas and automation intact**.

---

## Acceptance Criteria

1. **API Endpoint Created** - POST /api/submit-diagnostic endpoint accepting JSON form data
2. **Google Sheets API Integration** - Authenticated service account with write permissions
3. **Data Validation** - Backend validation of all required fields, error responses for invalid data
4. **Append Row Function** - Write form data to Sheet with all 26 columns in correct format
5. **Error Handling** - Try/catch blocks, meaningful error messages, retry logic for transient failures
6. **Rate Limiting** - Prevent spam/abuse (max 1 submission per minute per IP)
7. **CORS Configuration** - Allow requests from landing page domain only
8. **Environment Variables** - Sensitive credentials stored securely (never committed to git)

---

## Tasks / Subtasks

- [ ] **1. Create API Endpoint Structure** (AC: #1)
  - [ ] 1.1 Create API directory: `k2m-landing/api/`
  - [ ] 1.2 Create endpoint file: `submit-diagnostic.js`
  - [ ] 1.3 Export async handler function for Vercel
  - [ ] 1.4 Set up CORS headers
  - [ ] 1.5 Test endpoint responds to POST requests

- [ ] **2. Install Dependencies** (AC: #2)
  - [ ] 2.1 Install googleapis: `npm install googleapis`
  - [ ] 2.2 Verify package.json updated
  - [ ] 2.3 Test import works in serverless environment

- [ ] **3. Implement Form Data Validation** (AC: #3)
  - [ ] 3.1 Define required fields schema (first_name, last_name, email, zone_self_assessment, parent_name, parent_phone, parent_email)
  - [ ] 3.2 Implement email validation (regex check)
  - [ ] 3.3 Implement phone validation (Kenya +254, international formats)
  - [ ] 3.4 Validate age field (16/17/18/19+)
  - [ ] 3.5 Return 400 Bad Request with error messages for invalid data
  - [ ] 3.6 Sanitize inputs (prevent XSS, SQL injection)

- [ ] **4. Google Sheets API Authentication** (AC: #2, #8)
  - [ ] 4.1 Load credentials from environment variables
  - [ ] 4.2 Initialize Google Sheets API client
  - [ ] 4.3 Authenticate with service account
  - [ ] 4.4 Test API can read Sheet metadata
  - [ ] 4.5 Verify write permissions on target Sheet

- [ ] **5. Implement Append Row Function** (AC: #4)
  - [ ] 5.1 Map form fields to Sheet columns (26 columns from Story 5.4)
  - [ ] 5.2 Format timestamp (auto-generated)
  - [ ] 5.3 Generate Student ID (FIRST_LAST_#### format)
  - [ ] 5.4 Write row to Sheet using sheets.spreadsheets.values.append
  - [ ] 5.5 Verify data appears in correct columns
  - [ ] 5.6 Test with sample submission

- [ ] **6. Add Error Handling** (AC: #5)
  - [ ] 6.1 Wrap API calls in try/catch
  - [ ] 6.2 Return 500 Internal Server Error on failure
  - [ ] 6.3 Log errors to Vercel logs
  - [ ] 6.4 Implement retry logic for network failures (max 3 retries)
  - [ ] 6.5 Test error scenarios (invalid credentials, network timeout)

- [ ] **7. Implement Rate Limiting** (AC: #6)
  - [ ] 7.1 Use Vercel edge config or in-memory rate limiter
  - [ ] 7.2 Limit to 1 submission per minute per IP address
  - [ ] 7.3 Return 429 Too Many Requests on rate limit exceeded
  - [ ] 7.4 Add rate limit headers to response
  - [ ] 7.5 Test rate limiting works

- [ ] **8. Configure CORS** (AC: #7)
  - [ ] 8.1 Set Access-Control-Allow-Origin header (production domain only)
  - [ ] 8.2 Allow OPTIONS preflight requests
  - [ ] 8.3 Set Access-Control-Allow-Methods: POST, OPTIONS
  - [ ] 8.4 Set Access-Control-Allow-Headers: Content-Type
  - [ ] 8.5 Test CORS from frontend

- [ ] **9. Set Up Environment Variables** (AC: #8, Story 5.4 security)
  - [ ] 9.1 Create .env.local file (gitignored)
  - [ ] 9.2 Add GOOGLE_SHEETS_CLIENT_EMAIL
  - [ ] 9.3 Add GOOGLE_SHEETS_PRIVATE_KEY (with \n escaped)
  - [ ] 9.4 Add GOOGLE_SHEETS_SHEET_ID
  - [ ] 9.5 Add .env.local to .gitignore
  - [ ] 9.6 Test environment variables load correctly

- [ ] **10. Test API Endpoint** (AC: #1-8)
  - [ ] 10.1 Test with Postman or curl
  - [ ] 10.2 Test valid submission (200 OK)
  - [ ] 10.3 Test invalid data (400 Bad Request)
  - [ ] 10.4 Test rate limiting (429 Too Many Requests)
  - [ ] 10.5 Verify data appears in Google Sheets
  - [ ] 10.6 Test error scenarios (500 Internal Server Error)

---

## Dev Notes

### Strategic Context (Story 5.4 Integration)

**API Purpose:**
- Bridge between custom frontend form and Trevor's existing Google Sheets workflow
- Preserve all 26 columns, formulas, and automation
- Enable Trevor's dashboard views and manual review process

**Story 5.4 Column Mapping (26 Columns):**

```javascript
const columnMapping = {
  timestamp: new Date().toISOString(),
  student_id: `${firstName}_${lastName}_${Date.now().toString().slice(-4)}`,
  first_name: firstName,
  last_name: lastName, // For cluster assignment
  email_address: email,
  discord_username: discordUsername || '',
  age: age,
  zone_self_assessment: zoneSelfAssessment,
  zone_verification: zoneVerification,
  ai_experience_level: aiExperienceLevel,
  anxiety_level: anxietyLevel,
  confidence_level: confidenceLevel,
  motivation: motivation || '',
  goals: goals || '',
  four_habits_pre_assessment: fourHabitsPreAssessment || [],
  parent_guardian_name: parentName,
  parent_phone_number: parentPhone,
  parent_email_address: parentEmail,
  emergency_contact_backup: emergencyContact || '',
  weekly_updates_consent: weeklyUpdatesConsent,
  cluster_assignment: '', // Auto-calculated by Sheet formula
  crisis_flag: '', // Auto-calculated by Sheet formula
  intervention_priority: '', // Auto-calculated by Sheet formula
  trevor_review_notes: '',
  outreach_status: '',
  data_retention_date: '' // Auto-calculated (Timestamp + 180 days)
};
```

**Auto-Calculated Columns (Sheet Formulas):**
- Cluster assignment: Based on last name (A-F, G-L, M-R, S-Z)
- Crisis flag: Anxiety ≥8 OR crisis keywords
- Intervention priority: Zone + anxiety combination
- Data retention date: Timestamp + 180 days

### Technical Architecture

**Vercel Serverless Functions:**
- File-based routing: `api/submit-diagnostic.js` → `/api/submit-diagnostic`
- Automatically deployed to Vercel
- Serverless execution (scales automatically)
- 50-second execution limit (Vercel Hobby)
- 1MB request body limit

**Google Sheets API:**
```javascript
import { google } from 'googleapis';

const sheets = google.sheets({
  version: 'v4',
  auth: new google.auth.JWT(
    process.env.GOOGLE_SHEETS_CLIENT_EMAIL,
    null,
    process.env.GOOGLE_SHEETS_PRIVATE_KEY.replace(/\\n/g, '\n'),
    ['https://www.googleapis.com/auth/spreadsheets']
  )
});
```

**Validation Schema:**
```javascript
const requiredFields = [
  'firstName',
  'lastName',
  'email',
  'zoneSelfAssessment',
  'zoneVerification',
  'parentName',
  'parentPhone',
  'parentEmail'
];

const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

const validatePhone = (phone) => {
  // Kenya: 254XXXXXXXXX or +254XXXXXXXXX
  // International: +XXXXXXXXXX (10-15 digits)
  return /^\+?\d{10,15}$/.test(phone.replace(/\s/g, ''));
};
```

**Error Response Format:**
```javascript
// 400 Bad Request
{
  error: 'Validation failed',
  details: [
    { field: 'email', message: 'Invalid email format' },
    { field: 'parentPhone', message: 'Invalid phone format' }
  ]
}

// 500 Internal Server Error
{
  error: 'Internal server error',
  message: 'Failed to write to Google Sheets'
}
```

**Rate Limiting Strategy:**
- In-memory rate limiter (simple, effective for single instance)
- Store last submission timestamp per IP
- Reject if timestamp < 60 seconds ago
- Vercel serverless functions are stateless, so use Vercel KV or simple in-memory for MVP

**Security Checklist:**
- ✅ HTTPS only (automatic on Vercel)
- ✅ Environment variables for credentials (never commit)
- ✅ CORS restricted to production domain
- ✅ Input sanitization (prevent XSS)
- ✅ Rate limiting (prevent abuse)
- ✅ Error messages don't leak sensitive info

### Environment Variables Setup

**.env.local** (gitignored):
```env
GOOGLE_SHEETS_CLIENT_EMAIL=service-account@project-id.iam.gserviceaccount.com
GOOGLE_SHEETS_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
GOOGLE_SHEETS_SHEET_ID=1ABC123...
```

**Vercel Environment Variables (Production):**
- Add in Vercel dashboard: Settings → Environment Variables
- Same keys as .env.local
- Deploy automatically picks up changes

### Testing Strategy

**Manual Testing:**
```bash
# Test valid submission
curl -X POST https://your-domain.vercel.app/api/submit-diagnostic \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Test",
    "lastName": "Student",
    "email": "test@example.com",
    "zoneSelfAssessment": "Zone 1",
    ...
  }'

# Test rate limiting (should return 429 on second request within 60s)
```

**Integration Testing:**
- Submit form from frontend
- Verify data appears in Google Sheets
- Check all 26 columns populated correctly
- Verify formulas calculate cluster assignment, crisis flags

---

## Dev Agent Record

### Implementation Plan

**Phase 1: Setup (Tasks 1-3)**
- Create API endpoint structure
- Install googleapis dependency
- Implement validation schema

**Phase 2: Google Sheets Integration (Tasks 4-5)**
- Set up authentication
- Implement append row function
- Map all 26 columns correctly

**Phase 3: Security & Reliability (Tasks 6-8)**
- Error handling
- Rate limiting
- CORS configuration

**Phase 4: Configuration & Testing (Tasks 9-10)**
- Environment variables
- Comprehensive testing
- Production deployment

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
**Dependencies:** Story 1.1 must be complete (frontend form needs this endpoint)
**Blocked Until:** Google Sheets service account created (Story 1.3)
