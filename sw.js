// Indraprastha Meal Planner — Service Worker
// Strategy: Cache-first for the app shell, network-first for sync endpoints
const CACHE = 'indraprastha-v3';
const APP_SHELL = ['/', '/index.html', '/manifest.json', '/icon-192.png', '/icon-512.png'];

// Install: cache the app shell
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(APP_SHELL.map(u => {
      // Use no-cache fetch to get fresh copy on install
      return new Request(u, { cache: 'no-cache' });
    }).filter(Boolean))).then(() => self.skipWaiting())
  );
});

// Activate: clean up old caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Fetch: serve from cache for app shell, pass through for sync API
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Always go to network for sync endpoints (real-time data)
  if (url.pathname.startsWith('/sync/')) {
    e.respondWith(fetch(e.request).catch(() => new Response('{}', {
      headers: { 'Content-Type': 'application/json' }
    })));
    return;
  }

  // For the app shell: cache-first, then update cache in background
  e.respondWith(
    caches.match(e.request).then(cached => {
      const networkFetch = fetch(e.request).then(response => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return response;
      }).catch(() => null);

      // Return cached immediately; update in background
      return cached || networkFetch;
    })
  );
});

// Listen for skip-waiting message (triggered when new version available)
self.addEventListener('message', e => {
  if (e.data === 'skipWaiting') self.skipWaiting();
});
