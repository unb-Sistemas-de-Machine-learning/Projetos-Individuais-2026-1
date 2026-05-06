'use strict';

const {
  isValidIssue,
  buildPrompt,
  parseGeminiResponse,
  validateClassification,
  routeToSlackChannel,
  formatSlackMessage,
  formatSheetsRow,
} = require('../../solutions/solution-a/utils');

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
    const prompt = buildPrompt(baseIssue);
    expect(prompt).toContain('App crashes on login');
  });

  test('includes body in prompt', () => {
    const prompt = buildPrompt(baseIssue);
    expect(prompt).toContain('throws a 500 error');
  });

  test('includes label names in prompt', () => {
    const prompt = buildPrompt(baseIssue);
    expect(prompt).toContain('bug');
    expect(prompt).toContain('critical');
  });

  test('includes repository name in prompt', () => {
    const prompt = buildPrompt(baseIssue);
    expect(prompt).toContain('my-app');
  });

  test('handles missing body with placeholder', () => {
    const prompt = buildPrompt({ title: 'Some issue' });
    expect(prompt).toContain('(no body provided)');
  });

  test('handles missing labels gracefully', () => {
    const prompt = buildPrompt({ title: 'Some issue', body: 'desc', labels: [] });
    expect(prompt).toContain('(none)');
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
    const prompt = buildPrompt(baseIssue);
    expect(prompt).toContain('Return ONLY the JSON object');
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
    const result = parseGeminiResponse(wrapped);
    expect(result.type).toBe('bug');
  });

  test('strips markdown code block without language hint', () => {
    const wrapped = `\`\`\`\n${validJson}\n\`\`\``;
    const result = parseGeminiResponse(wrapped);
    expect(result.type).toBe('bug');
  });

  test('returns parse_error result for invalid JSON', () => {
    const result = parseGeminiResponse('this is not json at all');
    expect(result.parse_error).toBe(true);
    expect(result.confidence).toBe(0.0);
    expect(result.low_confidence).toBe(true);
    expect(result.type).toBe('unknown');
  });

  test('returns error result for empty string', () => {
    const result = parseGeminiResponse('');
    expect(result.parse_error).toBe(true);
    expect(result.low_confidence).toBe(true);
  });

  test('returns error result for non-string input', () => {
    const result = parseGeminiResponse(null);
    expect(result.parse_error).toBe(true);
  });

  test('feature type parsed correctly', () => {
    const json = JSON.stringify({
      type: 'feature',
      severity: 'low',
      component: 'frontend',
      confidence: 0.85,
      low_confidence: false,
      summary: 'Add dark mode',
      reasoning: 'Explicit feature request for UI enhancement',
    });
    const result = parseGeminiResponse(json);
    expect(result.type).toBe('feature');
    expect(result.severity).toBe('low');
    expect(result.component).toBe('frontend');
  });

  test('question type parsed correctly', () => {
    const json = JSON.stringify({
      type: 'question',
      severity: 'low',
      component: 'unknown',
      confidence: 0.78,
      low_confidence: false,
      summary: 'User asking how to reset password',
      reasoning: 'Interrogative phrasing, no indication of defect',
    });
    const result = parseGeminiResponse(json);
    expect(result.type).toBe('question');
  });

  test('sets low_confidence=true when confidence below 0.7', () => {
    const json = JSON.stringify({
      type: 'bug',
      severity: 'medium',
      component: 'unknown',
      confidence: 0.55,
      low_confidence: false,
      summary: 'Ambiguous issue',
      reasoning: 'Cannot determine details',
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
      type: 'bug',
      severity: 'critical',
      component: 'backend',
      confidence: 0.9,
      summary: 'summary',
      reasoning: 'reasoning',
    });
    expect(result.type).toBe('bug');
    expect(result.severity).toBe('critical');
    expect(result.component).toBe('backend');
  });

  test('rejects invalid type, falls back to unknown', () => {
    const result = validateClassification({ type: 'incident', severity: 'low', component: 'backend', confidence: 0.8 });
    expect(result.type).toBe('unknown');
  });

  test('rejects invalid severity, falls back to unknown', () => {
    const result = validateClassification({ type: 'bug', severity: 'urgent', component: 'backend', confidence: 0.8 });
    expect(result.severity).toBe('unknown');
  });

  test('rejects invalid component, falls back to unknown', () => {
    const result = validateClassification({ type: 'bug', severity: 'low', component: 'database', confidence: 0.8 });
    expect(result.component).toBe('unknown');
  });

  test('clamps confidence above 1.0', () => {
    const result = validateClassification({ type: 'bug', severity: 'low', component: 'backend', confidence: 1.5 });
    expect(result.confidence).toBe(1.0);
  });

  test('clamps confidence below 0.0', () => {
    const result = validateClassification({ type: 'bug', severity: 'low', component: 'backend', confidence: -0.1 });
    expect(result.confidence).toBe(0.0);
    expect(result.low_confidence).toBe(true);
  });

  test('handles null input gracefully', () => {
    const result = validateClassification(null);
    expect(result.type).toBe('unknown');
    expect(result.confidence).toBe(0.0);
  });

  test('handles missing confidence field', () => {
    const result = validateClassification({ type: 'bug', severity: 'low', component: 'backend' });
    expect(result.confidence).toBe(0.0);
    expect(result.low_confidence).toBe(true);
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

  test('routes low bug to #backlog', () => {
    expect(routeToSlackChannel({ type: 'bug', severity: 'low' })).toBe('#backlog');
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

  test('routes unknown type to #backlog', () => {
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
    type: 'bug',
    severity: 'critical',
    component: 'backend',
    confidence: 0.92,
    low_confidence: false,
    summary: 'Login endpoint throws 500',
    reasoning: 'Crash in production auth flow',
  };

  test('sets correct channel for critical bug', () => {
    const msg = formatSlackMessage(issue, criticalBug);
    expect(msg.channel).toBe('#incidents');
  });

  test('includes issue title in text', () => {
    const msg = formatSlackMessage(issue, criticalBug);
    expect(msg.text).toContain('App crashes on login');
  });

  test('includes issue URL in blocks', () => {
    const msg = formatSlackMessage(issue, criticalBug);
    const sectionText = msg.blocks[0].text.text;
    expect(sectionText).toContain('https://github.com/org/repo/issues/42');
  });

  test('adds low_confidence warning when applicable', () => {
    const lowConf = { ...criticalBug, confidence: 0.5, low_confidence: true };
    const msg = formatSlackMessage(issue, lowConf);
    const summaryBlock = msg.blocks[2].text.text;
    expect(summaryBlock).toContain('Low confidence');
  });

  test('no low_confidence warning for high confidence', () => {
    const msg = formatSlackMessage(issue, criticalBug);
    const summaryBlock = msg.blocks[2].text.text;
    expect(summaryBlock).not.toContain('Low confidence');
  });

  test('routes question to #questions', () => {
    const question = { type: 'question', severity: 'low', component: 'unknown', confidence: 0.8, low_confidence: false, summary: 'How to reset?', reasoning: '' };
    const msg = formatSlackMessage(issue, question);
    expect(msg.channel).toBe('#questions');
  });

  test('uses 🔴 emoji for critical severity', () => {
    const msg = formatSlackMessage(issue, criticalBug);
    expect(msg.text).toContain('🔴');
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
    type: 'bug',
    severity: 'critical',
    component: 'backend',
    confidence: 0.92,
    low_confidence: false,
    summary: 'Login endpoint throws 500',
    reasoning: 'Production auth failure',
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

  test('ai_flagged is always false in solution-a', () => {
    const row = formatSheetsRow(issue, classification);
    expect(row.ai_flagged).toBe(false);
  });

  test('formats confidence as percentage string', () => {
    const row = formatSheetsRow(issue, { ...classification, confidence: 0.55 });
    expect(row.confidence).toBe('55%');
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
