import { ROUTES } from './scanFlows.js';
import fs from 'fs';

function clamp01(n) {
  if (Number.isFinite(n)) return Math.max(0, Math.min(100, n));
  return 0;
}

function strengthFromRow(row) {
  const vol = Number(row.volume || 0);
  const price = Number(row.price || 0);
  const change = Number(row.change || 0);
  const spread = Number(row.spread || 0);

  // naive heuristic: volume & momentum positive, higher better; spread cost reduces score
  const volScore = Math.min(100, Math.log10(Math.max(1, vol + 1)) * 12);
  const momScore = clamp01(50 + change);
  const costScore = clamp01(100 - spread * 10);

  return clamp01(volScore * 0.5 + momScore * 0.35 + costScore * 0.15);
}

function normalizeRouteLabel(route) {
  return route.replace(/[^a-zA-Z0-9]/g, '_').slice(0, 40);
}

export function scoreRoutes(pricesBySymbol) {
  // pricesBySymbol: { SYM: { price, change, volume, spread } }
  return ROUTES.map((route) => {
    const symbols = route.split('→');
    const rows = symbols.map((s) => pricesBySymbol[s] || {}).filter(Boolean);
    const score = rows.length
      ? Math.round(rows.reduce((a, r) => a + strengthFromRow(r), 0) / rows.length)
      : 0;
    return { route, score, symbols: rows.map((r, i) => ({ symbol: symbols[i], score: Math.round(strengthFromRow(r)) })) };
  }).sort((a, b) => b.score - a.score);
}

export function saveStrengthScores(scores) {
  const payload = { updatedAt: new Date().toISOString(), scores: scores.map(({ route, score }) => ({ route, score })) };
  fs.writeFileSync('data/routeStrength.json', JSON.stringify(payload, null, 2));

  // compact file for webapp
  fs.writeFileSync('frontend/public/routeStrength.json', JSON.stringify({ updatedAt: payload.updatedAt, scores: scores.map(({ route, score }) => ({ route, score })) }, null, 2));
}
