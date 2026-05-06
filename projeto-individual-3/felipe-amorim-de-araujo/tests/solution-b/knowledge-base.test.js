'use strict';

const path = require('path');
const kbPath = path.resolve(__dirname, '../../solutions/solution-b/knowledge-base.json');

let kb;

beforeAll(() => {
  kb = require(kbPath);
});

describe('knowledge-base.json shape', () => {
  test('loads as valid JSON with an examples array', () => {
    expect(Array.isArray(kb.examples)).toBe(true);
  });

  test('has between 6 and 10 examples', () => {
    expect(kb.examples.length).toBeGreaterThanOrEqual(6);
    expect(kb.examples.length).toBeLessThanOrEqual(10);
  });

  test('every entry has issue.title as a non-empty string', () => {
    for (const entry of kb.examples) {
      expect(typeof entry.issue.title).toBe('string');
      expect(entry.issue.title.trim().length).toBeGreaterThan(0);
    }
  });

  test('every entry has classification with type, severity, component, summary, reasoning', () => {
    for (const entry of kb.examples) {
      const cl = entry.classification;
      expect(cl).toBeDefined();
      expect(typeof cl.type).toBe('string');
      expect(typeof cl.severity).toBe('string');
      expect(typeof cl.component).toBe('string');
      expect(typeof cl.summary).toBe('string');
      expect(typeof cl.reasoning).toBe('string');
    }
  });

  test('every entry has a non-empty _rationale', () => {
    for (const entry of kb.examples) {
      expect(typeof entry._rationale).toBe('string');
      expect(entry._rationale.trim().length).toBeGreaterThan(0);
    }
  });
});

describe('knowledge-base.json enum validity', () => {
  const VALID_TYPES = ['bug', 'feature', 'question'];
  const VALID_SEVERITIES = ['critical', 'medium', 'low'];
  const VALID_COMPONENTS = ['frontend', 'backend', 'infra', 'unknown'];

  test('all classification.type values are valid', () => {
    for (const entry of kb.examples) {
      expect(VALID_TYPES).toContain(entry.classification.type);
    }
  });

  test('all classification.severity values are valid', () => {
    for (const entry of kb.examples) {
      expect(VALID_SEVERITIES).toContain(entry.classification.severity);
    }
  });

  test('all classification.component values are valid', () => {
    for (const entry of kb.examples) {
      expect(VALID_COMPONENTS).toContain(entry.classification.component);
    }
  });
});

describe('knowledge-base.json coverage invariants', () => {
  test('all 3 types appear across examples', () => {
    const types = new Set(kb.examples.map(e => e.classification.type));
    expect(types.has('bug')).toBe(true);
    expect(types.has('feature')).toBe(true);
    expect(types.has('question')).toBe(true);
  });

  test('all 3 severities appear across examples', () => {
    const severities = new Set(kb.examples.map(e => e.classification.severity));
    expect(severities.has('critical')).toBe(true);
    expect(severities.has('medium')).toBe(true);
    expect(severities.has('low')).toBe(true);
  });

  test('at least 3 distinct components appear across examples', () => {
    const components = new Set(kb.examples.map(e => e.classification.component));
    expect(components.size).toBeGreaterThanOrEqual(3);
  });

  test('fallback safety: first 3 entries cover all 3 types', () => {
    const firstThreeTypes = new Set(kb.examples.slice(0, 3).map(e => e.classification.type));
    expect(firstThreeTypes.has('bug')).toBe(true);
    expect(firstThreeTypes.has('feature')).toBe(true);
    expect(firstThreeTypes.has('question')).toBe(true);
  });
});
