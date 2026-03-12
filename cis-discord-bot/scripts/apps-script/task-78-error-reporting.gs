/**
 * Task 7.8 Apps Script patch:
 * - Signed webhook helper (HMAC-SHA256, X-K2M-Signature)
 * - Centralized Apps Script runtime error reporting
 * - Wrapper utility to instrument existing functions
 *
 * Required Script Properties:
 *   BOT_URL                     e.g. https://kira-bot-production.up.railway.app
 *   WEBHOOK_SECRET              must match Railway WEBHOOK_SECRET
 *   DASHBOARD_WEBHOOK_URL       optional; defaults to BOT_URL + /api/internal/apps-script-error
 *   APPS_SCRIPT_ALERT_EMAIL     optional fallback email for MailApp alerts
 */

function _k2mGetPropertyOrThrow(key) {
  var value = PropertiesService.getScriptProperties().getProperty(key);
  if (!value) {
    throw new Error('Missing Script Property: ' + key);
  }
  return value;
}

function _k2mHex(bytes) {
  return bytes.map(function(b) {
    return ('0' + (b & 0xff).toString(16)).slice(-2);
  }).join('');
}

function _k2mSignedFetch(url, payloadObj) {
  var payloadJson = JSON.stringify(payloadObj || {});
  var secret = _k2mGetPropertyOrThrow('WEBHOOK_SECRET');
  var signatureBytes = Utilities.computeHmacSha256Signature(
    payloadJson,
    secret,
    Utilities.Charset.UTF_8
  );
  var signatureHex = _k2mHex(signatureBytes);

  return UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'X-K2M-Signature': 'sha256=' + signatureHex
    },
    payload: payloadJson,
    muteHttpExceptions: true
  });
}

function reportAppsScriptError(functionName, err, extra) {
  var props = PropertiesService.getScriptProperties();
  var botUrl = _k2mGetPropertyOrThrow('BOT_URL').replace(/\/+$/, '');
  var webhookUrl = props.getProperty('DASHBOARD_WEBHOOK_URL') ||
    (botUrl + '/api/internal/apps-script-error');

  var message = (err && err.stack) ? String(err.stack) : String(err);
  var payload = {
    type: 'apps_script_error',
    fn: String(functionName || 'unknown'),
    error: message,
    extra: extra || null,
    at: new Date().toISOString()
  };

  try {
    var resp = _k2mSignedFetch(webhookUrl, payload);
    var code = resp.getResponseCode();
    if (code < 200 || code >= 300) {
      throw new Error('Error webhook returned HTTP ' + code + ': ' + resp.getContentText());
    }
  } catch (webhookErr) {
    var fallbackEmail = props.getProperty('APPS_SCRIPT_ALERT_EMAIL');
    if (fallbackEmail) {
      MailApp.sendEmail({
        to: fallbackEmail,
        subject: '[K2M] Apps Script error: ' + payload.fn,
        body: [
          'Function: ' + payload.fn,
          '',
          'Primary error:',
          payload.error,
          '',
          'Webhook delivery error:',
          String(webhookErr)
        ].join('\n')
      });
    }
  }
}

function withK2mErrorReporting(functionName, fn) {
  try {
    return fn();
  } catch (err) {
    reportAppsScriptError(functionName, err);
    throw err;
  }
}

/**
 * Integration pattern:
 *
 * function activateStudent(rowNumber) {
 *   return withK2mErrorReporting('activateStudent', function() {
 *     // Existing logic unchanged
 *   });
 * }
 *
 * function onEdit(e) {
 *   return withK2mErrorReporting('onEdit', function() {
 *     // Existing logic unchanged
 *   });
 * }
 */
