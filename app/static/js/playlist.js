/* Playlist add/remove.
 *
 * One delegated listener handles every toggle on the page, so tables and card
 * grids share the same code. The button's aria-pressed state is the source of
 * truth for both its label and its styling.
 */
(function () {
  "use strict";

  const ENDPOINT = "/api/playlist";

  async function toggle(button) {
    const songId = button.dataset.songId;
    const songName = button.dataset.songName || "Track";
    const inPlaylist = button.getAttribute("aria-pressed") === "true";

    button.disabled = true;
    try {
      const response = inPlaylist
        ? await fetch(ENDPOINT + "/" + encodeURIComponent(songId), { method: "DELETE" })
        : await fetch(ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ song_id: Number(songId) })
          });

      if (!response.ok) {
        const payload = await response.json().catch(function () { return {}; });
        throw new Error(payload.error || "Request failed");
      }

      const result = await response.json();
      button.setAttribute("aria-pressed", String(result.in_playlist));
      window.showToast(
        result.in_playlist ? songName + " added to your playlist" : songName + " removed"
      );

      // On the playlist page itself, a removed track should leave the table.
      const row = document.querySelector('[data-playlist-row="' + songId + '"]');
      if (row && !result.in_playlist) {
        row.remove();
        renumber();
      }
    } catch (error) {
      window.showToast(error.message || "Could not update your playlist", "error");
    } finally {
      button.disabled = false;
    }
  }

  function renumber() {
    const rows = document.querySelectorAll("[data-playlist-row]");
    rows.forEach(function (row, index) {
      const cell = row.querySelector(".num");
      if (cell) cell.textContent = String(index + 1);
    });
    if (rows.length === 0) window.location.reload();
  }

  document.addEventListener("click", function (event) {
    const button = event.target.closest("[data-playlist-toggle]");
    if (button) toggle(button);
  });
})();
