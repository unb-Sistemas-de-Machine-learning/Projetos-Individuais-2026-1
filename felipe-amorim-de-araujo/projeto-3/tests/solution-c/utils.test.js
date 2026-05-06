'use strict';

const {
  isValidIssue,
  buildPrompt,
  parseGeminiResponse,
  validateClassification,
  isValidSchema,
  buildFallbackClassification,
  processWithRetry,
  routeToSlackChannel,
  formatSlackMessage,
  formatSheetsRow,
} = require('../../solutions/solution-c/utils');

// ─── isValidIssue ────────────────────────────────────────────────────────────

describe('isValidIssue', () => {
  test('returns true for issue with a title', () => {
    expect(isValidIssue({ title: 'App crashes on login' })).toBe(true);
  });

  test('returns false for missing title field', () => {
    expect(isValidIssue({ body: 'some body' })).toBe(false);
  });

  test('returns false for empty title string', () => {
    expect(isValidIssue({ title: '   ' })).toBe(false);
  });

  test('returns false for null input', () => {
    expect(isValidIssue(null)).toBe(false);
  });

  test('returns false for undefined input', () => {
    expect(isValidIssue(undefined)).toBe(false);
  });
});

// ─── buildPrompt ─────────────────────────────────────────────────────────────

describe('buildPrompt', () => {
  const baseIssue = {
    title: 'App crashes on login',
    body: 'When clicking login the app throws a 500 error.',
    labels: [{ name: 'bug' }, { name: 'critical' }],
    repository: { name: 'my-app' },
  };

  test('includes title in prompt', () => {
    expect(buildPrompt(baseIssue)).toContain('App crashes on login');
  });

  test('includes body in prompt', () => {
    expect(buildPrompt(baseIssue)).toContain('throws a 500 error');
  });

  test('includes label names in prompt', () => {
    const prompt = buildPrompt(baseIssue);
    expect(prompt).toContain('bug');
    expect(prompt).toContain('critical');
  });

  test('includes repository name in prompt', () => {
    expect(buildPrompt(baseIssue)).toContain('my-app');
  });

  test('handles missing body with placeholder', () => {
    expect(buildPrompt({ title: 'Some issue' })).toContain('(no body provided)');
  });

  test('handles missing labels gracefully', () => {
    expect(buildPrompt({ title: 'Some issue', body: 'desc', labels: [] })).toContain('(none)');
  });

  test('handles string labels array', () => {
    const prompt = buildPrompt({ title: 'Issue', labels: ['bug', 'help wanted'] });
    expect(prompt).toContain('bug');
    expect(prompt).toContain('help wanted');
  });

  test('handles completely empty issue', () => {
    const prompt = buildPrompt({});
    expect(prompt).toContain('(no title)');
    expect(typeof prompt).toBe('string');
  });

  test('prompt requests JSON-only response', () => {
    expect(buildPrompt(baseIssue)).toContain('Return ONLY the JSON object');
  });
});

// ─── parseGeminiResponse ─────────────────────────────────────────────────────

