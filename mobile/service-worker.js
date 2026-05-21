// Box Breathing Studio — service worker for offline support.
const CACHE = "bbs-mobile-v1";

const ASSETS = [
  "./",
  "./index.html",
  "./styles.css",
  "./app.js",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./assets/bg/bg_home.png",
  "./assets/bg/bg_box.png",
  "./assets/bg/bg_478.png",
  "./assets/bg/bg_bhramari.png",
  "./assets/bg/bg_nadi.png",
  "./assets/bg/bg_extended.png",
  "./assets/bg/bg_complete.png",
  "./assets/voice/inhale.mp3",
  "./assets/voice/hold.mp3",
  "./assets/voice/exhale.mp3",
  "./assets/voice/hold_empty.mp3",
  "./assets/voice/inhale_left.mp3",
  "./assets/voice/inhale_right.mp3",
  "./assets/voice/exhale_left.mp3",
  "./assets/voice/exhale_right.mp3",
  "./assets/voice/hum.mp3",
  "./assets/voice/begin.mp3",
  "./assets/voice/complete.mp3"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((response) => {
        // Cache new requests on the fly so the app stays offline-safe.
        const copy = response.clone();
        caches.open(CACHE).then((cache) => cache.put(event.request, copy));
        return response;
      }).catch(() => cached);
    })
  );
});
