// Radar Trending: cuba rangkaian dulu, guna salinan simpanan bila tiada internet.
const CACHE = "radar-v17";
const SHELL = ["./", "./index.html", "./data.json", "./history/index.json", "./history/scores.json", "./manifest.webmanifest", "./icons/icon-192.png", "./icons/icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const req = e.request;
  if(req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  const key = new URL(req.url); key.search = "";
  e.respondWith(
    fetch(req).then(res => { if(res.ok){ const copy = res.clone(); caches.open(CACHE).then(c => c.put(key.href, copy)); } return res; })
      .catch(() => caches.match(key.href).then(r => r || caches.match("./index.html")))
  );
});
