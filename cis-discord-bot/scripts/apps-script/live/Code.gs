/**
 * K2M Enrollment Automation v2 (Task 7.8 aligned)
 *
 * Flow:
 * - Installable onEdit trigger watches Column L (Payment Status)
 * - When status changes to Confirmed:
 *   1) Role upgrade webhook -> /api/internal/role-upgrade
 *   2) Preload webhook      -> /api/internal/preload-student
 *   3) Activation email     -> MailApp
 * - Runtime errors are signed and sent to:
 *   /api/internal/apps-script-error
 *
 * Required Script Properties:
 * - WEBHOOK_SECRET
 *
 * Optional Script Properties:
 * - BOT_URL
 * - DASHBOARD_WEBHOOK_URL
 * - APPS_SCRIPT_ALERT_EMAIL
 * - COHORT_ID
 * - COHORT_START_DATE
 */

var SHEET_NAME = 'Student Roster';
var DEFAULT_SHEET_ID = '16tLQbGUF9mI2z2cHxlwmGce6Npui0C5w8e1y46uanH0';
var DEFAULT_BOT_URL = 'https://kira-bot-production.up.railway.app';

// 1-based column indexes
var COL_NAME = 1;           // A
var COL_EMAIL = 2;          // B
var COL_PHONE = 3;          // C
var COL_DISCORD_ID = 4;     // D (discord_id|discord_username)
var COL_PROFESSION = 5;     // E
var COL_ZONE = 6;           // F
var COL_SITUATION = 7;      // G
var COL_GOALS = 8;          // H
var COL_EMOTIONAL = 9;      // I
var COL_PARENT_EMAIL = 10;  // J
var COL_MPESA_CODE = 11;    // K
var COL_PAYMENT = 12;       // L
var COL_NOTES = 13;         // M
var COL_CREATED_AT = 14;    // N
var COL_ACTIVATED_AT = 15;  // O
var COL_SUBMIT_TOKEN = 16;  // P
var COL_TOKEN_EXPIRY = 17;  // Q
var COL_INVITE_CODE = 18;   // R
var COL_ZONE_VERIFY = 19;   // S
var COL_ANXIETY = 20;       // T
var COL_HABITS = 21;        // U
var RUNTIME_ROSTER_HEADERS = [
  'enrollment_name',      // A
  'enrollment_email',     // B
  'phone_number',         // C
  'discord_id',           // D (or discord_id|discord_username)
  'profession',           // E
  'zone',                 // F
  'situation',            // G
  'goals',                // H
  'emotional_baseline',   // I
  'parent_email',         // J
  'mpesa_code',           // K
  'payment_status',       // L
  'notes',                // M
  'created_at',           // N
  'activated_at',         // O
  'submit_token',         // P
  'token_expiry',         // Q
  'invite_code',          // R
  'zone_verification',    // S
  'anxiety_level',        // T
  'habits_baseline'       // U
];
var RUNTIME_DROPDOWNS = [
  {
    key: 'profession',
    col: COL_PROFESSION,
    options: [
      'teacher',
      'entrepreneur',
      'university_student',
      'working_professional',
      'gap_year_student',
      'other'
    ]
  },
  {
    key: 'zone',
    col: COL_ZONE,
    options: ['Zone 0', 'Zone 1', 'Zone 2', 'Zone 3', 'Zone 4']
  },
  {
    key: 'emotional_baseline',
    col: COL_EMOTIONAL,
    options: ['excited', 'nervous', 'curious', 'skeptical', 'overwhelmed']
  },
  {
    key: 'payment_status',
    col: COL_PAYMENT,
    options: ['Lead', 'Waitlisted', 'Enrolled', 'Pending', 'Unverifiable', 'Confirmed']
  },
  {
    key: 'zone_verification',
    col: COL_ZONE_VERIFY,
    options: ['Zone 0', 'Zone 1', 'Zone 2', 'Zone 3', 'Zone 4']
  },
  {
    key: 'anxiety_level',
    col: COL_ANXIETY,
    options: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
  },
  {
    key: 'habits_baseline',
    col: COL_HABITS,
    options: ['Pause', 'Context', 'Iterate', 'Think First', 'None yet']
  }
];
var SUBMISSIONS_LOG_SHEET_NAME = 'Submissions Log';
var INTERVENTION_TRACKING_SHEET_NAME = 'Intervention Tracking';