describe('parseGeminiResponse', () => {
  const validJson = JSON.stringify({
    type: 'bug',
    severity: 'critical',
    component: 'backend',
    confidence: 0.92,
    low_confidence: false,
    summary: 'App crashes on login due to a 500 error',
    reasoning: 'Title mentions crash, body mentions 500 error in production',
  });

  test('parses valid JSON string', () => {
    const result = parseGeminiResponse(validJson);
    expect(result.type).toBe('bug');
    expect(result.severity).toBe('critical');
    expect(result.component).toBe('backend');
    expect(result.confidence).toBe(0.92);
    expect(result.low_confidence).toBe(false);
  });

  test('strips markdown code block before parsing', () => {
    const wrapped = `\`\`\`json\n${validJson}\n\`\`\``;
    expect(parseGeminiResponse(wrapped).type).toBe('bug');
  });

  test('strips markdown code block without language hint', () => {
    const wrapped = `\`\`\`\n${validJson}\n\`\`\``;
    expect(parseGeminiResponse(wrapped).type).toBe('bug');
  });

  test('returns parse_error result for invalid JSON', () => {
    const result = parseGeminiResponse('this is not json at all');
    expect(result.parse_error).toBe(true);
    expect(result.confidence).toBe(0.0);
    expect(result.type).toBe('unknown');
  });

  test('returns error result for empty string', () => {
    const result = parseGeminiResponse('');
    expect(result.parse_error).toBe(true);
    expect(result.low_confidence).toBe(true);
  });

  test('returns error result for non-string input', () => {
    expect(parseGeminiResponse(null).parse_error).toBe(true);
  });

  test('feature type parsed correctly', () => {
    const json = JSON.stringify({
      type: 'feature', severity: 'low', component: 'frontend',
      confidence: 0.85, low_confidence: false,
      summary: 'Add dark mode', reasoning: 'Explicit feature request',
    });
    const result = parseGeminiResponse(json);
    expect(result.type).toBe('feature');
    expect(result.component).toBe('frontend');
  });

  test('question type parsed correctly', () => {
    const json = JSON.stringify({
      type: 'question', severity: 'low', component: 'unknown',
      confidence: 0.78, low_confidence: false,
      summary: 'User asking how to reset password', reasoning: 'Interrogative phrasing',
    });
    expect(parseGeminiResponse(json).type).toBe('question');
  });

  test('sets low_confidence=true when confidence below 0.7', () => {
    const json = JSON.stringify({
      type: 'bug', severity: 'medium', component: 'unknown',
      confidence: 0.55, low_confidence: false,
      summary: 'Ambiguous issue', reasoning: 'Cannot determine',
    });
    const result = parseGeminiResponse(json);
    expect(result.low_confidence).toBe(true);
    expect(result.confidence).toBe(0.55);
  });
});

// ─── validateClassification ──────────────────────────────────────────────────

describe('validateClassification', () => {
  test('accepts valid classification', () => {
    const result = validateClassification({
      type: 'bug', severity: 'critical', component: 'backend',
      confidence: 0.9, summary: 'summary', reasoning: 'reasoning',
    });
    expect(result.type).toBe('bug');
    expect(result.severity).toBe('critical');
  });

  test('rejects invalid type, falls back to unknown', () => {
    expect(validateClassification({ type: 'incident', severity: 'low', component: 'backend', confidence: 0.8 }).type).toBe('unknown');
  });

  test('rejects invalid severity, falls back to unknown', () => {
    expect(validateClassification({ type: 'bug', severity: 'urgent', component: 'backend', confidence: 0.8 }).severity).toBe('unknown');
  });

  test('clamps confidence above 1.0', () => {
    expect(validateClassification({ type: 'bug', severity: 'low', component: 'backend', confidence: 1.5 }).confidence).toBe(1.0);
  });

  test('handles null input gracefully', () => {
    const result = validateClassification(null);
    expect(result.type).toBe('unknown');
    expect(result.confidence).toBe(0.0);
  });
});

// ─── isValidSchema ───────────────────────────────────────────────────────────

