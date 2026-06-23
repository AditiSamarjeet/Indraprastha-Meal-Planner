// Indraprastha Meal Planner — Service Worker (network-first)
const CACHE = 'indraprastha-v5';

self.addEventListener('install', e => {
  e.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Network-first for everything — always try to get fresh data
self.addEventListener('fetch', e => {
  // Only handle GET requests
  if (e.request.method !== 'GET') return;

  e.respondWith(
    fetch(e.request, { cache: 'no-store' })
      .then(response => {
        // Cache a copy for offline fallback (app shell only)
        if (response.ok) {
          const url = new URL(e.request.url);
          if (url.pathname === '/' || url.pathname.endsWith('index.html') || url.pathname.endsWith('manifest.json')) {
            const clone = response.clone();
            caches.open(CACHE).then(c => c.put(e.request, clone));
          }
        }
        return response;
      })
      .catch(() => caches.match(e.request)) // offline fallback
  );
});

self.addEventListener('message', e => {
  if (e.data === 'skipWaiting') self.skipWaiting();
});
