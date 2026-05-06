'use strict';

const {
  isValidIssue,
  buildPrompt,
  parseGeminiResponse,
  validateClassification,
  routeToSlackChannel,
  formatSlackMessage,
  formatSheetsRow,
  selectExamples,
} = require('../../solutions/solution-b/utils');

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

// ─── buildPrompt (zero-shot baseline — no examples) ──────────────────────────

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

// ─── buildPrompt (few-shot — with examples) ───────────────────────────────────

describe('buildPrompt with examples', () => {
  const baseIssue = {
    title: 'App crashes on login',
    body: 'When clicking login the app throws a 500 error.',
    labels: [{ name: 'bug' }, { name: 'critical' }],
    repository: { name: 'my-app' },
  };

  const sampleExamples = [
    {
      issue: { title: 'Login page broken', body: 'Cannot log in at all.', labels: ['bug', 'critical'] },
      classification: { type: 'bug', severity: 'critical', component: 'backend', summary: 'Login completely broken', reasoning: 'Auth failure.' },
    },
    {
      issue: { title: 'Add dark mode', body: 'Please add dark mode to settings.', labels: ['feature'] },
      classification: { type: 'feature', severity: 'low', component: 'frontend', summary: 'Add dark mode toggle', reasoning: 'UI enhancement request.' },
    },
    {
      issue: { title: 'How to reset password?', body: 'I cannot find the reset option.', labels: ['question'] },
      classification: { type: 'question', severity: 'low', component: 'unknown', summary: 'User asking about password reset', reasoning: 'Question, no defect.' },
    },
  ];

  test('with empty examples array, output matches calling with no examples argument', () => {
    expect(buildPrompt(baseIssue, [])).toBe(buildPrompt(baseIssue));
  });

  test('with examples, prompt contains "Examples of correctly classified issues:" header', () => {
    const prompt = buildPrompt(baseIssue, sampleExamples);
    expect(prompt).toContain('Examples of correctly classified issues:');
  });

  test('each example block contains its title', () => {
    const prompt = buildPrompt(baseIssue, sampleExamples);
    expect(prompt).toContain('Login page broken');
    expect(prompt).toContain('Add dark mode');
    expect(prompt).toContain('How to reset password?');
  });

  test('each example block contains its classification JSON', () => {
    const prompt = buildPrompt(baseIssue, sampleExamples);
    expect(prompt).toContain('"type": "bug"');
    expect(prompt).toContain('"type": "feature"');
    expect(prompt).toContain('"type": "question"');
  });

  test('example bodies are truncated at 300 chars with ellipsis', () => {
    const longBody = 'x'.repeat(400);
    const exWithLongBody = [{
      issue: { title: 'Long issue', body: longBody, labels: [] },
      classification: { type: 'bug', severity: 'low', component: 'unknown', summary: 'Long', reasoning: 'Long.' },
    }];
    const prompt = buildPrompt(baseIssue, exWithLongBody);
    expect(prompt).toContain('x'.repeat(300) + '…');
    expect(prompt).not.toContain('x'.repeat(301));
  });

  test('examples block appears before "Now classify this issue:" section', () => {
    const prompt = buildPrompt(baseIssue, sampleExamples);
    const examplesPos = prompt.indexOf('Examples of correctly classified issues:');
    const classifyPos = prompt.indexOf('Now classify this issue:');
    expect(examplesPos).toBeGreaterThan(-1);
    expect(classifyPos).toBeGreaterThan(-1);
    expect(examplesPos).toBeLessThan(classifyPos);
  });

  test('classification rules block is still present when examples are injected', () => {
    const prompt = buildPrompt(baseIssue, sampleExamples);
    expect(prompt).toContain('Classification rules:');
    expect(prompt).toContain('type=bug: reports something broken');
  });

  test('prompt total length stays under 8000 chars with 3 max-truncated examples', () => {
    const maxBodyExample = {
      issue: { title: 'A'.repeat(100), body: 'B'.repeat(400), labels: ['bug'] },
      classification: { type: 'bug', severity: 'critical', component: 'backend', summary: 'S'.repeat(100), reasoning: 'R'.repeat(100) },
    };
    const worstCaseExamples = [maxBodyExample, maxBodyExample, maxBodyExample];
    const prompt = buildPrompt(baseIssue, worstCaseExamples);
    expect(prompt.length).toBeLessThan(8000);
  });

  test('examples are numbered Example 1, Example 2, Example 3', () => {
    const prompt = buildPrompt(baseIssue, sampleExamples);
    expect(prompt).toContain('Example 1:');
    expect(prompt).toContain('Example 2:');
    expect(prompt).toContain('Example 3:');
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

  test('ai_flagged is always false in solution-b', () => {
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

// ─── selectExamples ──────────────────────────────────────────────────────────

describe('selectExamples', () => {
  const kbBug = {
    issue: { title: 'App crashes on login', body: 'Login throws a 500 error in production.', labels: ['bug', 'critical'] },
    classification: { type: 'bug', severity: 'critical', component: 'backend', summary: 'Login crash', reasoning: 'Auth failure.' },
  };
  const kbFeature = {
    issue: { title: 'Add dark mode', body: 'Please add dark mode support to the settings page.', labels: ['feature'] },
    classification: { type: 'feature', severity: 'low', component: 'frontend', summary: 'Dark mode toggle', reasoning: 'UI enhancement.' },
  };
  const kbQuestion = {
    issue: { title: 'How do I reset my password?', body: 'I cannot find the password reset option anywhere.', labels: ['question'] },
    classification: { type: 'question', severity: 'low', component: 'unknown', summary: 'Password reset question', reasoning: 'No defect reported.' },
  };
  const kbFeature2 = {
    issue: { title: 'Add export to CSV feature', body: 'Users want to export their data to CSV format for analysis.', labels: ['feature', 'backend'] },
    classification: { type: 'feature', severity: 'medium', component: 'backend', summary: 'CSV export feature', reasoning: 'New functionality.' },
  };

  const fullKb = [kbBug, kbFeature, kbQuestion, kbFeature2];

  test('returns [] when knowledge base is empty', () => {
    expect(selectExamples({ title: 'Some issue' }, [], 3)).toEqual([]);
  });

  test('returns [] when k is 0', () => {
    expect(selectExamples({ title: 'Some issue' }, fullKb, 0)).toEqual([]);
  });

  test('returns first K curated entries when no token or label overlap exists', () => {
    const noOverlapIssue = { title: 'xyz quantum infra flux', body: 'zzzz aaaa bbbb', labels: [] };
    const result = selectExamples(noOverlapIssue, fullKb, 3);
    expect(result).toHaveLength(3);
    expect(result[0]).toBe(kbBug);
    expect(result[1]).toBe(kbFeature);
    expect(result[2]).toBe(kbQuestion);
  });

  test('label intersection has higher weight than body overlap', () => {
    const kb = [
      { issue: { title: 'unrelated topic foo', body: 'crash login error auth service fails production five tokens matching total', labels: [] }, classification: { type: 'bug', severity: 'low', component: 'unknown', summary: '', reasoning: '' } },
      { issue: { title: 'short', body: 'short', labels: ['bug', 'critical'] }, classification: { type: 'bug', severity: 'critical', component: 'backend', summary: '', reasoning: '' } },
    ];
    const issue = { title: 'login', body: 'crash', labels: ['bug', 'critical'] };
    const result = selectExamples(issue, kb, 1);
    // Label match (2 labels × 3 = 6) should beat body-token match (5 tokens × 1 = 5)
    expect(result[0]).toBe(kb[1]);
  });

  test('title overlap has higher weight than body overlap', () => {
    const kb = [
      { issue: { title: 'completely different', body: 'login crash error production auth service down severely broken badly', labels: [] }, classification: { type: 'bug', severity: 'low', component: 'unknown', summary: '', reasoning: '' } },
      { issue: { title: 'login crash error', body: 'unrelated', labels: [] }, classification: { type: 'bug', severity: 'critical', component: 'backend', summary: '', reasoning: '' } },
    ];
    const issue = { title: 'login crash error', body: 'something else', labels: [] };
    const result = selectExamples(issue, kb, 1);
    // Entry 2 title match: 3 tokens × 2 = 6, body: 0
    // Entry 1 body match: many tokens × 1 but no title match
    // Title weight=2 means 3 shared title tokens = 6 > body-only matching
    expect(result[0]).toBe(kb[1]);
  });

  test('matching is case-insensitive', () => {
    const kb = [
      { issue: { title: 'LOGIN FAILURE', body: 'AUTH error', labels: [] }, classification: { type: 'bug', severity: 'critical', component: 'backend', summary: '', reasoning: '' } },
    ];
    const issue = { title: 'login failure', body: 'auth', labels: [] };
    const result = selectExamples(issue, kb, 1);
    expect(result).toHaveLength(1);
    expect(result[0]).toBe(kb[0]);
  });

  test('stop words do not contribute to score', () => {
    const kb = [
      { issue: { title: 'the is on in to of', body: 'and or for with when this that it my', labels: [] }, classification: { type: 'bug', severity: 'low', component: 'unknown', summary: '', reasoning: '' } },
    ];
    const issue = { title: 'the is on in to of', body: 'and or for', labels: [] };
    // All shared tokens are stop words — score should be 0 → fallback
    const result = selectExamples(issue, kb, 1);
    expect(result).toHaveLength(1);
    // Fallback returns kb.slice(0, 1)
    expect(result[0]).toBe(kb[0]);
  });

  test('ordering is deterministic on tied scores (ascending kbIndex)', () => {
    const kb = [
      { issue: { title: 'crash error', body: '', labels: [] }, classification: { type: 'bug', severity: 'low', component: 'unknown', summary: '', reasoning: '' } },
      { issue: { title: 'crash error', body: '', labels: [] }, classification: { type: 'feature', severity: 'low', component: 'frontend', summary: '', reasoning: '' } },
      { issue: { title: 'crash error', body: '', labels: [] }, classification: { type: 'question', severity: 'low', component: 'unknown', summary: '', reasoning: '' } },
    ];
    const issue = { title: 'crash error', body: '', labels: [] };
    const result1 = selectExamples(issue, kb, 2);
    const result2 = selectExamples(issue, kb, 2);
    expect(result1[0]).toBe(kb[0]);
    expect(result1[1]).toBe(kb[1]);
    expect(result1).toEqual(result2);
  });

  test('respects k limit — returns exactly k entries', () => {
    const bigKb = [kbBug, kbFeature, kbQuestion, kbFeature2,
      { issue: { title: 'extra1', body: '', labels: [] }, classification: { type: 'bug', severity: 'low', component: 'unknown', summary: '', reasoning: '' } },
      { issue: { title: 'extra2', body: '', labels: [] }, classification: { type: 'bug', severity: 'low', component: 'unknown', summary: '', reasoning: '' } },
      { issue: { title: 'extra3', body: '', labels: [] }, classification: { type: 'bug', severity: 'low', component: 'unknown', summary: '', reasoning: '' } },
      { issue: { title: 'extra4', body: '', labels: [] }, classification: { type: 'bug', severity: 'low', component: 'unknown', summary: '', reasoning: '' } },
    ];
    const result = selectExamples({ title: 'crash', body: '', labels: [] }, bigKb, 3);
    expect(result).toHaveLength(3);
  });

  test('does not mutate the knowledge base array', () => {
    const kbCopy = [{ ...kbBug }, { ...kbFeature }];
    const originalOrder = [kbCopy[0], kbCopy[1]];
    selectExamples({ title: 'feature dark mode', body: '', labels: ['feature'] }, kbCopy, 1);
    expect(kbCopy[0]).toBe(originalOrder[0]);
    expect(kbCopy[1]).toBe(originalOrder[1]);
  });

  test('handles issue with no body and no labels without throwing', () => {
    expect(() => selectExamples({ title: 'Crash on login' }, fullKb, 3)).not.toThrow();
  });

  test('handles labels as objects with .name property', () => {
    const issue = { title: 'login crash', body: '', labels: [{ name: 'bug' }, { name: 'critical' }] };
    expect(() => selectExamples(issue, fullKb, 3)).not.toThrow();
    const result = selectExamples(issue, fullKb, 3);
    expect(result.length).toBeGreaterThan(0);
  });
});