describe('isValidSchema', () => {
  const valid = {
    type: 'bug',
    severity: 'critical',
    component: 'backend',
    confidence: 0.92,
    low_confidence: false,
    summary: 'Login endpoint crashes',
    reasoning: 'Title and body indicate production crash',
  };

  test('returns true for fully valid classification', () => {
    expect(isValidSchema(valid)).toBe(true);
  });

  test('returns true when component is unknown (valid per spec)', () => {
    expect(isValidSchema({ ...valid, component: 'unknown' })).toBe(true);
  });

  test('returns true for confidence=0.0 with low_confidence=true', () => {
    expect(isValidSchema({ ...valid, confidence: 0.0, low_confidence: true })).toBe(true);
  });

  test('returns true for all three valid types', () => {
    expect(isValidSchema({ ...valid, type: 'bug' })).toBe(true);
    expect(isValidSchema({ ...valid, type: 'feature' })).toBe(true);
    expect(isValidSchema({ ...valid, type: 'question' })).toBe(true);
  });

  test('returns true for all three valid severities', () => {
    expect(isValidSchema({ ...valid, severity: 'critical' })).toBe(true);
    expect(isValidSchema({ ...valid, severity: 'medium' })).toBe(true);
    expect(isValidSchema({ ...valid, severity: 'low' })).toBe(true);
  });

  test('returns false when type is unknown (AI should not return this)', () => {
    expect(isValidSchema({ ...valid, type: 'unknown' })).toBe(false);
  });

  test('returns false when type is unrecognized', () => {
    expect(isValidSchema({ ...valid, type: 'incident' })).toBe(false);
  });

  test('returns false when severity is unknown', () => {
    expect(isValidSchema({ ...valid, severity: 'unknown' })).toBe(false);
  });

  test('returns false when severity is unrecognized', () => {
    expect(isValidSchema({ ...valid, severity: 'urgent' })).toBe(false);
  });

  test('returns false when component is unrecognized', () => {
    expect(isValidSchema({ ...valid, component: 'mobile' })).toBe(false);
  });

  test('returns false when confidence is missing', () => {
    const { confidence, ...rest } = valid;
    expect(isValidSchema(rest)).toBe(false);
  });

  test('returns false when confidence is a string', () => {
    expect(isValidSchema({ ...valid, confidence: '0.9' })).toBe(false);
  });

  test('returns false when confidence > 1', () => {
    expect(isValidSchema({ ...valid, confidence: 1.5 })).toBe(false);
  });

  test('returns false when confidence < 0', () => {
    expect(isValidSchema({ ...valid, confidence: -0.1 })).toBe(false);
  });

  test('returns false when low_confidence is not a boolean', () => {
    expect(isValidSchema({ ...valid, low_confidence: 'false' })).toBe(false);
  });

  test('returns false when summary is empty string', () => {
    expect(isValidSchema({ ...valid, summary: '' })).toBe(false);
  });

  test('returns false when summary is whitespace only', () => {
    expect(isValidSchema({ ...valid, summary: '   ' })).toBe(false);
  });

  test('returns false when summary is missing', () => {
    const { summary, ...rest } = valid;
    expect(isValidSchema(rest)).toBe(false);
  });

  test('returns false when reasoning is not a string', () => {
    expect(isValidSchema({ ...valid, reasoning: 42 })).toBe(false);
  });

  test('returns true when reasoning is empty string', () => {
    expect(isValidSchema({ ...valid, reasoning: '' })).toBe(true);
  });

  test('returns false when parse_error is set', () => {
    expect(isValidSchema({ ...valid, parse_error: true })).toBe(false);
  });

  test('returns false for null', () => {
    expect(isValidSchema(null)).toBe(false);
  });

  test('returns false for non-object', () => {
    expect(isValidSchema('string')).toBe(false);
  });

  test('rejects result from parseGeminiResponse with invalid JSON', () => {
    const result = parseGeminiResponse('not json');
    expect(isValidSchema(result)).toBe(false);
  });

  test('accepts result from parseGeminiResponse with valid JSON', () => {
    const json = JSON.stringify({
      type: 'feature', severity: 'low', component: 'frontend',
      confidence: 0.88, low_confidence: false,
      summary: 'Add dark mode support', reasoning: 'Feature request',
    });
    expect(isValidSchema(parseGeminiResponse(json))).toBe(true);
  });
});

// ─── buildFallbackClassification ─────────────────────────────────────────────

