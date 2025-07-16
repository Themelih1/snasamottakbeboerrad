self.addEventListener('install', function(e) {
  console.log('Service Worker: Yüklendi');

  e.waitUntil(
    caches.open('snasamottak-cache').then(function(cache) {
      return cache.addAll([
        '/',
        '/en/',
        '/static/styles.css',
        '/static/scripts.js',
        // Önemli statik dosyaları ekle
      ]);
    })
  );
});

self.addEventListener('fetch', function(e) {
  e.respondWith(
    caches.match(e.request).then(function(response) {
      return response || fetch(e.request);
    })
  );
});
