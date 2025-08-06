self.addEventListener('install', e => {
  console.log('🔧 Service Worker installato');
});

self.addEventListener('fetch', e => {
  e.respondWith(fetch(e.request));
});
