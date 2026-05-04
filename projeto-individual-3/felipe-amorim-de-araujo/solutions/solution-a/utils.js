'use strict';

const VALID_TYPES = ['bug', 'feature', 'question'];
const VALID_SEVERITIES = ['critical', 'medium', 'low'];
const VALID_COMPONENTS = ['frontend', 'backend', 'infra', 'unknown'];

function isValidIssue(issue) {
  return !!(issue && typeof issue.title === 'string' && issue.title.trim().length > 0);
}

function buildPrompt(issue) {
  const title = (issue && issue.title) || '';
  const body = (issue && issue.body) || '';
  const labels = Array.isArray(issue && issue.labels)
    ? issue.labels.map(l => (typeof l === 'string' ? l : l.name || '')).join(', ')
    : '';
  const repoName = (issue && issue.repository && issue.repository.name) || '';

  return `You are an issue classifier for a software project. Analyze the following GitHub issue and return a JSON classification.

Issue Title: ${title || '(no title)'}
Issue Body: ${body || '(no body provided)'}
Labels: ${labels || '(none)'}
Repository: ${repoName || '(unknown)'}

Return ONLY a valid JSON object with this exact structure:
{
  "type": "bug | feature | question",
  "severity": "critical | medium | low",
  "component": "frontend | backend | infra | unknown",
  "confidence": <float between 0.0 and 1.0>,
  "low_confidence": <boolean, true if confidence < 0.7>,
  "summary": "<one-line summary of the issue>",
  "reasoning": "<brief explanation of the classification>"
}

Classification rules:
- type=bug: reports something broken or not working as expected
- type=feature: requests new functionality or enhancement
- type=question: asks how something works or seeks clarification
- severity=critical: production-breaking, data loss, security vulnerability, auth failure in production
- severity=medium: significant functionality impaired but a workaround exists
- severity=low: minor issue, cosmetic problem, or nice-to-have improvement
- component=frontend: UI, CSS, JavaScript, browser-side behavior
- component=backend: API, database, server-side logic, authentication
- component=infra: deployment, CI/CD, Docker, cloud services, networking
- component=unknown: cannot determine from available context

Return ONLY the JSON object. No markdown code blocks, no prose outside the JSON.`;
}

function parseGeminiResponse(responseText) {
  if (typeof responseText !== 'string' || responseText.trim().length === 0) {
    return {
      type: 'unknown',
      severity: 'unknown',
      component: 'unknown',
      confidence: 0.0,
      low_confidence: true,
      summary: 'Empty response from AI',
      reasoning: 'Gemini returned an empty response',
      parse_error: true,
    };
  }

  let jsonText = responseText.trim();

  const codeBlockMatch = jsonText.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (codeBlockMatch) {
    jsonText = codeBlockMatch[1].trim();
  }

  try {
    const parsed = JSON.parse(jsonText);
    return validateClassification(parsed);
  } catch (err) {
    return {
      type: 'unknown',
      severity: 'unknown',
      component: 'unknown',
      confidence: 0.0,
      low_confidence: true,
      summary: 'Failed to parse AI response',
      reasoning: `JSON parse error: ${err.message}`,
      parse_error: true,
    };
  }
}

function validateClassification(obj) {
  if (!obj || typeof obj !== 'object') {
    return {
      type: 'unknown',
      severity: 'unknown',
      component: 'unknown',
      confidence: 0.0,
      low_confidence: true,
      summary: '',
      reasoning: 'Invalid classification object',
    };
  }

  const type = VALID_TYPES.includes(obj.type) ? obj.type : 'unknown';
  const severity = VALID_SEVERITIES.includes(obj.severity) ? obj.severity : 'unknown';
  const component = VALID_COMPONENTS.includes(obj.component) ? obj.component : 'unknown';
  const confidence = typeof obj.confidence === 'number'
    ? Math.min(1.0, Math.max(0.0, obj.confidence))
    : 0.0;

  return {
    type,
    severity,
    component,
    confidence,
    low_confidence: confidence < 0.7,
    summary: typeof obj.summary === 'string' ? obj.summary : '',
    reasoning: typeof obj.reasoning === 'string' ? obj.reasoning : '',
  };
}

function routeToSlackChannel(classification) {
  if (classification.type === 'question') {
    return '#questions';
  }
  if (classification.type === 'bug' && classification.severity === 'critical') {
    return '#incidents';
  }
  return '#backlog';
}

function formatSlackMessage(issue, classification) {
  const channel = routeToSlackChannel(classification);

  const severityEmoji = { critical: '🔴', medium: '🟡', low: '🟢', unknown: '⚪' };
  const typeLabel = { bug: 'Bug', feature: 'Feature Request', question: 'Question', unknown: 'Unknown' };

  const emoji = severityEmoji[classification.severity] || '⚪';
  const typeStr = typeLabel[classification.type] || classification.type;
  const issueUrl = issue.html_url || issue.url || '#';
  const title = issue.title || '(no title)';
  const confidenceNote = classification.low_confidence
    ? '\n⚠️ _Low confidence — manual review recommended_'
    : '';

  return {
    channel,
    text: `${emoji} [${typeStr}] ${title}`,
    blocks: [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `${emoji} *[${typeStr}]* <${issueUrl}|${title}>`,
        },
      },
      {
        type: 'section',
        fields: [
          { type: 'mrkdwn', text: `*Type:* ${classification.type}` },
          { type: 'mrkdwn', text: `*Severity:* ${classification.severity}` },
          { type: 'mrkdwn', text: `*Component:* ${classification.component}` },
          { type: 'mrkdwn', text: `*Confidence:* ${(classification.confidence * 100).toFixed(0)}%` },
        ],
      },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*Summary:* ${classification.summary}${confidenceNote}`,
        },
      },
    ],
  };
}

function formatSheetsRow(issue, classification, processedAt) {
  const timestamp = processedAt || new Date().toISOString();
  return {
    timestamp,
    issue_number: (issue && issue.number) || '',
    title: (issue && issue.title) || '',
    url: (issue && (issue.html_url || issue.url)) || '',
    type: classification.type,
    severity: classification.severity,
    component: classification.component,
    confidence: `${(classification.confidence * 100).toFixed(0)}%`,
    low_confidence: classification.low_confidence,
    ai_flagged: false,
    summary: classification.summary,
    reasoning: classification.reasoning,
  };
}

module.exports = {
  isValidIssue,
  buildPrompt,
  parseGeminiResponse,
  validateClassification,
  routeToSlackChannel,
  formatSlackMessage,
  formatSheetsRow,
};
