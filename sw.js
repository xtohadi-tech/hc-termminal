const CACHE = 'hc-v4';
const BASE = '/hc-termminal/';
const ASSETS = [
  BASE,
  `${BASE}index.html`,
  `${BASE}manifest.json`,
  `${BASE}icon-192.png`,
  `${BASE}icon-512.png`,
  `${BASE}sw.js`
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(ASSETS).catch(() => {}))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;

  const url = e.request.url;
  if (/https?:\/\/(?:[^/]*\.)?binance\.com|coingecko\.com|coinmarketcal\.com/.test(url)) {
    e.respondWith(fetch(e.request).catch(() => new Response('', { status: 503 })));
    return;
  }
  if (url.endsWith('/hc-termminal/')) {
    e.respondWith(caches.match(`${BASE}index.html`));
    return;
  }
  e.respondWith(caches.match(e.request).then(c => c || fetch(e.request)));
});