describe('buildFallbackClassification', () => {
  test('returns unknown for all classification fields', () => {
    const fallback = buildFallbackClassification();
    expect(fallback.type).toBe('unknown');
    expect(fallback.severity).toBe('unknown');
    expect(fallback.component).toBe('unknown');
  });

  test('returns confidence 0.0 and low_confidence true', () => {
    const fallback = buildFallbackClassification();
    expect(fallback.confidence).toBe(0.0);
    expect(fallback.low_confidence).toBe(true);
  });

  test('returns non-empty summary', () => {
    expect(buildFallbackClassification().summary.length).toBeGreaterThan(0);
  });

  test('uses default reasoning when no reason provided', () => {
    const fallback = buildFallbackClassification();
    expect(typeof fallback.reasoning).toBe('string');
    expect(fallback.reasoning.length).toBeGreaterThan(0);
  });

  test('uses provided reason in reasoning field', () => {
    const fallback = buildFallbackClassification('Gemini rate limit exceeded');
    expect(fallback.reasoning).toBe('Gemini rate limit exceeded');
  });

  test('does not set ai_flagged (that is a workflow concern set via formatSheetsRow)', () => {
    expect(buildFallbackClassification().ai_flagged).toBeUndefined();
  });
});

// ─── processWithRetry ────────────────────────────────────────────────────────

describe('processWithRetry', () => {
  const validJson = JSON.stringify({
    type: 'bug', severity: 'critical', component: 'backend',
    confidence: 0.91, low_confidence: false,
    summary: 'Login service crashes on startup', reasoning: 'Production auth failure',
  });

  const anotherValidJson = JSON.stringify({
    type: 'feature', severity: 'low', component: 'frontend',
    confidence: 0.82, low_confidence: false,
    summary: 'Add dark mode to settings', reasoning: 'Feature request for UI enhancement',
  });

  test('returns attempt 1 result when primary response is valid', () => {
    const result = processWithRetry(validJson);
    expect(result.used_fallback).toBe(false);
    expect(result.attempt).toBe(1);
    expect(result.classification.type).toBe('bug');
    expect(result.classification.severity).toBe('critical');
  });

  test('returns attempt 2 result when primary is invalid but retry is valid', () => {
    const result = processWithRetry('not json', anotherValidJson);
    expect(result.used_fallback).toBe(false);
    expect(result.attempt).toBe(2);
    expect(result.classification.type).toBe('feature');
  });

  test('returns fallback when both attempts fail', () => {
    const result = processWithRetry('invalid primary', 'invalid retry');
    expect(result.used_fallback).toBe(true);
    expect(result.attempt).toBe(2);
    expect(result.classification.type).toBe('unknown');
    expect(result.classification.severity).toBe('unknown');
    expect(result.classification.confidence).toBe(0.0);
  });

  test('returns fallback after attempt 1 when no retry text provided', () => {
    const result = processWithRetry('invalid primary');
    expect(result.used_fallback).toBe(true);
    expect(result.attempt).toBe(1);
  });

  test('returns fallback when primary has type=unknown (normalization result)', () => {
    const invalidTypeJson = JSON.stringify({
      type: 'incident', severity: 'critical', component: 'backend',
      confidence: 0.9, low_confidence: false,
      summary: 'Something failed', reasoning: 'Unknown type from AI',
    });
    const result = processWithRetry(invalidTypeJson, null);
    expect(result.used_fallback).toBe(true);
  });

  test('returns fallback when primary has severity=unknown', () => {
    const invalidSeverityJson = JSON.stringify({
      type: 'bug', severity: 'urgent', component: 'backend',
      confidence: 0.9, low_confidence: false,
      summary: 'Bug in production', reasoning: 'Invalid severity from AI',
    });
    const result = processWithRetry(invalidSeverityJson, null);
    expect(result.used_fallback).toBe(true);
  });

  test('returns fallback when primary has empty summary', () => {
    const emptySummaryJson = JSON.stringify({
      type: 'bug', severity: 'medium', component: 'backend',
      confidence: 0.85, low_confidence: false,
      summary: '', reasoning: 'Something happened',
    });
    const result = processWithRetry(emptySummaryJson, null);
    expect(result.used_fallback).toBe(true);
  });

  test('attempt 2 is tried even if retry text is empty string (invalid JSON)', () => {
    const result = processWithRetry(validJson, '');
    expect(result.used_fallback).toBe(false);
    expect(result.attempt).toBe(1);
  });

  test('classification has all required fields', () => {
    const result = processWithRetry(validJson);
    const c = result.classification;
    expect(c).toHaveProperty('type');
    expect(c).toHaveProperty('severity');
    expect(c).toHaveProperty('component');
    expect(c).toHaveProperty('confidence');
    expect(c).toHaveProperty('low_confidence');
    expect(c).toHaveProperty('summary');
    expect(c).toHaveProperty('reasoning');
  });

  test('fallback classification has all required fields', () => {
    const result = processWithRetry('bad', 'bad');
    const c = result.classification;
    expect(c).toHaveProperty('type');
    expect(c).toHaveProperty('severity');
    expect(c).toHaveProperty('component');
    expect(c).toHaveProperty('confidence');
    expect(c).toHaveProperty('low_confidence');
    expect(c).toHaveProperty('summary');
    expect(c).toHaveProperty('reasoning');
  });
});

