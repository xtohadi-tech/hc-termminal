import fs from 'fs';
import { ROUTES } from './scanFlows.js';

function readHistory() {
  if (!fs.existsSync('data/history.ndjson')) return [];
  return fs.readFileSync('data/history.ndjson', 'utf8')
    .split('\n')
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

function writeHistoryRow(row) {
  fs.mkdirSync('data', { recursive: true });
  fs.appendFileSync('data/history.ndjson', JSON.stringify({ ...row, ts: new Date().toISOString() }) + '\n');
}

function routeStatsFor(history, route) {
  const candles = history.filter((h) => h.route === route).slice(-30);
  if (!candles.length) return null;
  const wins = candles.filter((c) => (c.end || 0) > (c.start || 0)).length;
  const winRate = wins / candles.length;
  const lastChange = candles[candles.length - 1].change ?? null;

  return { samples: candles.length, winRate: Math.round(winRate * 100), lastChange, lastTs: candles[candles.length - 1].ts };
}

export function recordRouteCandle(route, startPrice, endPrice) {
  writeHistoryRow({ route, start: startPrice, end: endPrice, change: endPrice - startPrice });
}

export function routeBacktestSnapshot() {
  const history = readHistory();
  const snap = ROUTES.map((route) => ({ route, ...(routeStatsFor(history, route) || { samples: 0, winRate: null }) }))
    .filter((r) => r.samples > 0)
    .sort((a, b) => (b.winRate ?? 0) - (a.winRate ?? 0));

  fs.writeFileSync('frontend/public/routeBacktest.json', JSON.stringify({ updatedAt: new Date().toISOString(), rows: snap }, null, 2));
  return snap;
}
