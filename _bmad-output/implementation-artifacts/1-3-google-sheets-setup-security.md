# Story 1.3: Google Sheets Setup + Security

**Epic:** Landing Page Forms Integration
**Story:** 1.3 - Google Sheets Setup + Security
**Status:** ready-for-dev
**Created:** 2026-02-16
**Purpose:** Configure Google Sheets with 26 columns, formulas, and secure service account authentication

---

## Story

As a **System Administrator**,
I want **a properly configured Google Sheet with all required columns, formulas, and secure API access**,
so that **the backend API can write diagnostic data and Trevor can use his existing workflow with all automation intact**.

---

## Acceptance Criteria

1. **Google Sheets API Enabled** - API enabled in Google Cloud Console with service account created
2. **Service Account Authenticated** - Service account with JSON credentials, shared with Sheet
3. **Sheet Structure** - New Sheet created with all 26 columns from Story 5.4 specification
4. **Formulas Implemented** - Cluster assignment, crisis flags, intervention priority formulas working
5. **Environment Variables Secured** - Credentials stored in .env.local and Vercel environment variables
6. **Data Validation** - Column formatting, data types set correctly
7. **Testing Complete** - API can successfully write test data to Sheet
8. **Backup Strategy** - Version history enabled, backup copy created

---

## Tasks / Subtasks

