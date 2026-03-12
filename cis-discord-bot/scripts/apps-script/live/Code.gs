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
 * - CONTEXT_WEBHOOK_TOKEN
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
var COL_STAGE1_NUDGE_EMAIL_SENT = 22; // V
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
  'habits_baseline',      // U
  'stage1_nudge_email_sent' // V
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
var EXAMPLE_LIBRARY_SHEET_NAME = 'Example_Library';
var INTERVENTION_LIBRARY_SHEET_NAME = 'Intervention_Library';
var OPS_HEALTH_EXPECTED_TABS = [
  'Student Roster',
  'Submissions Log',
  'Intervention Tracking',
  'Progress Dashboard',
  'Summary',
  'Example_Library',
  'Intervention_Library'
];
var SHEET_ERROR_TOKENS = ['#REF!', '#N/A', '#VALUE!', '#DIV/0!', '#NAME?', '#NUM!', '#ERROR!'];
var EXAMPLE_LIBRARY_SHEET_ALIASES = [
  'Example Library',
  'Examples Library',
  'Examples_Library',
  'example_library',
  'example library'
];
var INTERVENTION_LIBRARY_SHEET_ALIASES = [
  'Intervention Library',
  'Interventions Library',
  'Interventions_Library',
  'intervention_library',
  'intervention library'
];

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

/**
 * Task 6.2 context webhooks (deployed via Apps Script web app).
 *
 * Expects POST JSON:
 * {
 *   token: "<CONTEXT_WEBHOOK_TOKEN>",
 *   action: "getStudentContext" | "getExamplesByProfession" | "getIntervention",
 *   ...action fields...
 * }
 */
function doPost(e) {
  return withK2mErrorReporting_('doPost', function() {
    var payload = parseWebAppPayload_(e);
    var auth = validateContextWebhookToken_(payload.token);
    if (!auth.success) {
      return jsonResponse_({ success: false, error: auth.error });
    }

    var action = String(payload.action || '').trim();
    if (!action) {
      return jsonResponse_({ success: false, error: 'Missing action' });
    }

    if (action === 'getStudentContext') {
      return jsonResponse_(getStudentContext(payload.discord_id));
    }
    if (action === 'getExamplesByProfession') {
      return jsonResponse_(getExamplesByProfession(payload.profession, payload.week));
    }
    if (action === 'getIntervention') {
      return jsonResponse_(getIntervention(payload.barrier_type, payload.week));
    }

    return jsonResponse_({ success: false, error: 'Unknown action: ' + action });
  });
}

function parseWebAppPayload_(e) {
  var raw = '';
  if (e && e.postData && e.postData.contents) {
    raw = String(e.postData.contents).trim();
  }
  if (!raw) return {};

  try {
    var parsed = JSON.parse(raw);
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      return parsed;
    }
    throw new Error('Payload must be a JSON object');
  } catch (err) {
    throw new Error('Invalid JSON payload: ' + err);
  }
}

function validateContextWebhookToken_(providedToken) {
  var expected = String(getOptionalProperty_('CONTEXT_WEBHOOK_TOKEN', '') || '').trim();
  if (!expected) {
    return { success: false, error: 'CONTEXT_WEBHOOK_TOKEN not configured' };
  }

  var provided = String(providedToken || '').trim();
  if (!provided || provided !== expected) {
    return { success: false, error: 'Unauthorized' };
  }
  return { success: true };
}

function getStudentContext(discordIdInput) {
  var discordId = normalizeDiscordId_(discordIdInput);
  if (!discordId) {
    return { success: false, error: 'discord_id must be numeric' };
  }

  var spreadsheet = getTargetSpreadsheet_();
  var roster = spreadsheet.getSheetByName(SHEET_NAME);
  if (!roster) {
    return { success: false, error: 'Missing sheet: ' + SHEET_NAME };
  }

  var lastRow = roster.getLastRow();
  if (lastRow < 2) {
    return { success: false, error: 'student_not_found' };
  }

  var values = roster.getRange(2, 1, lastRow - 1, COL_HABITS).getValues();
  for (var i = 0; i < values.length; i += 1) {
    var row = values[i];
    var identity = parseDiscordIdentity_(row[COL_DISCORD_ID - 1]);
    if (identity.discord_id !== discordId) {
      continue;
    }

    var fullName = String(row[COL_NAME - 1] || '').trim();
    var situation = String(row[COL_SITUATION - 1] || '').trim();
    var goals = String(row[COL_GOALS - 1] || '').trim();
    var emotional = String(row[COL_EMOTIONAL - 1] || '').trim().toLowerCase();
    return {
      success: true,
      profile: {
        discord_id: discordId,
        discord_username: String(identity.discord_username || '').trim(),
        first_name: extractFirstName_(fullName),
        enrollment_name: fullName,
        profession: normalizeProfession_(row[COL_PROFESSION - 1]),
        zone: String(row[COL_ZONE - 1] || '').trim(),
        situation: situation,
        goals: goals,
        emotional_baseline: emotional,
        barrier_type: inferBarrierType_(situation, goals, emotional)
      }
    };
  }

  return { success: false, error: 'student_not_found' };
}