// ─── routeToSlackChannel ─────────────────────────────────────────────────────

describe('routeToSlackChannel', () => {
  test('routes critical bug to #incidents', () => {
    expect(routeToSlackChannel({ type: 'bug', severity: 'critical' })).toBe('#incidents');
  });

  test('routes medium bug to #backlog', () => {
    expect(routeToSlackChannel({ type: 'bug', severity: 'medium' })).toBe('#backlog');
  });

  test('routes feature to #backlog', () => {
    expect(routeToSlackChannel({ type: 'feature', severity: 'medium' })).toBe('#backlog');
  });

  test('routes critical feature to #backlog (not #incidents)', () => {
    expect(routeToSlackChannel({ type: 'feature', severity: 'critical' })).toBe('#backlog');
  });

  test('routes question to #questions', () => {
    expect(routeToSlackChannel({ type: 'question', severity: 'low' })).toBe('#questions');
  });

  test('routes unknown type (fallback) to #backlog', () => {
    expect(routeToSlackChannel({ type: 'unknown', severity: 'unknown' })).toBe('#backlog');
  });
});

// ─── formatSlackMessage ──────────────────────────────────────────────────────

describe('formatSlackMessage', () => {
  const issue = {
    title: 'App crashes on login',
    html_url: 'https://github.com/org/repo/issues/42',
    number: 42,
  };

  const criticalBug = {
    type: 'bug', severity: 'critical', component: 'backend',
    confidence: 0.92, low_confidence: false,
    summary: 'Login endpoint throws 500', reasoning: 'Production auth failure',
  };

  test('sets correct channel for critical bug', () => {
    expect(formatSlackMessage(issue, criticalBug).channel).toBe('#incidents');
  });

  test('includes issue title in text', () => {
    expect(formatSlackMessage(issue, criticalBug).text).toContain('App crashes on login');
  });

  test('includes issue URL in blocks', () => {
    const msg = formatSlackMessage(issue, criticalBug);
    expect(msg.blocks[0].text.text).toContain('https://github.com/org/repo/issues/42');
  });

  test('shows ai_flagged warning when aiFlagged=true', () => {
    const msg = formatSlackMessage(issue, criticalBug, true);
    expect(msg.blocks[2].text.text).toContain('AI classification failed');
  });

  test('shows low_confidence warning when low_confidence=true and not ai_flagged', () => {
    const lowConf = { ...criticalBug, confidence: 0.5, low_confidence: true };
    const msg = formatSlackMessage(issue, lowConf, false);
    expect(msg.blocks[2].text.text).toContain('Low confidence');
  });

  test('ai_flagged warning takes precedence over low_confidence warning', () => {
    const lowConf = { ...criticalBug, confidence: 0.5, low_confidence: true };
    const msg = formatSlackMessage(issue, lowConf, true);
    expect(msg.blocks[2].text.text).toContain('AI classification failed');
    expect(msg.blocks[2].text.text).not.toContain('Low confidence');
  });

  test('no warning when high confidence and not ai_flagged', () => {
    const msg = formatSlackMessage(issue, criticalBug, false);
    expect(msg.blocks[2].text.text).not.toContain('Low confidence');
    expect(msg.blocks[2].text.text).not.toContain('AI classification failed');
  });

  test('routes question to #questions', () => {
    const question = {
      type: 'question', severity: 'low', component: 'unknown',
      confidence: 0.8, low_confidence: false, summary: 'How to reset?', reasoning: '',
    };
    expect(formatSlackMessage(issue, question).channel).toBe('#questions');
  });

  test('uses 🔴 emoji for critical severity', () => {
    expect(formatSlackMessage(issue, criticalBug).text).toContain('🔴');
  });

  test('uses ⚪ emoji for unknown severity (fallback)', () => {
    const fallback = {
      type: 'unknown', severity: 'unknown', component: 'unknown',
      confidence: 0.0, low_confidence: true, summary: 'AI failed', reasoning: '',
    };
    expect(formatSlackMessage(issue, fallback, true).text).toContain('⚪');
  });
});

