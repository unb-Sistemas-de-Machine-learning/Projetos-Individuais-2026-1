function normalizeArticle(input) {
  if (!input) throw new Error('Input is required');
  
  return {
    article_title: (input.title || '').trim().substring(0, 500),
    abstract: (input.abstract || '').trim().substring(0, 2000),
    keywords: Array.isArray(input.keywords) ? input.keywords.slice(0, 10) : [],
    doi: input.doi ? input.doi.trim() : null,
    source: input.source || 'unknown',
    received_at: new Date().toISOString(),
    is_valid: !!(input.title && input.abstract)
  };
}

function isValidDOI(doi) {
  if (!doi) return false;
  const doiRegex = /^10\.\d{4,}\/[-._;()/:\w]+$/;
  return doiRegex.test(doi);
}


function recalculateConfidence(aiConfidence, doiValid, metadataComplete) {
  const weights = {
    ai: 0.7,
    doi: 0.2,
    metadata: 0.1
  };
  
  return (
    (aiConfidence * weights.ai) +
    (doiValid * weights.doi) +
    (metadataComplete * weights.metadata)
  );
}

function analyzeHallucinationRisk(classified) {
  const risks = [];
  
  if (!classified.summary || classified.summary.length < 20) {
    risks.push('Resumo muito curto - possível alucinação');
  }
  
  if (classified.confidence < 0.5) {
    risks.push('Confiança baixa - incerteza alta');
  }
  
  if (!Array.isArray(classified.topics) || classified.topics.length === 0) {
    risks.push('Sem tópicos extraídos - falha possível');
  }
  
  return {
    risk_level: risks.length > 0 ? 'medium' : 'low',
    flags: risks,
    should_request_human_review: risks.length > 0
  };
}


function formatDecisionLog(decision) {
  return {
    timestamp: new Date().toISOString(),
    article_title: decision.article_title,
    classification: decision.classification,
    confidence: Math.round(decision.confidence * 100) / 100,
    decision: decision.decision,
    reason: decision.reason || 'N/A',
    reviewed_by: 'AI:auto',
    manually_reviewed: false
  };
}

module.exports = {
  normalizeArticle,
  isValidDOI,
  recalculateConfidence,
  analyzeHallucinationRisk,
  formatDecisionLog
};