function getExamplesByProfession(professionInput, weekInput) {
  var profession = normalizeProfession_(professionInput);
  var week = parseWeekNumber_(weekInput);
  if (!profession) {
    return { success: false, error: 'profession is required' };
  }
  if (!week) {
    return { success: false, error: 'week is required' };
  }

  var spreadsheet = getTargetSpreadsheet_();
  var sheet = spreadsheet.getSheetByName(EXAMPLE_LIBRARY_SHEET_NAME);
  if (!sheet) {
    return { success: false, error: 'Missing sheet: ' + EXAMPLE_LIBRARY_SHEET_NAME };
  }

  var rows = sheet.getDataRange().getValues();
  if (!rows || rows.length < 2) {
    return { success: true, examples: [], count: 0 };
  }

  var idx = buildHeaderIndexMap_(rows[0]);
  if (
    idx.profession < 0 ||
    idx.example_text < 0 ||
    idx.week_relevant < 0
  ) {
    return { success: false, error: 'Example_Library headers are missing required columns' };
  }

  var examples = [];
  for (var i = 1; i < rows.length; i += 1) {
    var row = rows[i];
    var rowProfession = normalizeProfession_(row[idx.profession]);
    if (rowProfession !== profession) {
      continue;
    }

    var weekRelevant = String(row[idx.week_relevant] || '').trim();
    if (!weekMatchesRange_(week, weekRelevant)) {
      continue;
    }

    var exampleText = String(row[idx.example_text] || '').trim();
    if (!exampleText) {
      continue;
    }

    examples.push({
      id: idx.id >= 0 ? String(row[idx.id] || '').trim() : '',
      profession: rowProfession,
      example_text: exampleText,
      week_relevant: weekRelevant,
      habit_tag: idx.habit_tag >= 0 ? String(row[idx.habit_tag] || '').trim() : ''
    });

    if (examples.length >= 3) {
      break;
    }
  }

  return {
    success: true,
    examples: examples,
    count: examples.length
  };
}