// ─── formatSheetsRow ─────────────────────────────────────────────────────────

describe('formatSheetsRow', () => {
  const issue = {
    number: 42,
    title: 'App crashes on login',
    html_url: 'https://github.com/org/repo/issues/42',
  };

  const classification = {
    type: 'bug', severity: 'critical', component: 'backend',
    confidence: 0.92, low_confidence: false,
    summary: 'Login endpoint throws 500', reasoning: 'Production auth failure',
  };

  test('includes all required fields', () => {
    const row = formatSheetsRow(issue, classification, '2026-05-03T12:00:00.000Z');
    expect(row.timestamp).toBe('2026-05-03T12:00:00.000Z');
    expect(row.issue_number).toBe(42);
    expect(row.title).toBe('App crashes on login');
    expect(row.url).toBe('https://github.com/org/repo/issues/42');
    expect(row.type).toBe('bug');
    expect(row.severity).toBe('critical');
    expect(row.component).toBe('backend');
    expect(row.confidence).toBe('92%');
    expect(row.low_confidence).toBe(false);
    expect(row.ai_flagged).toBe(false);
    expect(row.summary).toBe('Login endpoint throws 500');
    expect(row.reasoning).toBe('Production auth failure');
  });

  test('ai_flagged defaults to false when not provided', () => {
    expect(formatSheetsRow(issue, classification).ai_flagged).toBe(false);
  });

  test('ai_flagged=true when passed explicitly — Gemini API failure after retry', () => {
    const row = formatSheetsRow(issue, classification, '2026-05-03T12:00:00.000Z', true);
    expect(row.ai_flagged).toBe(true);
  });

  test('ai_flagged=false when passed explicitly as false', () => {
    expect(formatSheetsRow(issue, classification, undefined, false).ai_flagged).toBe(false);
  });

  test('formats confidence as percentage string', () => {
    expect(formatSheetsRow(issue, { ...classification, confidence: 0.55 }).confidence).toBe('55%');
  });

  test('formats fallback classification correctly with ai_flagged=true', () => {
    const fallback = {
      type: 'unknown', severity: 'unknown', component: 'unknown',
      confidence: 0.0, low_confidence: true,
      summary: 'AI classification failed — manual review required',
      reasoning: 'Both attempts failed',
    };
    const row = formatSheetsRow(issue, fallback, '2026-05-03T12:00:00.000Z', true);
    expect(row.ai_flagged).toBe(true);
    expect(row.type).toBe('unknown');
    expect(row.confidence).toBe('0%');
    expect(row.low_confidence).toBe(true);
  });

  test('uses current timestamp when not provided', () => {
    const before = Date.now();
    const row = formatSheetsRow(issue, classification);
    const after = Date.now();
    const rowTime = new Date(row.timestamp).getTime();
    expect(rowTime).toBeGreaterThanOrEqual(before);
    expect(rowTime).toBeLessThanOrEqual(after);
  });
});