- [ ] **1. Enable Google Sheets API** (AC: #1)
  - [ ] 1.1 Go to Google Cloud Console (console.cloud.google.com)
  - [ ] 1.2 Create new project OR select existing project
  - [ ] 1.3 Navigate to "APIs & Services" → "Library"
  - [ ] 1.4 Search for "Google Sheets API"
  - [ ] 1.5 Click "Enable" for Google Sheets API
  - [ ] 1.6 Verify API is enabled in "APIs & Services" → "Enabled APIs & services"

- [ ] **2. Create Service Account** (AC: #2)
  - [ ] 2.1 Go to "APIs & Services" → "Credentials"
  - [ ] 2.2 Click "Create Credentials" → "Service Account"
  - [ ] 2.3 Service account name: `k2m-diagnostic-api`
  - [ ] 2.4 Service account description: "API service account for K2M diagnostic form submissions"
  - [ ] 2.5 Click "Create and Continue"
  - [ ] 2.6 Skip granting roles (we'll grant Sheet access directly)
  - [ ] 2.7 Click "Done"
  - [ ] 2.8 Note service account email: `k2m-diagnostic-api@project-id.iam.gserviceaccount.com`

- [ ] **3. Create and Download Service Account Key** (AC: #2)
  - [ ] 3.1 Click on service account name
  - [ ] 3.2 Go to "Keys" tab
  - [ ] 3.3 Click "Add Key" → "Create New Key"
  - [ ] 3.4 Key type: JSON
  - [ ] 3.5 Click "Create"
  - [ ] 3.6 Download JSON file (automatic)
  - [ ] 3.7 Rename to `k2m-diagnostic-api-credentials.json`
  - [ ] 3.8 Store securely (never commit to git)

- [ ] **4. Create Google Sheet** (AC: #3)
  - [ ] 4.1 Go to Google Sheets (sheets.google.com)
  - [ ] 4.2 Click "Blank" spreadsheet
  - [ ] 4.3 Name: "K2M Cohort #X - Diagnostic Responses"
  - [ ] 4.4 Create sheet: "Diagnostic Responses" (first tab)
  - [ ] 4.5 Create additional sheets: "Cohort Overview", "High-Priority Students", "Zone Distribution" (for Trevor's dashboard)

- [ ] **5. Add Column Headers (26 Columns)** (AC: #3)
  - [ ] 5.1 Add header row (Row 1) with all 26 column names from Story 5.4
  - [ ] 5.2 Column A: Timestamp
  - [ ] 5.3 Column B: Student ID
  - [ ] 5.4 Column C: First Name
  - [ ] 5.5 Column D: Last Name
  - [ ] 5.6 Column E: Email Address
  - [ ] 5.7 Column F: Discord Username
  - [ ] 5.8 Column G: Age
  - [ ] 5.9 Column H: Zone Self-Assessment
  - [ ] 5.10 Column I: Zone Verification
  - [ ] 5.11 Column J: AI Experience Level
  - [ ] 5.12 Column K: Anxiety Level
  - [ ] 5.13 Column L: Confidence Level
  - [ ] 5.14 Column M: Motivation
  - [ ] 5.15 Column N: Goals
  - [ ] 5.16 Column O: 4 Habits Pre-Assessment
  - [ ] 5.17 Column P: Parent/Guardian Name
  - [ ] 5.18 Column Q: Parent Phone Number
  - [ ] 5.19 Column R: Parent Email Address
  - [ ] 5.20 Column S: Emergency Contact Backup
  - [ ] 5.21 Column T: Weekly Updates Consent
  - [ ] 5.22 Column U: Cluster Assignment
  - [ ] 5.23 Column V: Crisis Flag
  - [ ] 5.24 Column W: Intervention Priority
  - [ ] 5.25 Column X: Trevor Review Notes
  - [ ] 5.26 Column Y: Outreach Status
  - [ ] 5.27 Column Z: Data Retention Date

- [ ] **6. Implement Formulas** (AC: #4)
  - [ ] 6.1 Column U (Cluster Assignment): `=IF(UPPER(LEFT(D2,1))<="F", "Cluster 1", IF(UPPER(LEFT(D2,1))<="L", "Cluster 2", IF(UPPER(LEFT(D2,1))<="R", "Cluster 3", "Cluster 4")))`
  - [ ] 6.2 Column V (Crisis Flag): `=IF(K2>=7, "HIGH ANXIETY", IF(OR(M2="want to die", M2="hopeless", M2="can't go on", M2="suicide", M2="self-harm"), "CRISIS", "OK"))`
  - [ ] 6.3 Column W (Intervention Priority): `=IF(AND(H2="Zone 0", K2>=7), "LEVEL 3: IMMEDIATE outreach", IF(AND(H2="Zone 0", K2>=5), "LEVEL 2: Monitor + DM", IF(K2>=8, "LEVEL 3: Check in", "LEVEL 1: Normal monitoring")))`
  - [ ] 6.4 Column Z (Data Retention Date): `=A2 + 180`
  - [ ] 6.5 Test formulas with sample data

- [ ] **7. Share Sheet with Service Account** (AC: #2)
  - [ ] 7.1 Click "Share" button in Google Sheet
  - [ ] 7.2 Paste service account email
  - [ ] 7.3 Grant role: "Editor"
  - [ ] 7.4 Click "Send"
  - [ ] 7.5 Verify service account appears in "Share" settings
  - [ ] 7.6 Note Sheet ID from URL: `https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit`

- [ ] **8. Set Up Environment Variables** (AC: #5)
  - [ ] 8.1 Open service account JSON file
  - [ ] 8.2 Extract `client_email` value
  - [ ] 8.3 Extract `private_key` value (replace \n with \\n for .env)
  - [ ] 8.4 Extract `project_id` (for reference)
  - [ ] 8.5 Create .env.local file in k2m-landing/
  - [ ] 8.6 Add `GOOGLE_SHEETS_CLIENT_EMAIL=service-account-email`
  - [ ] 8.7 Add `GOOGLE_SHEETS_PRIVATE_KEY="private-key-with-escaped-newlines"`
  - [ ] 8.8 Add `GOOGLE_SHEETS_SHEET_ID=your-sheet-id`
  - [ ] 8.9 Verify .env.local is in .gitignore

- [ ] **9. Configure Vercel Environment Variables** (AC: #5)
  - [ ] 9.1 Go to Vercel dashboard (vercel.com)
  - [ ] 9.2 Select k2m-landing project
  - [ ] 9.3 Go to "Settings" → "Environment Variables"
  - [ ] 9.4 Add `GOOGLE_SHEETS_CLIENT_EMAIL` (same value as .env.local)
  - [ ] 9.5 Add `GOOGLE_SHEETS_PRIVATE_KEY` (same value as .env.local)
  - [ ] 9.6 Add `GOOGLE_SHEETS_SHEET_ID` (same value as .env.local)
  - [ ] 9.7 Select all environments (Production, Preview, Development)
  - [ ] 9.8 Click "Save"
  - [ ] 9.9 Redeploy project to pick up new environment variables

- [ ] **10. Format Columns and Add Data Validation** (AC: #6)
  - [ ] 10.1 Freeze header row (View → Freeze → 1 row)
  - [ ] 10.2 Format header row: Bold, background color
  - [ ] 10.3 Set text wrapping for long text columns (M, N, X)
  - [ ] 10.4 Format Column K (Anxiety Level) as number
  - [ ] 10.5 Format Column Z (Data Retention Date) as date
  - [ ] 10.6 Add data validation to Column G (Age): Dropdown list
  - [ ] 10.7 Add data validation to Column H (Zone): Dropdown list
  - [ ] 10.8 Add conditional formatting for Column V (Crisis Flag): Red if CRISIS, yellow if HIGH ANXIETY

- [ ] **11. Test API → Sheets Integration** (AC: #7)
  - [ ] 11.1 Use Story 1.2 API endpoint (or create test script)
  - [ ] 11.2 Submit test data to API
  - [ ] 11.3 Verify row appears in Google Sheets
  - [ ] 11.4 Verify all 26 columns populated correctly
  - [ ] 11.5 Verify formulas calculate (Cluster Assignment, Crisis Flag, Intervention Priority)
  - [ ] 11.6 Verify Student ID format correct
  - [ ] 11.7 Verify timestamp auto-generated
  - [ ] 11.8 Test with invalid data (should fail validation)

- [ ] **12. Set Up Backup Strategy** (AC: #8)
  - [ ] 12.1 Enable version history in Google Sheets (File → Version history → See version history)
  - [ ] 12.2 Create backup copy: File → Make a copy
  - [ ] 12.3 Name backup: "K2M Cohort #X - Diagnostic Responses - BACKUP"
  - [ ] 12.4 Store backup in separate folder
  - [ ] 12.5 Set up automatic weekly exports (optional, Google Apps Script)
  - [ ] 12.6 Document backup location in runbook

---

## Dev Notes

### Strategic Context (Story 5.4 Integration)

**Why This Matters:**
- Trevor's existing workflow depends on Google Sheets
- All formulas, dashboards, and manual review processes are Sheets-based
- Preserving this workflow means zero disruption to operations

**Story 5.4 Requirements:**
- 26 columns with exact names and order
- Formulas for cluster assignment (by last name)
- Crisis flag formulas (anxiety ≥8, crisis keywords)
- Intervention priority logic (Zone + anxiety combination)
- Data retention tracking (6 months)

### Technical Architecture

**Google Cloud Console Setup:**
1. Create project or use existing
2. Enable Google Sheets API
3. Create service account
4. Download JSON credentials
5. Share Sheet with service account email

**Service Account JSON Structure:**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "k2m-diagnostic-api@project-id.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

**Environment Variables Format:**

**.env.local:**
```env
GOOGLE_SHEETS_CLIENT_EMAIL=k2m-diagnostic-api@project-id.iam.gserviceaccount.com
GOOGLE_SHEETS_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQE...\\n-----END PRIVATE KEY-----\\n"
GOOGLE_SHEETS_SHEET_ID=1ABC123...
```

**Vercel Environment Variables:**
- Same keys, same values
- Set in dashboard, NOT in code
- Automatically injected into serverless functions

**Sheet Sharing Permissions:**
- Service account email: `k2m-diagnostic-api@project-id.iam.gserviceaccount.com`
- Role: "Editor" (can read and write)
- DO NOT share with "Anyone with link" (security risk)
- Trevor retains ownership

**Formula Explanations:**

1. **Cluster Assignment (Column U):**
   - Uses first letter of last name (Column D)
   - Case-insensitive (UPPER function)
   - Maps to 4 clusters: A-F, G-L, M-R, S-Z

2. **Crisis Flag (Column V):**
   - Triggers if anxiety ≥7
   - Triggers if crisis keywords in motivation (want to die, hopeless, suicide, etc.)
   - Values: "OK", "HIGH ANXIETY", "CRISIS"

3. **Intervention Priority (Column W):**
   - LEVEL 3: Zone 0 + anxiety ≥7 OR anxiety ≥8
   - LEVEL 2: Zone 0 + anxiety ≥5
   - LEVEL 1: Normal monitoring

4. **Data Retention Date (Column Z):**
   - Timestamp + 180 days
   - Automatic deletion reminder

**Security Checklist:**
- ✅ Service account JSON never committed to git
- ✅ .env.local in .gitignore
- ✅ Private key escaped correctly (\n → \\n)
- ✅ Service account has Editor access (not Viewer)
- ✅ Sheet NOT publicly accessible
- ✅ Version history enabled (audit trail)
- ✅ Backup copy created

**Data Validation Rules:**
- Column G (Age): 16/17/18/19+ (dropdown)
- Column H (Zone Self-Assessment): Zone 0/Zone 1/Zone 2/Zone 3/Zone 4
- Column K (Anxiety Level): 1-10 (number)
- Column T (Weekly Updates Consent): Yes/No/Not sure yet

### Testing Script

**Simple test to verify API can write to Sheet:**
```javascript
// test-sheet-api.js
const { google } = require('googleapis');

const auth = new google.auth.JWT(
  process.env.GOOGLE_SHEETS_CLIENT_EMAIL,
  null,
  process.env.GOOGLE_SHEETS_PRIVATE_KEY.replace(/\\n/g, '\n'),
  ['https://www.googleapis.com/auth/spreadsheets']
);

const sheets = google.sheets({ version: 'v4', auth });

async function testWrite() {
  try {
    const response = await sheets.spreadsheets.values.append({
      spreadsheetId: process.env.GOOGLE_SHEETS_SHEET_ID,
      range: 'Diagnostic Responses!A:Z',
      valueInputOption: 'RAW',
      resource: {
        values: [[
          new Date().toISOString(),
          'TEST_1234',
          'Test',
          'Student',
          'test@example.com',
          '',
          '18',
          'Zone 1',
          'Zone 1',
          'Tried a few times',
          '5',
          'Somewhat confident',
          'Curious about AI',
          'Learn AI skills',
          'Pause, Context',
          'Test Parent',
          '+254700000000',
          'parent@example.com',
          '',
          'Yes'
        ]]
      }
    });
    console.log('✅ Test write successful:', response.data);
  } catch (error) {
    console.error('❌ Test write failed:', error);
  }
}

testWrite();
```

---

## Dev Agent Record

### Implementation Plan

**Phase 1: Google Cloud Setup (Tasks 1-3)**
- Enable Google Sheets API
- Create service account
- Download credentials

**Phase 2: Sheet Structure (Tasks 4-6)**
- Create Sheet with 26 columns
- Add all formulas
- Format and validate columns

**Phase 3: Security & Access (Tasks 7-9)**
- Share Sheet with service account
- Configure environment variables
- Set up Vercel environment

**Phase 4: Testing & Backup (Tasks 10-12)**
- Test API integration
- Verify all formulas work
- Create backup strategy

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
**Dependencies:** None (can be done in parallel with Story 1.2)
**Unblocks:** Story 1.2 (API needs Sheet ID and credentials)
