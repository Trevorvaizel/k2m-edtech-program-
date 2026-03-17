# Apps Script Patch Kit (Task 7.8)

This folder contains the canonical patch for Apps Script runtime error surfacing.

## File

- `task-78-error-reporting.gs`

## What it adds

- Signed webhook helper using `X-K2M-Signature` (HMAC-SHA256).
- `reportAppsScriptError(functionName, err, extra)` that posts to:
  - `DASHBOARD_WEBHOOK_URL` Script Property, or
  - `BOT_URL + /api/internal/apps-script-error`.
- Fallback email alert via optional `APPS_SCRIPT_ALERT_EMAIL`.
- `withK2mErrorReporting(functionName, fn)` wrapper utility.

## Required Script Properties

- `BOT_URL` (example: `https://kira-bot-production.up.railway.app`)
- `WEBHOOK_SECRET` (must match Railway `WEBHOOK_SECRET`)

Optional:
- `DASHBOARD_WEBHOOK_URL`
- `APPS_SCRIPT_ALERT_EMAIL`

## How to use in existing project

1. Add `task-78-error-reporting.gs` to your Apps Script project.
2. Wrap critical functions with:
   - `withK2mErrorReporting('functionName', function() { ... })`
3. Keep your business logic unchanged inside the wrapper.

### Example

```javascript
function activateStudent(rowNumber) {
  return withK2mErrorReporting('activateStudent', function() {
    // Existing activateStudent logic
  });
}
```

