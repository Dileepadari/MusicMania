/* iTunes search.
 *
 * Results are built with DOM nodes rather than string concatenation, so a track
 * title containing quotes or angle brackets cannot break the markup.
 */
(function () {
  "use strict";

  const form = document.getElementById("search-form");
  const input = document.getElementById("search-input");
  const results = document.getElementById("search-results");
  const status = document.getElementById("search-status");
  const explicit = document.getElementById("filter-explicit");
  const minutes = document.getElementById("filter-minutes");
  const seconds = document.getElementById("filter-seconds");
  const reset = document.getElementById("filter-reset");
  const tagline = document.getElementById("search-tagline");

  const RESULT_LIMIT = 12;

  /** Max duration in ms from the two filter inputs, or null when both are blank. */
  function maxDurationMs() {
    const mins = parseInt(minutes.value, 10);
    const secs = parseInt(seconds.value, 10);
    if (Number.isNaN(mins) && Number.isNaN(secs)) return null;
    return ((Number.isNaN(mins) ? 0 : mins) * 60 + (Number.isNaN(secs) ? 0 : secs)) * 1000;
  }

  function formatDuration(ms) {
    // Audiobook and ebook rows come back with no trackTimeMillis at all, and a
    // few music rows report 0. Both should read as unknown, not "0 min 00 sec".
    if (!ms || ms < 1000) return "Unknown length";
    const total = Math.round(ms / 1000);
    const mins = Math.floor(total / 60);
    const secs = total % 60;
    return mins + " min " + String(secs).padStart(2, "0") + " sec";
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function resultCard(track) {
    const card = element("article", "result");

    const art = element("div", "result__art");
    const image = element("img");
    image.src = track.artworkUrl100 || "";
    image.alt = "";
    image.loading = "lazy";
    art.appendChild(image);

    if (track.previewUrl) {
      const audio = document.createElement("audio");
      audio.controls = true;
      audio.preload = "none";
      audio.src = track.previewUrl;
      art.appendChild(audio);
    }

    const body = element("div", "result__body");
    body.appendChild(element("h2", "result__title", track.trackName || track.collectionName || "Untitled"));
    body.appendChild(element("p", "muted", track.artistName || "Unknown artist"));

    const meta = element("div", "result__meta");
    [
      track.collectionName,
      formatDuration(track.trackTimeMillis),
      track.primaryGenreName,
      track.trackExplicitness ? "Explicitness: " + track.trackExplicitness : null
    ]
      .filter(Boolean)
      .forEach(function (text) { meta.appendChild(element("span", null, text)); });
    body.appendChild(meta);

    if (track.trackViewUrl) {
      const link = element("a", null, "More about this track");
      link.href = track.trackViewUrl;
      link.target = "_blank";
      link.rel = "noopener";
      body.appendChild(link);
    }

    card.append(art, body);
    return card;
  }

  async function search(term) {
    results.replaceChildren();
    status.textContent = "Searching...";

    const url = new URL("https://itunes.apple.com/search");
    url.searchParams.set("term", term);
    url.searchParams.set("explicit", explicit.checked ? "yes" : "no");
    url.searchParams.set("limit", "25");
    // Without this the API defaults to media=all and returns films, ebooks and
    // audiobooks alongside the music, which is not what this page is for.
    url.searchParams.set("media", "music");

    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error("iTunes returned " + response.status);
      const payload = await response.json();
      render(payload.results || []);
    } catch (error) {
      status.textContent = "Could not reach the iTunes catalogue. Check your connection and try again.";
    }
  }

  function render(tracks) {
    const limit = maxDurationMs();
    const matches = tracks
      .filter(function (track) { return limit === null || (track.trackTimeMillis || 0) <= limit; })
      .slice(0, RESULT_LIMIT);

    if (matches.length === 0) {
      status.textContent = "No results found. Try a different search or clear the filters.";
      return;
    }

    status.textContent = "Showing " + matches.length + " result" + (matches.length === 1 ? "" : "s");
    const fragment = document.createDocumentFragment();
    matches.forEach(function (track) { fragment.appendChild(resultCard(track)); });
    results.appendChild(fragment);
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const term = input.value.trim();
    if (term) search(term);
  });

  reset.addEventListener("click", function () {
    explicit.checked = false;
    minutes.value = "";
    seconds.value = "";
    input.focus();
  });

  /* Rotating tagline. Purely decorative, so it is skipped when the visitor has
     asked for reduced motion. */
  if (tagline && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const lines = [
      "Search the iTunes catalogue and play a 30 second preview.",
      "Discover the musical gems you have not heard yet.",
      "Filter by length when you only have a few minutes."
    ];
    let index = 0;
    window.setInterval(function () {
      index = (index + 1) % lines.length;
      tagline.textContent = lines[index];
    }, 5000);
  }
})();