function installOnEditTrigger() {
  var spreadsheet = getTargetSpreadsheet_();
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i += 1) {
    if (triggers[i].getHandlerFunction() === 'onEditInstallable') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }

  ScriptApp.newTrigger('onEditInstallable')
    .forSpreadsheet(spreadsheet)
    .onEdit()
    .create();
}

function getTargetSpreadsheet_() {
  var sheetId = String(getOptionalProperty_('SHEET_ID', DEFAULT_SHEET_ID)).trim();
  return SpreadsheetApp.openById(sheetId);
}

function onEditInstallable(e) {
  return withK2mErrorReporting_('onEditInstallable', function() {
    if (!e || !e.range) return;

    var range = e.range;
    var sheet = range.getSheet();
    if (!sheet || sheet.getName() !== SHEET_NAME) return;
    if (range.getColumn() !== COL_PAYMENT) return;

    var value = String((e.value !== undefined ? e.value : range.getValue()) || '')
      .trim()
      .toLowerCase();
    if (value !== 'confirmed') return;

    activateStudentByRow_(sheet, range.getRow());
  });
}

function activateStudentByRow_(sheet, row) {
  return withK2mErrorReporting_('activateStudentByRow_', function() {
    var activatedAt = sheet.getRange(row, COL_ACTIVATED_AT).getValue();
    if (activatedAt) {
      Logger.log('Row ' + row + ' already activated at ' + activatedAt + '. Skipping.');
      return;
    }

    var rowValues = sheet.getRange(row, 1, 1, COL_HABITS).getValues()[0];
    var payload = buildPreloadPayload_(rowValues);
    var errors = [];

    if (payload.discord_id && payload.discord_id.match(/^\d+$/)) {
      var roleResult = callRoleUpgrade_(payload.discord_id);
      if (!roleResult.success) {
        errors.push('role upgrade failed: ' + roleResult.error);
      }
    } else {
      errors.push('discord_id missing or invalid; student may not have joined Discord');
    }

    var preloadResult = callPreloadStudent_(payload);
    if (!preloadResult.success) {
      errors.push('preload failed: ' + preloadResult.error);
    }

    var emailResult = sendActivationEmail_(payload.enrollment_email, payload.enrollment_name);
    if (!emailResult.success) {
      errors.push('activation email failed: ' + emailResult.error);
    }

    if (errors.length > 0) {
      var note = 'ACTIVATION ERRORS: ' + errors.join(' | ');
      sheet.getRange(row, COL_NOTES).setValue(note);
      reportAppsScriptError_('activateStudentByRow_', note, {
        row: row,
        email: payload.enrollment_email
      });
      return;
    }

    sheet.getRange(row, COL_ACTIVATED_AT).setValue(new Date());
    sheet.getRange(row, COL_NOTES).setValue('Activated via Apps Script v2');
  });
}