function getIntervention(barrierTypeInput, weekInput) {
  var barrierType = normalizeBarrierType_(barrierTypeInput);
  var week = parseWeekNumber_(weekInput);
  if (!barrierType) {
    return { success: false, error: 'barrier_type is required' };
  }
  if (!week) {
    return { success: false, error: 'week is required' };
  }

  var spreadsheet = getTargetSpreadsheet_();
  var sheet = spreadsheet.getSheetByName(INTERVENTION_LIBRARY_SHEET_NAME);
  if (!sheet) {
    return { success: false, error: 'Missing sheet: ' + INTERVENTION_LIBRARY_SHEET_NAME };
  }

  var rows = sheet.getDataRange().getValues();
  if (!rows || rows.length < 2) {
    return { success: true, intervention: null };
  }

  var idx = buildHeaderIndexMap_(rows[0]);
  if (
    idx.barrier_type < 0 ||
    idx.week_range < 0 ||
    idx.intervention_text < 0
  ) {
    return { success: false, error: 'Intervention_Library headers are missing required columns' };
  }

  for (var i = 1; i < rows.length; i += 1) {
    var row = rows[i];
    var rowBarrier = normalizeBarrierType_(row[idx.barrier_type]);
    if (rowBarrier !== barrierType) {
      continue;
    }

    var weekRange = String(row[idx.week_range] || '').trim();
    if (!weekMatchesRange_(week, weekRange)) {
      continue;
    }

    var interventionText = String(row[idx.intervention_text] || '').trim();
    if (!interventionText) {
      continue;
    }

    return {
      success: true,
      intervention: {
        id: idx.id >= 0 ? String(row[idx.id] || '').trim() : '',
        barrier_type: rowBarrier,
        week_range: weekRange,
        intervention_text: interventionText
      }
    };
  }

  return { success: true, intervention: null };
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

    if (errors.length === 0 && payload.discord_id && payload.discord_id.match(/^\d+$/)) {
      var dmResult = callActivationDm_(payload.discord_id, payload.enrollment_name);
      if (!dmResult.success) {
        errors.push('activation dm failed: ' + dmResult.error);
      }
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

function callActivationDm_(discordId, fullName) {
  try {
    var botUrl = normalizeBotUrl_();
    var resp = signedFetch_(botUrl + '/api/internal/activation-dm', {
      discord_id: String(discordId || '').trim(),
      enrollment_name: String(fullName || '').trim(),
      first_session_date: String(getOptionalProperty_('COHORT_1_FIRST_SESSION_DATE', '')).trim(),
      week1_start_date: String(getOptionalProperty_('COHORT_1_START_DATE', '')).trim()
    });
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
    var response = signedFetch_(dashboardUrl, payload);
    var parsed = parseWebhookResponse_(response);
    if (!parsed.success) {
      throw new Error('apps-script-error webhook failed: ' + parsed.error);
    }
    if (
      parsed.body &&
      Object.prototype.hasOwnProperty.call(parsed.body, 'dashboard_posted') &&
      parsed.body.dashboard_posted === false
    ) {
      throw new Error('apps-script-error webhook accepted but dashboard post failed');
    }
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

function normalizeDiscordId_(value) {
  var id = String(value || '').trim();
  if (!id.match(/^\d+$/)) {
    return '';
  }
  return id;
}

function normalizeProfession_(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '_');
}

function normalizeBarrierType_(value) {
  var normalized = String(value || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '_');

  if (normalized === 'identity' || normalized === 'time' || normalized === 'relevance' || normalized === 'technical') {
    return normalized;
  }
  return '';
}

function parseWeekNumber_(value) {
  if (value === null || value === undefined) return null;
  if (typeof value === 'number' && !isNaN(value)) {
    var asNumber = Math.floor(value);
    return asNumber > 0 ? asNumber : null;
  }

  var text = String(value || '').trim();
  if (!text) return null;
  var match = text.match(/\d+/);
  if (!match) return null;

  var parsed = parseInt(match[0], 10);
  return parsed > 0 ? parsed : null;
}

function weekMatchesRange_(weekNumber, rangeText) {
  if (!weekNumber) return false;

  var raw = String(rangeText || '').trim().toLowerCase();
  if (!raw) return true;

  var matches = raw.match(/\d+/g);
  if (!matches || matches.length === 0) {
    return true;
  }
  if (matches.length === 1) {
    return weekNumber === parseInt(matches[0], 10);
  }

  var start = parseInt(matches[0], 10);
  var end = parseInt(matches[1], 10);
  if (isNaN(start) || isNaN(end)) {
    return false;
  }
  if (start > end) {
    var tmp = start;
    start = end;
    end = tmp;
  }
  return weekNumber >= start && weekNumber <= end;
}

function normalizeHeaderKey_(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '_');
}

function buildHeaderIndexMap_(headerRow) {
  var indexMap = {
    id: -1,
    profession: -1,
    example_text: -1,
    week_relevant: -1,
    habit_tag: -1,
    barrier_type: -1,
    week_range: -1,
    intervention_text: -1
  };
  for (var i = 0; i < headerRow.length; i += 1) {
    var key = normalizeHeaderKey_(headerRow[i]);
    if (Object.prototype.hasOwnProperty.call(indexMap, key)) {
      indexMap[key] = i;
    }
  }
  return indexMap;
}

function inferBarrierType_(situation, goals, emotionalBaseline) {
  var text = (
    String(situation || '') + ' ' +
    String(goals || '') + ' ' +
    String(emotionalBaseline || '')
  ).toLowerCase();

  if (!text.trim()) {
    return '';
  }

  var buckets = {
    identity: ['not technical', 'not for me', 'behind', 'intimidated', 'not smart', 'stupid', 'nervous', 'overwhelmed'],
    time: ['busy', 'no time', 'schedule', 'commitments', 'responsibilities', 'overloaded'],
    relevance: ['not relevant', 'does not apply', 'my job does not need', 'different field', 'skeptical'],
    technical: ['confusing', 'failed', 'complicated', 'don\'t know where to start', 'technical terms', 'interface']
  };

  var bestType = '';
  var bestScore = 0;
  for (var key in buckets) {
    if (!Object.prototype.hasOwnProperty.call(buckets, key)) continue;
    var terms = buckets[key];
    var score = 0;
    for (var i = 0; i < terms.length; i += 1) {
      if (text.indexOf(terms[i]) >= 0) {
        score += 1;
      }
    }
    if (score > bestScore) {
      bestScore = score;
      bestType = key;
    }
  }
  return bestType;
}

function jsonResponse_(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload || {}))
    .setMimeType(ContentService.MimeType.JSON);
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
 * Run once to set context webhook token without exposing it in code:
 * setContextWebhookToken('<shared token used by llm_integration CONTEXT_ENGINE_WEBHOOK_TOKEN>')
 */
function setContextWebhookToken(token) {
  if (!token || !String(token).trim()) {
    throw new Error('setContextWebhookToken requires a non-empty value');
  }
  PropertiesService.getScriptProperties().setProperty(
    'CONTEXT_WEBHOOK_TOKEN',
    String(token).trim()
  );
}

/**
 * Non-destructive schema repair:
 * - Keeps all existing data rows
 * - Rewrites row-1 headers (A:V) to runtime canonical labels
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
 * Clears only data rows (row 2+) in A:V.
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
 * Apply runtime-aligned dropdown automation for Student Roster A:V.
 * - Clears old/misaligned validations in A2:V
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
 * 1) Rewrites A1:V1 runtime headers
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
 * Read-only health review for the bound operations spreadsheet.
 *
 * Checks:
 * - tab presence/visibility
 * - Student Roster + context library headers
 * - error tokens in key tabs (A1:Z200)
 * - dropdown contract integrity on Student Roster row 2
 * - Confirmed rows missing activation fields
 */
function reviewOpsSheetHealth() {
  return withK2mErrorReporting_('reviewOpsSheetHealth', function() {
    var spreadsheet = getTargetSpreadsheet_();
    var sheets = spreadsheet.getSheets();
    var actualTabs = sheets.map(function(s) { return s.getName(); });
    var hiddenTabs = sheets
      .filter(function(s) { return s.isSheetHidden(); })
      .map(function(s) { return s.getName(); });

    var missingTabs = OPS_HEALTH_EXPECTED_TABS.filter(function(name) {
      return actualTabs.indexOf(name) < 0;
    });
    var extraTabs = actualTabs.filter(function(name) {
      return OPS_HEALTH_EXPECTED_TABS.indexOf(name) < 0;
    });

    var headerChecks = {
      student_roster: verifyHeadersMatch_(
        spreadsheet.getSheetByName(SHEET_NAME),
        RUNTIME_ROSTER_HEADERS
      ),
      example_library: verifyHeadersMatch_(
        spreadsheet.getSheetByName(EXAMPLE_LIBRARY_SHEET_NAME),
        ['id', 'profession', 'example_text', 'week_relevant', 'habit_tag']
      ),
      intervention_library: verifyHeadersMatch_(
        spreadsheet.getSheetByName(INTERVENTION_LIBRARY_SHEET_NAME),
        ['id', 'barrier_type', 'week_range', 'intervention_text']
      )
    };

    var errorScanTabs = [
      SHEET_NAME,
      SUBMISSIONS_LOG_SHEET_NAME,
      INTERVENTION_TRACKING_SHEET_NAME,
      'Progress Dashboard',
      'Summary',
      EXAMPLE_LIBRARY_SHEET_NAME,
      INTERVENTION_LIBRARY_SHEET_NAME
    ];
    var errorScan = {};
    for (var i = 0; i < errorScanTabs.length; i += 1) {
      var tabName = errorScanTabs[i];
      var tabSheet = spreadsheet.getSheetByName(tabName);
      errorScan[tabName] = scanSheetErrors_(tabSheet, 26, 200);
    }

    var rosterQuality = inspectRosterQuality_(spreadsheet.getSheetByName(SHEET_NAME));
    var dropdowns = verifyRuntimeDropdowns_(spreadsheet.getSheetByName(SHEET_NAME));

    return {
      success: true,
      action: 'ops_sheet_health_review',
      spreadsheet_id: spreadsheet.getId(),
      spreadsheet_name: spreadsheet.getName(),
      structure: {
        expected_tabs: OPS_HEALTH_EXPECTED_TABS,
        actual_tabs: actualTabs,
        missing_tabs: missingTabs,
        extra_tabs: extraTabs,
        hidden_tabs: hiddenTabs
      },
      headers: headerChecks,
      errors: errorScan,
      roster_quality: rosterQuality,
      dropdowns: dropdowns
    };
  });
}

/**
 * One-click safe repair for the known live-sheet issues.
 *
 * Applies:
 * - canonical Student Roster headers/dropdowns
 * - context library tab presence
 * - emotional baseline normalization for known legacy values
 * - dashboard error hardening for average formulas
 * - intervention retention-date formula hardening
 * - summary crisis-phone text correction
 *
 * Returns post-repair health review.
 */
function repairOpsSheetHealth() {
  return withK2mErrorReporting_('repairOpsSheetHealth', function() {
    var headerResult = repairStudentRosterHeaders();
    var libraryResult = ensureContextLibraryTabs();
    var emotionalResult = normalizeRosterEmotionalBaselineValues();
    var dashboardResult = repairProgressDashboardRuntimeFormulas();
    var retentionResult = repairInterventionRetentionDateFormulas();
    var summaryPhonesResult = repairSummaryCrisisPhones();
    var postCheck = reviewOpsSheetHealth();

    return {
      success: true,
      action: 'ops_sheet_health_repaired',
      applied: {
        roster_headers: headerResult,
        context_libraries: libraryResult,
        emotional_normalization: emotionalResult,
        dashboard_runtime_formulas: dashboardResult,
        retention_formulas: retentionResult,
        summary_phones: summaryPhonesResult
      },
      post_check: postCheck
    };
  });
}

/**
 * Normalizes known legacy emotional baseline values to runtime options.
 * Current mapping:
 * - hopeful -> curious
 */
function normalizeRosterEmotionalBaselineValues() {
  return withK2mErrorReporting_('normalizeRosterEmotionalBaselineValues', function() {
    var spreadsheet = getTargetSpreadsheet_();
    var sheet = spreadsheet.getSheetByName(SHEET_NAME);
    if (!sheet) throw new Error('Missing sheet: ' + SHEET_NAME);

    var lastRow = sheet.getLastRow();
    if (lastRow < 2) {
      return {
        success: true,
        action: 'normalize_emotional_baseline',
        updated_rows: 0,
        updates: []
      };
    }

    var values = sheet.getRange(2, COL_EMOTIONAL, lastRow - 1, 1).getValues();
    var mapping = {
      hopeful: 'curious'
    };
    var updates = [];
    for (var i = 0; i < values.length; i += 1) {
      var raw = String(values[i][0] || '').trim();
      var normalized = raw.toLowerCase();
      if (!raw) continue;
      if (!Object.prototype.hasOwnProperty.call(mapping, normalized)) continue;

      var target = mapping[normalized];
      if (raw === target) continue;
      values[i][0] = target;
      updates.push({
        row: i + 2,
        from: raw,
        to: target
      });
    }

    if (updates.length > 0) {
      sheet.getRange(2, COL_EMOTIONAL, values.length, 1).setValues(values);
    }

    return {
      success: true,
      action: 'normalize_emotional_baseline',
      updated_rows: updates.length,
      updates: updates
    };
  });
}

/**
 * Rewrites legacy Progress Dashboard formulas to current runtime schema.
 *
 * Notes:
 * - Uses Student Roster runtime columns (A:V).
 * - Replaces legacy references to deprecated columns (AE:AJ).
 * - Uses Submissions/Interventions tabs for engagement and anxiety trends.
 */
function repairProgressDashboardRuntimeFormulas() {
  return withK2mErrorReporting_('repairProgressDashboardRuntimeFormulas', function() {
    var spreadsheet = getTargetSpreadsheet_();
    var sheet = spreadsheet.getSheetByName('Progress Dashboard');
    if (!sheet) {
      return {
        success: false,
        action: 'repair_progress_dashboard_runtime_formulas',
        error: 'Missing sheet: Progress Dashboard'
      };
    }

    // Optional label updates to match the repaired metric semantics.
    var labelUpdates = [
      { cell: 'A31', value: 'Anxiety Band: High (8-10)' },
      { cell: 'A32', value: 'Anxiety Band: Moderate (6-7)' },
      { cell: 'A33', value: 'Anxiety Band: Mild (4-5)' },
      { cell: 'A34', value: 'Anxiety Band: Low (1-3)' },
      { cell: 'A42', value: 'Any Habit Baseline Set (not \"None yet\")' },
      { cell: 'A53', value: 'Students with Artifact Submission' },
      { cell: 'A54', value: 'Artifact Submission Entries' },
      { cell: 'A55', value: 'Students Without Artifact Submission' },
      { cell: 'A56', value: 'Artifact Participation Rate' },
      { cell: 'A57', value: 'Parents with Email on File' }
    ];
    for (var i = 0; i < labelUpdates.length; i += 1) {
      sheet.getRange(labelUpdates[i].cell).setValue(labelUpdates[i].value);
    }

    var formulaUpdates = [
      { cell: 'B6', formula: '=COUNTIF(\'Student Roster\'!L:L,"Confirmed")' },
      { cell: 'B7', formula: '=COUNTIF(\'Student Roster\'!L:L,"Pending")' },
      { cell: 'B8', formula: '=COUNTIF(\'Student Roster\'!L:L,"Unverifiable")' },

      { cell: 'B12', formula: '=COUNTIF(\'Student Roster\'!F:F,"Zone 0")' },
      { cell: 'B13', formula: '=COUNTIF(\'Student Roster\'!F:F,"Zone 1")' },
      { cell: 'B14', formula: '=COUNTIF(\'Student Roster\'!F:F,"Zone 2")' },
      { cell: 'B15', formula: '=COUNTIF(\'Student Roster\'!F:F,"Zone 3")' },
      { cell: 'B16', formula: '=COUNTIF(\'Student Roster\'!F:F,"Zone 4")' },

      { cell: 'B17', formula: '=COUNTIF(\'Student Roster\'!S:S,"Zone 0")' },
      { cell: 'B18', formula: '=COUNTIF(\'Student Roster\'!S:S,"Zone 1")' },
      { cell: 'B19', formula: '=COUNTIF(\'Student Roster\'!S:S,"Zone 2")' },
      { cell: 'B20', formula: '=COUNTIF(\'Student Roster\'!S:S,"Zone 3")' },
      { cell: 'B21', formula: '=COUNTIF(\'Student Roster\'!S:S,"Zone 4")' },
      {
        cell: 'B22',
        formula: '=IFERROR((COUNTIFS(\'Student Roster\'!F:F,"Zone 0",\'Student Roster\'!S:S,"Zone 1")+COUNTIFS(\'Student Roster\'!F:F,"Zone 1",\'Student Roster\'!S:S,"Zone 2")+COUNTIFS(\'Student Roster\'!F:F,"Zone 2",\'Student Roster\'!S:S,"Zone 3")+COUNTIFS(\'Student Roster\'!F:F,"Zone 3",\'Student Roster\'!S:S,"Zone 4"))/MAX(COUNTIF(\'Student Roster\'!S:S,"Zone *"),1),0)'
      },

      { cell: 'B26', formula: '=IFERROR(AVERAGEIF(\'Student Roster\'!T2:T,">=0"),0)' },
      { cell: 'B27', formula: '=IFERROR(AVERAGEIF(\'Intervention Tracking\'!S3:S,">=0"),0)' },
      { cell: 'B28', formula: '=IFERROR(COUNTIF(\'Intervention Tracking\'!L3:L,"Improved")/MAX(COUNTA(\'Intervention Tracking\'!L3:L),1),0)' },
      { cell: 'B29', formula: '=IFERROR(COUNTIF(\'Intervention Tracking\'!L3:L,"Escalated")/MAX(COUNTA(\'Intervention Tracking\'!L3:L),1),0)' },
      { cell: 'B30', formula: '=COUNTIF(\'Student Roster\'!T2:T,">=7")' },
      { cell: 'B31', formula: '=COUNTIF(\'Student Roster\'!T2:T,">=8")' },
      { cell: 'B32', formula: '=COUNTIFS(\'Student Roster\'!T2:T,">=6",\'Student Roster\'!T2:T,"<=7")' },
      { cell: 'B33', formula: '=COUNTIFS(\'Student Roster\'!T2:T,">=4",\'Student Roster\'!T2:T,"<=5")' },
      { cell: 'B34', formula: '=COUNTIFS(\'Student Roster\'!T2:T,">=1",\'Student Roster\'!T2:T,"<=3")' },

      { cell: 'B38', formula: '=IFERROR(COUNTIF(\'Student Roster\'!U:U,"Pause")/MAX(COUNTA(\'Student Roster\'!B:B)-1,1),0)' },
      { cell: 'B39', formula: '=IFERROR(COUNTIF(\'Student Roster\'!U:U,"Context")/MAX(COUNTA(\'Student Roster\'!B:B)-1,1),0)' },
      { cell: 'B40', formula: '=IFERROR(COUNTIF(\'Student Roster\'!U:U,"Iterate")/MAX(COUNTA(\'Student Roster\'!B:B)-1,1),0)' },
      { cell: 'B41', formula: '=IFERROR(COUNTIF(\'Student Roster\'!U:U,"Think First")/MAX(COUNTA(\'Student Roster\'!B:B)-1,1),0)' },
      { cell: 'B42', formula: '=IFERROR(COUNTIFS(\'Student Roster\'!U:U,"<>",\'Student Roster\'!U:U,"<>None yet")/MAX(COUNTA(\'Student Roster\'!B:B)-1,1),0)' },

      { cell: 'B46', formula: '=IFERROR(COUNTUNIQUE(FILTER(\'Submissions Log\'!E3:E,LEN(\'Submissions Log\'!E3:E)>0))/MAX(COUNTA(\'Student Roster\'!B:B)-1,1),0)' },
      { cell: 'B47', formula: '=IFERROR(COUNTA(FILTER(\'Submissions Log\'!A3:A,LEN(\'Submissions Log\'!A3:A)>0))/MAX(COUNTUNIQUE(FILTER(\'Submissions Log\'!E3:E,LEN(\'Submissions Log\'!E3:E)>0)),1),0)' },
      { cell: 'B48', formula: '=IFERROR(COUNTIF(\'Submissions Log\'!J3:J,"/frame")/MAX(COUNTA(\'Student Roster\'!B:B)-1,1),0)' },
      { cell: 'B49', formula: '=IFERROR(COUNTUNIQUE(FILTER(\'Submissions Log\'!E3:E,\'Submissions Log\'!H3:H="Artifact Submission"))/MAX(COUNTA(\'Student Roster\'!B:B)-1,1),0)' },

      { cell: 'B53', formula: '=COUNTUNIQUE(FILTER(\'Submissions Log\'!E3:E,\'Submissions Log\'!H3:H="Artifact Submission"))' },
      { cell: 'B54', formula: '=COUNTIF(\'Submissions Log\'!H3:H,"Artifact Submission")' },
      { cell: 'B55', formula: '=MAX((COUNTA(\'Student Roster\'!B:B)-1)-B53,0)' },
      { cell: 'B56', formula: '=IFERROR(B53/MAX(COUNTA(\'Student Roster\'!B:B)-1,1),0)' },
      { cell: 'B57', formula: '=COUNTIF(\'Student Roster\'!J:J,"*@*")' }
    ];
    for (var j = 0; j < formulaUpdates.length; j += 1) {
      sheet.getRange(formulaUpdates[j].cell).setFormula(formulaUpdates[j].formula);
    }

    return {
      success: true,
      action: 'repair_progress_dashboard_runtime_formulas',
      updated_formulas: formulaUpdates.length,
      updated_labels: labelUpdates.length,
      formula_cells: formulaUpdates.map(function(item) { return item.cell; }),
      label_cells: labelUpdates.map(function(item) { return item.cell; })
    };
  });
}

/**
 * Backward-compatible wrapper retained for existing runbooks.
 */
function hardenProgressDashboardAverages() {
  return repairProgressDashboardRuntimeFormulas();
}

/**
 * Fixes legacy retention-date formulas in Intervention Tracking column W.
 *
 * - Converts W2 from broken formula to descriptor text if needed.
 * - Rewrites legacy per-row formulas `=B{row}+180` to guarded form:
 *   `=IF(B{row}=\"\",\"\",B{row}+180)`.
 */
function repairInterventionRetentionDateFormulas() {
  return withK2mErrorReporting_('repairInterventionRetentionDateFormulas', function() {
    var spreadsheet = getTargetSpreadsheet_();
    var sheet = spreadsheet.getSheetByName(INTERVENTION_TRACKING_SHEET_NAME);
    if (!sheet) {
      return {
        success: false,
        action: 'repair_intervention_retention_formulas',
        error: 'Missing sheet: ' + INTERVENTION_TRACKING_SHEET_NAME
      };
    }

    var descriptorCell = sheet.getRange('W2');
    var descriptorFormula = String(descriptorCell.getFormula() || '').trim();
    var descriptorUpdated = false;
    if (descriptorFormula === '=B2+180') {
      descriptorCell.setValue('Auto: timestamp + 180 days');
      descriptorUpdated = true;
    }

    var lastRow = Math.max(3, sheet.getMaxRows());
    var formulaRange = sheet.getRange(3, 23, lastRow - 2, 1);
    var formulas = formulaRange.getFormulas();
    var rewrites = 0;

    for (var i = 0; i < formulas.length; i += 1) {
      var row = i + 3;
      var existing = String(formulas[i][0] || '').trim();
      var legacy = '=B' + row + '+180';
      if (existing !== legacy) continue;
      formulas[i][0] = '=IF(B' + row + '="","",B' + row + '+180)';
      rewrites += 1;
    }

    if (rewrites > 0) {
      formulaRange.setFormulas(formulas);
    }

    return {
      success: true,
      action: 'repair_intervention_retention_formulas',
      descriptor_updated: descriptorUpdated,
      rewritten_formulas: rewrites
    };
  });
}

/**
 * Converts Summary crisis phone cells from accidental formulas to plain text.
 * Looks for the "KENYA CRISIS RESOURCES" block and fixes the next 3 rows in column B.
 */
function repairSummaryCrisisPhones() {
  return withK2mErrorReporting_('repairSummaryCrisisPhones', function() {
    var spreadsheet = getTargetSpreadsheet_();
    var sheet = spreadsheet.getSheetByName('Summary');
    if (!sheet) {
      return {
        success: false,
        action: 'repair_summary_crisis_phones',
        error: 'Missing sheet: Summary'
      };
    }

    var headingRow = findRowByExactText_(sheet, 1, 'KENYA CRISIS RESOURCES (Level 4 response protocol)');
    if (!headingRow) {
      return {
        success: false,
        action: 'repair_summary_crisis_phones',
        error: 'Crisis resources heading not found'
      };
    }

    var fixed = [];
    for (var i = 1; i <= 3; i += 1) {
      var row = headingRow + i;
      var cell = sheet.getRange(row, 2);
      var formula = String(cell.getFormula() || '').trim();
      var display = String(cell.getDisplayValue() || '').trim();
      var candidate = '';

      if (formula && formula.charAt(0) === '+') {
        candidate = formula;
      } else if (display.indexOf("'+") === 0) {
        candidate = display.substring(1);
      }

      if (!candidate) continue;
      // Force plain-text storage so leading + is not reinterpreted as formula.
      cell.setNumberFormat('@');
      cell.setValue(candidate);
      fixed.push('B' + row);
    }

    return {
      success: true,
      action: 'repair_summary_crisis_phones',
      heading_row: headingRow,
      fixed_cells: fixed
    };
  });
}

/**
 * Verify runtime alignment without changing data.
 * Checks:
 * - Student Roster headers A:V
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

function verifyHeadersMatch_(sheet, expectedHeaders) {
  if (!sheet) {
    return {
      status: 'missing_sheet',
      expected: expectedHeaders,
      actual: []
    };
  }
  var expectedLen = expectedHeaders.length;
  var actual = sheet.getRange(1, 1, 1, expectedLen).getValues()[0].map(function(v) {
    return String(v || '').trim();
  });
  return {
    status: arraysEqual_(actual, expectedHeaders) ? 'ok' : 'mismatch',
    expected: expectedHeaders,
    actual: actual
  };
}

function scanSheetErrors_(sheet, maxCols, maxRows) {
  if (!sheet) {
    return { status: 'missing_sheet', count: 0, sample: [] };
  }
  var cols = Math.max(1, Math.min(maxCols, sheet.getMaxColumns()));
  var rows = Math.max(1, Math.min(maxRows, sheet.getMaxRows()));
  var values = sheet.getRange(1, 1, rows, cols).getDisplayValues();
  var hits = [];
  for (var r = 0; r < values.length; r += 1) {
    var row = values[r];
    for (var c = 0; c < row.length; c += 1) {
      var txt = String(row[c] || '').trim();
      if (SHEET_ERROR_TOKENS.indexOf(txt) >= 0) {
        hits.push({
          cell: columnToLetter_(c + 1) + (r + 1),
          error: txt
        });
      }
    }
  }
  return {
    status: 'ok',
    count: hits.length,
    sample: hits.slice(0, 15)
  };
}

function inspectRosterQuality_(sheet) {
  if (!sheet) {
    return { status: 'missing_sheet' };
  }

  var lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    return {
      status: 'ok',
      data_rows: 0,
      confirmed_rows_missing_required: [],
      invalid_emotional_values: []
    };
  }

  var values = sheet.getRange(2, 1, lastRow - 1, RUNTIME_ROSTER_HEADERS.length).getValues();
  var emotionalAllowed = ['excited', 'nervous', 'curious', 'skeptical', 'overwhelmed'];
  var invalidEmotional = [];
  var confirmedMissing = [];

  for (var i = 0; i < values.length; i += 1) {
    var row = values[i];
    var rowNum = i + 2;

    var emotional = String(row[COL_EMOTIONAL - 1] || '').trim();
    if (emotional && emotionalAllowed.indexOf(emotional) < 0) {
      invalidEmotional.push({
        row: rowNum,
        value: emotional
      });
    }

    var payment = String(row[COL_PAYMENT - 1] || '').trim();
    if (payment === 'Confirmed') {
      var missing = [];
      if (!String(row[COL_DISCORD_ID - 1] || '').trim()) missing.push('discord_id');
      if (!String(row[COL_ACTIVATED_AT - 1] || '').trim()) missing.push('activated_at');
      if (missing.length > 0) {
        confirmedMissing.push({
          row: rowNum,
          missing: missing
        });
      }
    }
  }

  return {
    status: 'ok',
    data_rows: values.length,
    confirmed_rows_missing_required: confirmedMissing,
    invalid_emotional_values: invalidEmotional
  };
}

function findRowByExactText_(sheet, columnNumber, expectedValue) {
  var lastRow = sheet.getLastRow();
  if (lastRow < 1) return 0;
  var values = sheet.getRange(1, columnNumber, lastRow, 1).getDisplayValues();
  var expected = String(expectedValue || '').trim();
  for (var i = 0; i < values.length; i += 1) {
    var got = String(values[i][0] || '').trim();
    if (got === expected) {
      return i + 1;
    }
  }
  return 0;
}

function columnToLetter_(column) {
  var temp = '';
  var letter = '';
  while (column > 0) {
    temp = (column - 1) % 26;
    letter = String.fromCharCode(temp + 65) + letter;
    column = (column - temp - 1) / 26;
  }
  return letter;
}

/**
 * Fresh-cohort reset helper (safe default):
 * - Creates a timestamped backup copy of Student Roster tab
 * - Reapplies runtime headers + runtime dropdown validations
 * - Clears Student Roster data rows (row 2+ in A:V)
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
    'APPS_SCRIPT_ALERT_EMAIL',
    'CONTEXT_WEBHOOK_TOKEN'
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
 * Task 6.2 non-destructive setup helper.
 *
 * Creates missing context library tabs with required headers:
 * - Example_Library: id, profession, example_text, week_relevant, habit_tag
 * - Intervention_Library: id, barrier_type, week_range, intervention_text
 *
 * Safety:
 * - Never edits existing formulas/data rows.
 * - Only writes headers when tab is newly created, or when existing tab has no data rows.
 * - If an existing tab has data + header mismatch, reports manual review required.
 */
function ensureContextLibraryTabs() {
  return withK2mErrorReporting_('ensureContextLibraryTabs', function() {
    var spreadsheet = getTargetSpreadsheet_();
    var results = [];

    results.push(ensureContextLibrarySheet_(
      spreadsheet,
      EXAMPLE_LIBRARY_SHEET_NAME,
      ['id', 'profession', 'example_text', 'week_relevant', 'habit_tag'],
      EXAMPLE_LIBRARY_SHEET_ALIASES
    ));
    results.push(ensureContextLibrarySheet_(
      spreadsheet,
      INTERVENTION_LIBRARY_SHEET_NAME,
      ['id', 'barrier_type', 'week_range', 'intervention_text'],
      INTERVENTION_LIBRARY_SHEET_ALIASES
    ));

    return {
      success: true,
      spreadsheet_id: spreadsheet.getId(),
      action: 'ensure_context_library_tabs',
      results: results
    };
  });
}

function ensureContextLibrarySheet_(spreadsheet, sheetName, expectedHeaders, legacyAliases) {
  var sheet = spreadsheet.getSheetByName(sheetName);
  var created = false;
  var renamedFrom = '';

  if (!sheet) {
    sheet = findSheetByAliases_(spreadsheet, legacyAliases || []);
    if (sheet) {
      renamedFrom = sheet.getName();
      sheet.setName(sheetName);
    }
  }

  if (!sheet) {
    sheet = spreadsheet.insertSheet(sheetName);
    created = true;
  }

  var maxCols = sheet.getMaxColumns();
  if (maxCols < expectedHeaders.length) {
    sheet.insertColumnsAfter(maxCols, expectedHeaders.length - maxCols);
  }

  var currentHeaders = sheet.getRange(1, 1, 1, expectedHeaders.length).getValues()[0]
    .map(function(v) { return String(v || '').trim(); });
  var expected = expectedHeaders.map(function(v) { return String(v || '').trim(); });
  var headersMatch = arraysEqual_(currentHeaders, expected);

  if (created) {
    sheet.getRange(1, 1, 1, expectedHeaders.length).setValues([expectedHeaders]);
    sheet.setFrozenRows(1);
    sheet.autoResizeColumns(1, expectedHeaders.length);
    return {
      sheet: sheetName,
      status: 'created',
      headers_written: true
    };
  }

  if (headersMatch) {
    return {
      sheet: sheetName,
      status: renamedFrom ? 'renamed_legacy_ok' : 'ok',
      headers_written: false,
      renamed_from: renamedFrom || null
    };
  }

  var lastRow = sheet.getLastRow();
  var hasDataRows = lastRow > 1;
  if (!hasDataRows) {
    sheet.getRange(1, 1, 1, expectedHeaders.length).setValues([expectedHeaders]);
    sheet.setFrozenRows(1);
    sheet.autoResizeColumns(1, expectedHeaders.length);
    return {
      sheet: sheetName,
      status: 'headers_repaired_empty_sheet',
      headers_written: true,
      renamed_from: renamedFrom || null
    };
  }

  return {
    sheet: sheetName,
    status: 'manual_review_required',
    headers_written: false,
    renamed_from: renamedFrom || null,
    expected_headers: expected,
    current_headers: currentHeaders
  };
}

function findSheetByAliases_(spreadsheet, aliases) {
  if (!aliases || !aliases.length) return null;

  var lookup = {};
  for (var i = 0; i < aliases.length; i += 1) {
    var key = normalizeSheetName_(aliases[i]);
    if (key) lookup[key] = true;
  }

  var sheets = spreadsheet.getSheets();
  for (var j = 0; j < sheets.length; j += 1) {
    var name = sheets[j].getName();
    if (lookup[normalizeSheetName_(name)]) {
      return sheets[j];
    }
  }

  return null;
}

function normalizeSheetName_(value) {
  return String(value || '').trim().toLowerCase().replace(/[\s_\-]+/g, '');
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
