# Google Sheets API Setup - Complete Guide

## Overview
This guide walks you through setting up Google Sheets API credentials to automate template creation. **One-time setup, takes 10-15 minutes.**

---

## Prerequisites
- Google account (any Gmail account works)
- Web browser (Chrome, Firefox, Edge, Safari)
- Internet connection

---

## Step 1: Create Google Cloud Project (3 minutes)

### 1.1 Go to Google Cloud Console
Open browser and go to: https://console.cloud.google.com/

**What you'll see:**
- Welcome screen or dashboard (if you've used Google Cloud before)

### 1.2 Create New Project
- Look at top left (next to "Google Cloud Platform" logo)
- Click dropdown that shows project name (or "Select a project")
- Click **"NEW PROJECT"** button (top right of popup)

**Fill in project details:**
- **Name:** `K2M Sheets Templates` (or any name you prefer)
- **Location:** `No organization` (leave as default)
- Click **"CREATE"**

**What happens:**
- Screen shows "Creating project..." with spinner
- Takes 10-30 seconds
- You'll see notification: "Project K2M Sheets Templates created"

### 1.3 Verify You're in the Right Project
- Check top left dropdown
- Should show: **K2M Sheets Templates**
- If not, click dropdown → select your new project

---

## Step 2: Enable Google Sheets API (2 minutes)

### 2.1 Search for Sheets API
- Look at **top search bar** (has magnifying glass icon, says "Search")
- Type: `Google Sheets API`
- Press Enter or click search

**What you'll see:**
- Search results page
- First result: "Google Sheets API" by Google Cloud

### 2.2 Enable the API
- Click on **"Google Sheets API"** result
- You'll see API overview page
- Look for **BLUE BUTTON** near top that says **"ENABLE"**
- Click it

**What happens:**
- Button changes to "Managing..."
- Shows spinner for 5-10 seconds
- Then changes to **"MANAGE"** (this means it's enabled!)

**Verify it's enabled:**
- You should see dashboard with "API enabled" message
- Left sidebar shows "APIs & Services" > "Dashboard"

---

## Step 3: Configure OAuth Consent Screen (3 minutes)

### 3.1 Go to OAuth Consent Screen
- In left sidebar, look for **"APIs & Services"**
- Expand it if collapsed
- Click **"OAuth consent screen"**

### 3.2 Choose User Type
- You'll see radio buttons:
  - ◉ External
  - ○ Internal
- Select **"External"** (allows you to use it yourself)
- Click **"CREATE"** button (blue, bottom right)

### 3.3 Fill in App Information (Step 1 of 4)
**App information:**
- **User Type:** External (already selected)
- **App name:** `K2M Sheets Generator`
- **User support email:** (your email - prefilled)
- **Developer contact information:**
  - Add your email address
  - Click **"ADD"** button
  - Click **"SAVE AND CONTINUE"** (bottom right)

### 3.4 Scopes (Step 2 of 4)
- Click **"SAVE AND CONTINUE"** (no changes needed - you'll add scopes later)

### 3.5 Test Users (Step 3 of 4)
- Click **"ADD USERS"**
- Add **YOUR EMAIL** (the same Google account you're using)
- Click **"ADD"**
- Click **"SAVE AND CONTINUE"**

### 3.6 Summary (Step 4 of 4)
- Review everything
- Click **"BACK TO DASHBOARD"**

**What this does:**
- Allows your Google account to use this app
- You're the only authorized user (secure!)

---

## Step 4: Create OAuth 2.0 Credentials (3 minutes)

### 4.1 Go to Credentials Page
- In left sidebar: **"APIs & Services"** > **"Credentials"**
- Click on it

### 4.2 Create OAuth Client ID
- Look for button near top: **"+ CREATE CREDENTIALS"** (blue button)
- Click it
- Dropdown appears
- Select **"OAuth client ID"**

### 4.3 Choose Application Type
You'll see different app types as cards:
- Web application
- Android
- iOS
- Chrome app
- **Desktop app**  ← SELECT THIS ONE
- Universal Windows Platform (UWP)

- Click on **"Desktop app"** card

### 4.4 Name the Client ID
- **Name:** `K2M Sheets Generator` (or leave default)
- Don't change anything else

### 4.5 Create the Credential
- Click **"CREATE"** button (blue, bottom right)

**What happens:**
- Popup appears: "OAuth client created"
- Shows your Client ID and Client Secret
- **IMPORTANT:** Look for button that says **"DOWNLOAD JSON"**
- Click it!

---

## Step 5: Download and Save Credentials (2 minutes)

### 5.1 Download the JSON File
- After clicking "DOWNLOAD JSON":
  - File downloads to your computer
  - Name will be something like: `client_secret_123456789-abcdef.json`

### 5.2 Rename the File
- Locate the downloaded file (usually in Downloads folder)
- Rename it to: **`credentials.json`**
  - Windows: Right-click > Rename > Type `credentials.json` > Enter
  - Mac: Click file name, type new name, press Enter

### 5.3 Move to Project Directory
- Move the `credentials.json` file to:
  ```
  /mnt/c/Users/OMEN/Documents/K2M/k2m-edtech-program-/
  ```

**How to move:**
- Drag and drop file into that folder
- OR copy file, navigate to folder, paste

### 5.4 Verify File is in Place
Run this command to check:
```bash
ls -lh credentials.json
```

You should see:
```
-rw-r--r-- 1 user user 2.5K Feb 16 10:30 credentials.json
```

---

## Step 6: Install Required Python Packages (1 minute)

### 6.1 Install Google Sheets API Libraries
Run this command:
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**What you'll see:**
- Download progress bars
- "Successfully installed..." messages
- Package names and versions

**Expected output:**
```
Successfully installed google-api-python-client-2.108.0
Successfully installed google-auth-2.23.4
Successfully installed google-auth-httplib2-0.2.0
Successfully installed google-auth-oauthlib-1.1.0
(and several dependency packages)
```

---

## Step 7: Run the Script! (1 minute)

### 7.1 Execute the Script
```bash
python create_google_sheets_templates.py
```

**What happens:**

**Step 1: Browser opens for OAuth**
- Your default browser opens
- Google sign-in screen appears
- Select your Google account (the same one from setup)

**Step 2: Permission Screen**
- You'll see: "Google hasn't verified this app" (this is NORMAL - it's your own app!)
- Click **"Advanced"** (small link)
- Click **"Go to K2M Sheets Generator (unsafe)"** at bottom
- On permission screen:
  - "See, edit, create, and delete all your Google Sheets spreadsheets"
  - Click **"Allow"**

**Step 3: Script Creates Sheets**
- Browser shows: "Authentication successful. You can close this window."
- Terminal shows progress:
  ```
  ✓ Authentication successful
  ✓ Created spreadsheet: K2M Cohort #1 - Operations Templates
    ID: 1ABC123xyz456
    URL: https://docs.google.com/spreadsheets/d/1ABC123xyz456
  ✓ Student Roster headers added
  ✓ Student Roster formulas added
  ✓ Student Roster data validation rules configured
  ✓ Submissions Log headers added
  ✓ Submissions Log formulas added
  ✓ Intervention Tracking headers added
  ✓ Intervention Tracking formulas added
  ✓ Progress Dashboard metrics added
  ```

**Step 4: Completion Message**
```
✅ TEMPLATE CREATION COMPLETE!

Spreadsheet URL: https://docs.google.com/spreadsheets/d/1ABC123xyz456

Next Steps:
1. Open the spreadsheet and review all 4 sheets
2. Manually set up data validation (drop-down menus)
3. Manually set up conditional formatting
4. Review formulas and adjust ranges as needed
5. Test with sample data
```

---

## Step 8: Verify the Sheets (2 minutes)

### 8.1 Open the Spreadsheet
- Click the URL shown in terminal output
- OR go to https://sheets.google.com
- Find spreadsheet named "K2M Cohort #1 - Operations Templates"

### 8.2 Check All 5 Sheets Exist
You should see tabs at bottom:
1. **Student Roster** (30+ columns)
2. **Submissions Log** (22 columns)
3. **Intervention Tracking** (23 columns)
4. **Progress Dashboard** (metrics organized)
5. **Summary** (front-page dashboard)

### 8.3 Verify Headers and Formulas
**Student Roster (Row 1):**
- Should show: Timestamp, Student ID, First Name, Last Name, Email, ... Notes
- Row 2 should have formulas in columns J, N, AA, AB, AC, AJ

**Test a formula:**
- Click cell J2 (Zone Shift)
- Formula bar should show: `=IF(AND(H2="Zone 0", I2="Zone 0"), ...)`

---

## Troubleshooting

### Problem: "credentials.json not found"
**Solution:**
- Verify file is in project directory: `ls credentials.json`
- If not, re-download from Google Cloud Console
- Make sure it's named exactly `credentials.json` (not credentials.json.txt)

### Problem: "Redirect URI mismatch" error
**Solution:**
- This is rare for Desktop app type
- If it happens, go back to credentials page
- Edit the OAuth client
- Add `http://localhost` to Authorized redirect URIs

### Problem: "API not enabled" error
**Solution:**
- Go back to Google Cloud Console
- APIs & Services > Library
- Search "Google Sheets API"
- Click **"ENABLE"**

### Problem: Script runs but no spreadsheet created
**Solution:**
- Check terminal for error messages
- Look for "ERROR:" in output
- Common issue: Network connection or quota exceeded
- Try running again after 1 minute

### Problem: OAuth authentication loop (keeps asking for permission)
**Solution:**
- Delete `token_sheets.json` file if it exists
- Run script again
- This refreshes the authentication token

---

## Security Notes

**Your credentials are SAFE because:**
- Only YOU can use them (your Google account)
- Desktop app = runs only on your computer
- token_sheets.json is auto-generated refresh token
- Never share credentials.json or token_sheets.json

**Best practices:**
- Add `credentials.json` to `.gitignore` (never commit to GitHub)
- Add `token_sheets.json` to `.gitignore`
- Store credentials.json securely (it's your personal access key)

---

## What Gets Created (File Inventory)

After setup, you'll have these new files:

```
k2m-edtech-program-/
├── credentials.json           ← OAuth credentials (KEEP SECRET)
├── token_sheets.json          ← Auto-generated refresh token
├── create_google_sheets_templates.py  ← The automation script
├── GOOGLE_SHEETS_API_SETUP.md ← This guide
├── GOOGLE_SHEETS_TEMPLATES_README.md  ← Full documentation
└── GOOGLE_SHEETS_QUICK_SETUP.md      ← Manual setup guide
```

**In your Google Drive (Sheets):**
- **K2M Cohort #1 - Operations Templates** (spreadsheet with 5 sheets)

---

## Time Estimate

| Step | Time | Cumulative |
|------|------|------------|
| Create project | 3 min | 3 min |
| Enable API | 2 min | 5 min |
| OAuth consent screen | 3 min | 8 min |
| Create credentials | 3 min | 11 min |
| Download & save file | 2 min | 13 min |
| Install packages | 1 min | 14 min |
| Run script | 1 min | 15 min |
| **TOTAL** | **15 min** | **15 min** |

---

## Success Criteria

You'll know it worked when:

✅ Browser opened and asked for Google account
✅ You clicked "Allow" for permissions
✅ Terminal showed "✅ TEMPLATE CREATION COMPLETE!"
✅ You got a spreadsheet URL
✅ Opening URL shows 5 sheets with headers
✅ Row 2 has formulas in some columns

---

## Next Steps After Setup

1. **Test with sample data:**
   - Add 2-3 fake students to Student Roster
   - Verify crisis flags trigger for anxiety >=7
   - Check cluster assignments (A-F, G-L, M-R, S-Z)

2. **Set up data validation (manual step):**
   - Open Student Roster sheet
   - Select column H (Zone Baseline)
   - Data > Data Validation
   - Dropdown > Options: Zone 0, Zone 1, Zone 2, Zone 3, Zone 4
   - Repeat for other columns with choices

3. **Set up conditional formatting (manual step):**
   - Format > Conditional formatting
   - Crisis Flag = "CRISIS" → Red background
   - Crisis Flag = "HIGH ANXIETY" → Orange background
   - Engagement Status = "Stuck" → Yellow background

4. **Connect to Google Forms (when ready):**
   - Create diagnostic form (Story 5.4)
   - Responses > Link to Sheets
   - Select "K2M Cohort #1 - Student Roster"
   - Test with sample submission

---

## FAQ

**Q: Do I need to pay for this?**
A: No. Google Sheets API free tier is generous (100 requests/day per user). You'll never hit the limit.

**Q: Can I reuse this for other cohorts?**
A: Yes! Just run `python create_google_sheets_templates.py` again. Enter new cohort name when prompted.

**Q: What if I lose credentials.json?**
A: Go back to Google Cloud Console > APIs & Services > Credentials > Download JSON again.

**Q: Can I share the spreadsheet with others?**
A: Yes! Click "Share" button > Add people. But they can't use the Python script (they need their own credentials).

**Q: Is this secure?**
A: Yes. Desktop app = only runs on your computer. Credentials never leave your machine.

**Q: Do I need to be a programmer?**
A: No. This guide is written for non-programmers. Just copy-paste commands.

---

**Need Help?**
- Check terminal output for error messages
- Verify all steps were completed
- Make sure credentials.json is in the right place
- Check that you enabled the Google Sheets API

**Still stuck?**
- Run the script with verbose output:
  ```bash
  python create_google_sheets_templates.py 2>&1 | tee output.log
  ```
- Share output.log with error messages
