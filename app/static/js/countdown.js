/* Countdown to the spotlight release date supplied by the server. */
(function () {
  "use strict";

  const root = document.querySelector("[data-countdown]");
  if (!root) return;

  const target = new Date(root.dataset.countdown);
  if (Number.isNaN(target.getTime())) return;

  const fields = {
    days: root.querySelector("[data-countdown-days]"),
    hours: root.querySelector("[data-countdown-hours]"),
    minutes: root.querySelector("[data-countdown-minutes]"),
    seconds: root.querySelector("[data-countdown-seconds]")
  };

  const pad = function (value) { return String(value).padStart(2, "0"); };

  function tick() {
    const remaining = target.getTime() - Date.now();
    if (remaining <= 0) {
      root.querySelector(".countdown").innerHTML = "<p class='muted'>Out now.</p>";
      window.clearInterval(timer);
      return;
    }
    const seconds = Math.floor(remaining / 1000);
    fields.days.textContent = pad(Math.floor(seconds / 86400));
    fields.hours.textContent = pad(Math.floor(seconds / 3600) % 24);
    fields.minutes.textContent = pad(Math.floor(seconds / 60) % 60);
    fields.seconds.textContent = pad(seconds % 60);
  }

  tick();
  const timer = window.setInterval(tick, 1000);
})();
