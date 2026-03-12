# K2M Enrollment Automation v2 (Live Script)

This folder is linked to the new Apps Script project created for Task 7.8.

## Linked IDs

- Script ID: `1DhzxAcO3FGZ1wjAsO4cOBHs8uoTFYgPPQPD7oAwrLqaX8c1iwnjHHH1b`
- Target roster sheet ID (runtime): `16tLQbGUF9mI2z2cHxlwmGce6Npui0C5w8e1y46uanH0`

## What this script does

- Watches Column `L` (`Payment Status`) via installable onEdit trigger.
- On `Confirmed`, it:
  - calls `/api/internal/role-upgrade`
  - calls `/api/internal/preload-student`
  - sends activation email
  - writes activation outcome to Columns `M` and `O`
- Reports runtime errors to `/api/internal/apps-script-error` with signed webhook.
- Exposes task `6.2` context webhooks via web-app `doPost`:
  - `getStudentContext(discord_id)`
  - `getExamplesByProfession(profession, week)`
  - `getIntervention(barrier_type, week)`
  - token-authenticated via `CONTEXT_WEBHOOK_TOKEN`

## One-time setup (required)

1. Open script editor:
   - `https://script.google.com/d/1DhzxAcO3FGZ1wjAsO4cOBHs8uoTFYgPPQPD7oAwrLqaX8c1iwnjHHH1b/edit`
2. Run function: `seedK2MDefaults`
3. In Project Settings -> Script properties, add:
   - `WEBHOOK_SECRET` = same value as Railway `WEBHOOK_SECRET`
   - `CONTEXT_WEBHOOK_TOKEN` = same value as bot env `CONTEXT_ENGINE_WEBHOOK_TOKEN`
4. Run function: `installOnEditTrigger`
5. Approve Google authorization prompts.

Optional validation:
- Run `smokeTestInternalWebhooks` and confirm response includes HTTP status fields.
- Deploy as web app and test a signed `POST` body with:
  - `action`
  - `token`
  - action-specific fields

## Context library tabs required for task 6.2

- `Example_Library` tab:
  - required headers: `id, profession, example_text, week_relevant, habit_tag`
- `Intervention_Library` tab:
  - required headers: `id, barrier_type, week_range, intervention_text`

The bot side calls these through `CONTEXT_ENGINE_WEBHOOK_URL` and `CONTEXT_ENGINE_WEBHOOK_TOKEN`.

Safe one-click helper (Apps Script editor):
- Run `ensureContextLibraryTabs`
- It creates missing tabs and headers without touching existing data/formulas.
- It also renames common legacy tab names (for example `Example Library`) to canonical runtime names.

## Ops health helpers (run from Apps Script UI)

- `reviewOpsSheetHealth`
  - Read-only health audit:
    - tab presence/visibility
    - runtime headers
    - formula error tokens (`#REF!`, `#VALUE!`, etc.)
    - dropdown rules
    - `Confirmed` rows missing activation fields

- `repairOpsSheetHealth`
  - One-click safe repair bundle:
    - repairs runtime roster headers/dropdowns
    - ensures context library tabs
    - normalizes known emotional baseline legacy values
    - hardens dashboard averages against `#DIV/0!`
    - repairs intervention retention date formulas
    - converts crisis phone formula cells to plain text
  - Returns a post-repair `reviewOpsSheetHealth` report.

- `normalizeRosterEmotionalBaselineValues`
  - Targeted data cleanup for known legacy emotional values
  - Current mapping: `hopeful -> curious`

- `hardenProgressDashboardAverages`
  - Backward-compatible wrapper (now delegates to full dashboard repair)

- `repairProgressDashboardRuntimeFormulas`
  - Rewrites legacy Progress Dashboard formulas to runtime-aligned columns/data sources.
  - Removes dependency on deprecated `Student Roster` legacy columns (`AE:AJ`).

- `repairInterventionRetentionDateFormulas`
  - Fixes `Intervention Tracking` column `W` retention formulas (`W2` descriptor + guarded formulas on row `3+`)

- `repairSummaryCrisisPhones`
  - Fixes `Summary` crisis contact cells where `+254...` was interpreted as formula

## Schema maintenance helpers (run from Apps Script UI)

- `repairStudentRosterHeaders`
  - Non-destructive.
  - Rewrites `Student Roster` headers `A:U` to runtime canonical names.
  - Keeps all existing data rows.

- `backupAndRecreateStudentRosterSheet`
  - Destructive (with automatic backup).
  - Copies current `Student Roster` to a timestamped backup tab, then recreates a clean `Student Roster` tab with runtime headers.

- `clearStudentRosterDataRows`
  - Clears data rows (row `2+`) in `A:U` while keeping header row.

- `applyRuntimeRosterDropdowns`
  - Clears old validation rules in `A2:U`.
  - Reapplies runtime-aligned dropdowns for:
    - `profession`
    - `zone`
    - `emotional_baseline`
    - `payment_status`
    - `zone_verification`
    - `anxiety_level`
    - `habits_baseline`

- `alignRuntimeRosterSchema`
  - One-click alignment:
    - rewrites runtime headers (`A1:U1`)
    - reapplies runtime-aligned dropdowns

- `verifyRuntimeRosterAlignment`
  - Read-only verification report for runtime readiness:
    - checks `Student Roster` headers (`A:U`)
    - checks runtime dropdown rules on row `2`
    - checks installable trigger `onEditInstallable`
    - checks required/recommended script properties presence

- `resetForFreshCohort`
  - Safe reset for post-testing / next cohort prep:
    - creates backup tab: `Student Roster_pre_reset_<timestamp>`
    - reapplies runtime headers + dropdowns on `Student Roster`
    - clears `Student Roster` data rows (`row 2+`, columns `A:U`)
    - clears historical rows in:
      - `Submissions Log` (`row 3+`)
      - `Intervention Tracking` (`row 3+`)
  - Leaves `Progress Dashboard` and `Summary` structure intact.

## CLI commands used from this folder

```powershell
npx.cmd --yes @google/clasp push -f
npx.cmd --yes @google/clasp version "Task 7.8 v2"
npx.cmd --yes @google/clasp deploy -d "Task 7.8 v2"
```