function buildPreloadPayload_(rowValues) {
  var identity = parseDiscordIdentity_(rowValues[COL_DISCORD_ID - 1]);
  var email = String(rowValues[COL_EMAIL - 1] || '').trim();
  var name = String(rowValues[COL_NAME - 1] || '').trim();
  var inviteCode = String(rowValues[COL_INVITE_CODE - 1] || '').trim();
  var paymentStatus = String(rowValues[COL_PAYMENT - 1] || '').trim();
  var cohortId = String(getOptionalProperty_('COHORT_ID', 'cohort-1')).trim();
  var startDate = String(getOptionalProperty_('COHORT_START_DATE', '')).trim();

  var discordId = identity.discord_id;
  if (!discordId) {
    discordId = '__pending__' + (email || 'unknown');
  }

  return {
    enrollment_email: email,
    enrollment_name: name,
    last_name: extractLastName_(name),
    invite_code: inviteCode,
    discord_id: discordId,
    discord_username: identity.discord_username,
    cohort_id: cohortId,
    start_date: startDate,
    enrollment_status: 'enrolled',
    payment_status: paymentStatus || 'Confirmed',
    profession: String(rowValues[COL_PROFESSION - 1] || '').trim(),
    zone: String(rowValues[COL_ZONE - 1] || '').trim(),
    situation: String(rowValues[COL_SITUATION - 1] || '').trim(),
    goals: String(rowValues[COL_GOALS - 1] || '').trim(),
    emotional_baseline: String(rowValues[COL_EMOTIONAL - 1] || '').trim(),
    parent_email: String(rowValues[COL_PARENT_EMAIL - 1] || '').trim(),
    mpesa_code: String(rowValues[COL_MPESA_CODE - 1] || '').trim(),
    phone_number: String(rowValues[COL_PHONE - 1] || '').trim()
  };
}

function callRoleUpgrade_(discordId) {
  try {
    var botUrl = normalizeBotUrl_();
    var resp = signedFetch_(botUrl + '/api/internal/role-upgrade', {
      discord_id: String(discordId).trim()
    });
    return parseWebhookResponse_(resp);
  } catch (err) {
    return { success: false, error: String(err) };
  }
}

function callPreloadStudent_(payload) {
  try {
    var botUrl = normalizeBotUrl_();
    var resp = signedFetch_(botUrl + '/api/internal/preload-student', payload);
    return parseWebhookResponse_(resp);
  } catch (err) {
    return { success: false, error: String(err) };
  }
}

function parseWebhookResponse_(resp) {
  var code = resp.getResponseCode();
  var text = String(resp.getContentText() || '');
  var body = {};
  try {
    body = text ? JSON.parse(text) : {};
  } catch (_ignored) {
    body = {};
  }

  if (code >= 200 && code < 300 && body.success !== false) {
    return { success: true, status: code, body: body };
  }
  return {
    success: false,
    status: code,
    error: (body && body.error) ? String(body.error) : ('HTTP ' + code + ': ' + text)
  };
}

function sendActivationEmail_(email, fullName) {
  try {
    var to = String(email || '').trim();
    if (!to) {
      return { success: false, error: 'missing enrollment email' };
    }
    var firstName = extractFirstName_(fullName);
    MailApp.sendEmail({
      to: to,
      subject: 'Welcome to K2M Cohort 1',
      htmlBody: [
        '<p>Hi ' + escapeHtml_(firstName) + ',</p>',
        '<p>Your payment is confirmed and your activation is complete.</p>',
        '<p>Open Discord and continue in your cohort channels.</p>',
        '<p>- Trevor, K2M</p>'
      ].join('')
    });
    return { success: true };
  } catch (err) {
    return { success: false, error: String(err) };
  }
}

function reportAppsScriptError_(functionName, errOrMessage, extra) {
  var message = (errOrMessage && errOrMessage.stack)
    ? String(errOrMessage.stack)
    : String(errOrMessage);

  var payload = {
    type: 'apps_script_error',
    fn: String(functionName || 'unknown'),
    error: message,
    extra: extra || null,
    at: new Date().toISOString()
  };

  try {
    var dashboardUrl = getOptionalProperty_('DASHBOARD_WEBHOOK_URL', '');
    if (!dashboardUrl) {
      dashboardUrl = normalizeBotUrl_() + '/api/internal/apps-script-error';
    }
    signedFetch_(dashboardUrl, payload);
  } catch (webhookErr) {
    var fallbackEmail = getOptionalProperty_('APPS_SCRIPT_ALERT_EMAIL', '');
    if (fallbackEmail) {
      MailApp.sendEmail({
        to: fallbackEmail,
        subject: '[K2M] Apps Script error: ' + payload.fn,
        body: [
          'Function: ' + payload.fn,
          '',
          'Error:',
          payload.error,
          '',
          'Webhook delivery error:',
          String(webhookErr)
        ].join('\n')
      });
    }
  }
}

