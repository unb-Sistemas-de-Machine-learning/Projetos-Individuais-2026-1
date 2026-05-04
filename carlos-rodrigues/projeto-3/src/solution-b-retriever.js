const http = require('http');
const fs = require('fs');
const url = require('url');

const PORT = process.env.PORT || 3000;
const knowledgePath = __dirname + '/../solutions/solution-b/knowledge.json';

let knowledge = [];
try {
  knowledge = JSON.parse(fs.readFileSync(knowledgePath, 'utf8'));
} catch (e) {
  console.error('Cannot load knowledge.json:', e.message);
  knowledge = [];
}

function scoreItem(item, qTokens) {
  const text = (item.title + ' ' + item.summary + ' ' + (item.keywords || []).join(' ')).toLowerCase();
  let score = 0;
  for (const t of qTokens) if (t && text.indexOf(t) !== -1) score += 1;
  return score;
}

function tokenize(s) {
  return (s || '').toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
}

const server = http.createServer((req, res) => {
  console.log(`${new Date().toISOString()} - ${req.socket.remoteAddress} ${req.method} ${req.url}`);
  if (req.method === 'POST' && req.url === '/search') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      console.log('Request body:', body.slice(0, 1000));
      try {
        const payload = JSON.parse(body || '{}');
        const q = payload.q || '';
        const topK = Math.max(1, Math.min(10, Number(payload.topK) || 3));
        const qTokens = tokenize(q);
        const results = knowledge.map(item => ({item, score: scoreItem(item, qTokens)}))
          .filter(r => r.score > 0)
          .sort((a,b) => b.score - a.score)
          .slice(0, topK)
          .map(r => ({id: r.item.id, title: r.item.title, summary: r.item.summary, score: r.score}));
        res.writeHead(200, {'Content-Type': 'application/json'});
        res.end(JSON.stringify({results}));
      } catch (e) {
        res.writeHead(400, {'Content-Type': 'application/json'});
        res.end(JSON.stringify({error: 'invalid payload'}));
      }
    });
    return;
  }
  res.writeHead(404, {'Content-Type': 'text/plain'});
  res.end('Not Found');
});

server.listen(PORT, '::', () => console.log(`Local retriever listening on [::]:${PORT} (IPv6/IPv4)`));
