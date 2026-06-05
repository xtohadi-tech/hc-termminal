import fs from 'fs';
import https from 'node:https';

if (!fs.existsSync('bot/config.json')) {
  console.log(JSON.stringify({ ok: false, missing: 'bot/config.json' }, null, 2));
  process.exit(0);
}
const { telegram: tg, thresholds } = JSON.parse(fs.readFileSync('bot/config.json', 'utf8'));

function request({ method, path, body }) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const req = https.request({ hostname: 'api.telegram.org', path: `/bot${tg.botToken}${path}`, method, headers: data ? { 'content-type': 'application/json', 'content-length': Buffer.byteLength(data) } : {} }, (res) => {
      let out = '';
      res.on('data', (chunk) => (out += chunk));
      res.on('end', () => {
        try {
          resolve(JSON.parse(out));
        } catch (e) {
          resolve(out);
        }
      });
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

async function send(msg) {
  if (!tg.botToken || !tg.chatId) return;
  await request({ method: 'POST', path: '/sendMessage', body: { chat_id: tg.chatId, text: msg, disable_web_page_preview: true } });
}

export async function sendAlert(message) {
  await send(`🚨 HC Terminal\n\n${message}`);
}

export function matchesThreshold(route) {
  return {
    strong: route.score >= (thresholds.strong ?? 78),
    breakout: route.changePct != null && route.changePct >= (thresholds.breakoutPct ?? 12),
  };
}