function withK2mErrorReporting_(functionName, fn) {
  try {
    return fn();
  } catch (err) {
    reportAppsScriptError_(functionName, err);
    throw err;
  }
}

function signedFetch_(url, payloadObj) {
  var body = JSON.stringify(payloadObj || {});
  var secret = getRequiredProperty_('WEBHOOK_SECRET');
  var sigBytes = Utilities.computeHmacSha256Signature(
    body,
    secret,
    Utilities.Charset.UTF_8
  );
  var sigHex = bytesToHex_(sigBytes);

  return UrlFetchApp.fetch(String(url).trim(), {
    method: 'post',
    contentType: 'application/json',
    headers: { 'X-K2M-Signature': 'sha256=' + sigHex },
    payload: body,
    muteHttpExceptions: true
  });
}

function parseDiscordIdentity_(cellValue) {
  var raw = String(cellValue || '').trim();
  if (!raw) return { discord_id: '', discord_username: '' };

  var parts = raw.split('|');
  var first = String(parts[0] || '').trim();
  var second = String(parts[1] || '').trim();

  if (first.match(/^\d+$/)) {
    return { discord_id: first, discord_username: second };
  }
  if (raw.match(/^\d+$/)) {
    return { discord_id: raw, discord_username: '' };
  }
  return { discord_id: '', discord_username: second || raw };
}

function getRequiredProperty_(key) {
  var value = PropertiesService.getScriptProperties().getProperty(key);
  if (!value) {
    throw new Error('Missing Script Property: ' + key);
  }
  return value;
}

function getOptionalProperty_(key, fallback) {
  var value = PropertiesService.getScriptProperties().getProperty(key);
  return value ? value : fallback;
}

function normalizeBotUrl_() {
  var url = String(getOptionalProperty_('BOT_URL', DEFAULT_BOT_URL)).trim();
  return url.replace(/\/+$/, '');
}

function bytesToHex_(bytes) {
  return bytes.map(function(b) {
    return ('0' + (b & 0xff).toString(16)).slice(-2);
  }).join('');
}

function extractFirstName_(fullName) {
  var parts = String(fullName || '').trim().split(/\s+/);
  return parts[0] || 'there';
}

function extractLastName_(fullName) {
  var parts = String(fullName || '').trim().split(/\s+/);
  if (parts.length < 2) return '';
  return parts.slice(1).join(' ');
}

