const CACHE = "habit-v1";
const FILES = ["/", "/index.html", "/main.py"]; // main.py не кешируется, но путь нужен

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(FILES))
  );
});

self.addEventListener("fetch", (e) => {
  e.respondWith(
    caches.match(e.request).then((r) => r || fetch(e.request))
  );
});