function escapeHtml_(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Run once after push to seed non-secret defaults.
 */
function seedK2MDefaults() {
  var props = PropertiesService.getScriptProperties();
  props.setProperties({
    SHEET_ID: DEFAULT_SHEET_ID,
    BOT_URL: 'https://kira-bot-production.up.railway.app',
    DASHBOARD_WEBHOOK_URL: 'https://kira-bot-production.up.railway.app/api/internal/apps-script-error',
    COHORT_ID: 'cohort-1',
    COHORT_START_DATE: '2026-03-16',
    APPS_SCRIPT_ALERT_EMAIL: 'trevor@k2mlabs.com'
  }, true);
}

/**
 * Run once to set secret without exposing it in code:
 * setWebhookSecret('<value from Railway WEBHOOK_SECRET>')
 */
function setWebhookSecret(secret) {
  if (!secret || !String(secret).trim()) {
    throw new Error('setWebhookSecret requires a non-empty value');
  }
  PropertiesService.getScriptProperties().setProperty(
    'WEBHOOK_SECRET',
    String(secret).trim()
  );
}

/**
 * Non-destructive schema repair:
 * - Keeps all existing data rows
 * - Rewrites row-1 headers (A:U) to runtime canonical labels
 */
function repairStudentRosterHeaders() {
  return withK2mErrorReporting_('repairStudentRosterHeaders', function() {
    var spreadsheet = getTargetSpreadsheet_();
    var sheet = spreadsheet.getSheetByName(SHEET_NAME);
    if (!sheet) {
      throw new Error('Missing sheet: ' + SHEET_NAME);
    }
    ensureRuntimeRosterColumns_(sheet);
    sheet.getRange(1, 1, 1, RUNTIME_ROSTER_HEADERS.length).setValues([RUNTIME_ROSTER_HEADERS]);
    sheet.setFrozenRows(1);
    applyRuntimeRosterDropdowns_(sheet);
    return {
      success: true,
      action: 'headers_repaired',
      spreadsheet_id: spreadsheet.getId(),
      sheet_name: SHEET_NAME,
      columns_set: RUNTIME_ROSTER_HEADERS.length
    };
  });
}

/**
 * Destructive rebuild with backup:
 * - Copies current Student Roster tab to a timestamped backup tab
 * - Deletes old Student Roster tab
 * - Creates a fresh Student Roster tab with runtime headers only
 */
function backupAndRecreateStudentRosterSheet() {
  return withK2mErrorReporting_('backupAndRecreateStudentRosterSheet', function() {
    var spreadsheet = getTargetSpreadsheet_();
    var oldSheet = spreadsheet.getSheetByName(SHEET_NAME);
    var backupName = '';

    if (oldSheet) {
      var stamp = Utilities.formatDate(
        new Date(),
        Session.getScriptTimeZone(),
        'yyyyMMdd_HHmmss'
      );
      backupName = SHEET_NAME + '_backup_' + stamp;
      oldSheet.copyTo(spreadsheet).setName(backupName);
      spreadsheet.deleteSheet(oldSheet);
    }

    var newSheet = spreadsheet.insertSheet(SHEET_NAME, 0);
    ensureRuntimeRosterColumns_(newSheet);
    newSheet.getRange(1, 1, 1, RUNTIME_ROSTER_HEADERS.length).setValues([RUNTIME_ROSTER_HEADERS]);
    newSheet.setFrozenRows(1);
    newSheet.autoResizeColumns(1, RUNTIME_ROSTER_HEADERS.length);
    applyRuntimeRosterDropdowns_(newSheet);

    return {
      success: true,
      action: 'sheet_recreated',
      spreadsheet_id: spreadsheet.getId(),
      sheet_name: SHEET_NAME,
      backup_sheet: backupName || null
    };
  });
}

/**
 * Clears only data rows (row 2+) in A:U.
 * Header row remains intact.
 */
function clearStudentRosterDataRows() {
  return withK2mErrorReporting_('clearStudentRosterDataRows', function() {
    var spreadsheet = getTargetSpreadsheet_();
    var sheet = spreadsheet.getSheetByName(SHEET_NAME);
    if (!sheet) {
      throw new Error('Missing sheet: ' + SHEET_NAME);
    }
    ensureRuntimeRosterColumns_(sheet);
    var maxRows = sheet.getMaxRows();
    if (maxRows > 1) {
      sheet.getRange(2, 1, maxRows - 1, RUNTIME_ROSTER_HEADERS.length).clearContent();
    }
    return {
      success: true,
      action: 'data_rows_cleared',
      spreadsheet_id: spreadsheet.getId(),
      sheet_name: SHEET_NAME,
      cleared_rows: Math.max(0, maxRows - 1)
    };
  });
}

/**
 * Apply runtime-aligned dropdown automation for Student Roster A:U.
 * - Clears old/misaligned validations in A2:U
 * - Applies dropdowns for runtime fields (profession/zone/payment/etc.)
 * - Uses allowInvalid=true so existing out-of-band values are not blocked
 */
function applyRuntimeRosterDropdowns() {
  return withK2mErrorReporting_('applyRuntimeRosterDropdowns', function() {
    var spreadsheet = getTargetSpreadsheet_();
    var sheet = spreadsheet.getSheetByName(SHEET_NAME);
    if (!sheet) {
      throw new Error('Missing sheet: ' + SHEET_NAME);
    }
    ensureRuntimeRosterColumns_(sheet);
    var summary = applyRuntimeRosterDropdowns_(sheet);
    summary.spreadsheet_id = spreadsheet.getId();
    summary.sheet_name = SHEET_NAME;
    return summary;
  });
}

/**
 * One-click runtime alignment:
 * 1) Rewrites A1:U1 runtime headers
 * 2) Reapplies runtime dropdown validations
 */
function alignRuntimeRosterSchema() {
  return withK2mErrorReporting_('alignRuntimeRosterSchema', function() {
    var headerResult = repairStudentRosterHeaders();
    var dropdownResult = applyRuntimeRosterDropdowns();
    return {
      success: true,
      action: 'runtime_schema_aligned',
      header_result: headerResult,
      dropdown_result: dropdownResult
    };
  });
}

/**
 * Verify runtime alignment without changing data.
 * Checks:
 * - Student Roster headers A:U
 * - Runtime dropdown validation rules on row 2
 * - installable onEdit trigger presence
 * - required/recommended script properties presence
 */
function verifyRuntimeRosterAlignment() {
  return withK2mErrorReporting_('verifyRuntimeRosterAlignment', function() {
    var spreadsheet = getTargetSpreadsheet_();
    var sheet = spreadsheet.getSheetByName(SHEET_NAME);
    if (!sheet) {
      throw new Error('Missing sheet: ' + SHEET_NAME);
    }

    var headerCheck = verifyRuntimeHeaders_(sheet);
    var dropdownCheck = verifyRuntimeDropdowns_(sheet);
    var triggerCheck = verifyOnEditTrigger_();
    var propertyCheck = verifyRuntimeScriptProperties_();

    var ok = (
      headerCheck.mismatch_count === 0 &&
      dropdownCheck.missing_count === 0 &&
      dropdownCheck.criteria_mismatch_count === 0 &&
      dropdownCheck.options_mismatch_count === 0 &&
      triggerCheck.installed === true &&
      propertyCheck.missing_required.length === 0
    );

    return {
      success: ok,
      action: 'runtime_roster_alignment_verified',
      spreadsheet_id: spreadsheet.getId(),
      sheet_name: SHEET_NAME,
      checks: {
        headers: headerCheck,
        dropdowns: dropdownCheck,
        trigger: triggerCheck,
        properties: propertyCheck
      }
    };
  });
}

/**
 * Fresh-cohort reset helper (safe default):
 * - Creates a timestamped backup copy of Student Roster tab
 * - Reapplies runtime headers + runtime dropdown validations
 * - Clears Student Roster data rows (row 2+ in A:U)
 * - Clears historical activity rows in:
 *   - Submissions Log (row 3+)
 *   - Intervention Tracking (row 3+)
 *
 * Keeps:
 * - Header/descriptor rows
 * - Progress Dashboard formulas/layout
 * - Summary tab content
 */
function resetForFreshCohort() {
  return withK2mErrorReporting_('resetForFreshCohort', function() {
    var spreadsheet = getTargetSpreadsheet_();
    var roster = spreadsheet.getSheetByName(SHEET_NAME);
    if (!roster) {
      throw new Error('Missing sheet: ' + SHEET_NAME);
    }

    var stamp = Utilities.formatDate(
      new Date(),
      Session.getScriptTimeZone(),
      'yyyyMMdd_HHmmss'
    );
    var backupName = SHEET_NAME + '_pre_reset_' + stamp;
    roster.copyTo(spreadsheet).setName(backupName);

    ensureRuntimeRosterColumns_(roster);
    roster.getRange(1, 1, 1, RUNTIME_ROSTER_HEADERS.length).setValues([RUNTIME_ROSTER_HEADERS]);
    roster.setFrozenRows(1);
    var dropdownResult = applyRuntimeRosterDropdowns_(roster);

    var rosterMaxRows = roster.getMaxRows();
    var rosterRowsCleared = 0;
    if (rosterMaxRows > 1) {
      rosterRowsCleared = rosterMaxRows - 1;
      roster.getRange(2, 1, rosterRowsCleared, RUNTIME_ROSTER_HEADERS.length).clearContent();
    }

    var submissionsClear = clearSheetRowsFrom_(spreadsheet, SUBMISSIONS_LOG_SHEET_NAME, 3);
    var interventionsClear = clearSheetRowsFrom_(spreadsheet, INTERVENTION_TRACKING_SHEET_NAME, 3);

    return {
      success: true,
      action: 'fresh_cohort_reset_complete',
      spreadsheet_id: spreadsheet.getId(),
      backup_sheet: backupName,
      roster_rows_cleared: rosterRowsCleared,
      dropdown_result: dropdownResult,
      log_clears: [submissionsClear, interventionsClear]
    };
  });
}

function ensureRuntimeRosterColumns_(sheet) {
  var missingCols = RUNTIME_ROSTER_HEADERS.length - sheet.getMaxColumns();
  if (missingCols > 0) {
    sheet.insertColumnsAfter(sheet.getMaxColumns(), missingCols);
  }
}

function applyRuntimeRosterDropdowns_(sheet) {
  var maxRows = sheet.getMaxRows();
  if (maxRows < 2) {
    sheet.insertRowsAfter(1, 1);
    maxRows = sheet.getMaxRows();
  }
  var dataRows = maxRows - 1;

  // Clear legacy validation rules that were attached to old template semantics.
  sheet.getRange(2, 1, dataRows, RUNTIME_ROSTER_HEADERS.length).clearDataValidations();

  var applied = [];
  for (var i = 0; i < RUNTIME_DROPDOWNS.length; i += 1) {
    var spec = RUNTIME_DROPDOWNS[i];
    var rule = SpreadsheetApp.newDataValidation()
      .requireValueInList(spec.options, true)
      .setAllowInvalid(true)
      .build();
    sheet.getRange(2, spec.col, dataRows, 1).setDataValidation(rule);
    applied.push({
      key: spec.key,
      column: spec.col,
      options: spec.options.length
    });
  }

  return {
    success: true,
    action: 'runtime_dropdowns_applied',
    rows_covered: dataRows,
    dropdown_columns_applied: applied.length,
    applied: applied
  };
}

function verifyRuntimeHeaders_(sheet) {
  var actual = sheet.getRange(1, 1, 1, RUNTIME_ROSTER_HEADERS.length).getValues()[0];
  var mismatches = [];
  for (var i = 0; i < RUNTIME_ROSTER_HEADERS.length; i += 1) {
    var expected = String(RUNTIME_ROSTER_HEADERS[i]);
    var got = String(actual[i] || '').trim();
    if (got !== expected) {
      mismatches.push({
        column: i + 1,
        expected: expected,
        actual: got
      });
    }
  }
  return {
    expected_columns: RUNTIME_ROSTER_HEADERS.length,
    mismatch_count: mismatches.length,
    mismatches: mismatches
  };
}

function verifyRuntimeDropdowns_(sheet) {
  var maxRows = sheet.getMaxRows();
  if (maxRows < 2) {
    return {
      inspected_row: null,
      missing_count: RUNTIME_DROPDOWNS.length,
      criteria_mismatch_count: 0,
      options_mismatch_count: 0,
      missing: RUNTIME_DROPDOWNS.map(function(d) {
        return { key: d.key, column: d.col, reason: 'row_2_missing' };
      }),
      criteria_mismatches: [],
      options_mismatches: []
    };
  }

  var missing = [];
  var criteriaMismatches = [];
  var optionsMismatches = [];

  for (var i = 0; i < RUNTIME_DROPDOWNS.length; i += 1) {
    var spec = RUNTIME_DROPDOWNS[i];
    var rule = sheet.getRange(2, spec.col).getDataValidation();
    if (!rule) {
      missing.push({ key: spec.key, column: spec.col, reason: 'no_validation_rule' });
      continue;
    }

    var type = rule.getCriteriaType();
    if (type !== SpreadsheetApp.DataValidationCriteria.VALUE_IN_LIST) {
      criteriaMismatches.push({
        key: spec.key,
        column: spec.col,
        expected_type: 'VALUE_IN_LIST',
        actual_type: String(type)
      });
      continue;
    }

    var criteriaValues = rule.getCriteriaValues() || [];
    var actualOptions = (criteriaValues[0] || []).map(function(v) {
      return String(v);
    });
    var expectedOptions = spec.options.map(function(v) {
      return String(v);
    });
    if (!arraysEqual_(actualOptions, expectedOptions)) {
      optionsMismatches.push({
        key: spec.key,
        column: spec.col,
        expected_options: expectedOptions,
        actual_options: actualOptions
      });
    }
  }

  return {
    inspected_row: 2,
    missing_count: missing.length,
    criteria_mismatch_count: criteriaMismatches.length,
    options_mismatch_count: optionsMismatches.length,
    missing: missing,
    criteria_mismatches: criteriaMismatches,
    options_mismatches: optionsMismatches
  };
}

function verifyOnEditTrigger_() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i += 1) {
    if (
      triggers[i].getHandlerFunction() === 'onEditInstallable' &&
      triggers[i].getEventType() === ScriptApp.EventType.ON_EDIT
    ) {
      return { installed: true };
    }
  }
  return { installed: false };
}

function verifyRuntimeScriptProperties_() {
  var props = PropertiesService.getScriptProperties().getProperties();
  var required = ['WEBHOOK_SECRET'];
  var recommended = [
    'SHEET_ID',
    'BOT_URL',
    'DASHBOARD_WEBHOOK_URL',
    'COHORT_ID',
    'COHORT_START_DATE',
    'APPS_SCRIPT_ALERT_EMAIL'
  ];

  var missingRequired = [];
  var missingRecommended = [];

  for (var i = 0; i < required.length; i += 1) {
    if (!props[required[i]]) {
      missingRequired.push(required[i]);
    }
  }
  for (var j = 0; j < recommended.length; j += 1) {
    if (!props[recommended[j]]) {
      missingRecommended.push(recommended[j]);
    }
  }

  return {
    missing_required: missingRequired,
    missing_recommended: missingRecommended
  };
}

function arraysEqual_(a, b) {
  if (!a || !b) return false;
  if (a.length !== b.length) return false;
  for (var i = 0; i < a.length; i += 1) {
    if (String(a[i]) !== String(b[i])) return false;
  }
  return true;
}

function clearSheetRowsFrom_(spreadsheet, sheetName, startRow) {
  var sheet = spreadsheet.getSheetByName(sheetName);
  if (!sheet) {
    return { sheet: sheetName, status: 'missing' };
  }

  var maxRows = sheet.getMaxRows();
  var maxCols = sheet.getMaxColumns();
  if (maxRows < startRow) {
    return {
      sheet: sheetName,
      status: 'ok',
      cleared_rows: 0,
      start_row: startRow
    };
  }

  var rowsToClear = maxRows - startRow + 1;
  sheet.getRange(startRow, 1, rowsToClear, maxCols).clearContent();
  return {
    sheet: sheetName,
    status: 'cleared',
    cleared_rows: rowsToClear,
    start_row: startRow
  };
}

/**
 * Manual smoke test from Apps Script editor.
 */
function smokeTestInternalWebhooks() {
  return withK2mErrorReporting_('smokeTestInternalWebhooks', function() {
    var botUrl = normalizeBotUrl_();
    var roleRes = signedFetch_(botUrl + '/api/internal/role-upgrade', { discord_id: '0' });
    var errRes = signedFetch_(botUrl + '/api/internal/apps-script-error', {
      type: 'apps_script_error',
      fn: 'smokeTestInternalWebhooks',
      error: 'manual smoke test'
    });
    return {
      role_upgrade_http: roleRes.getResponseCode(),
      apps_script_error_http: errRes.getResponseCode()
    };
  });
}
