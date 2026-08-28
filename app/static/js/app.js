/* Shared behaviour: mobile navigation and the toast helper other scripts use. */
(function () {
  "use strict";

  const toggle = document.querySelector("[data-nav-toggle]");
  const nav = document.getElementById("primary-nav");
  const mobileQuery = window.matchMedia("(max-width: 900px)");

  function applyNavState() {
    if (!nav || !toggle) return;
    if (mobileQuery.matches) {
      const open = toggle.getAttribute("aria-expanded") === "true";
      nav.hidden = !open;
    } else {
      nav.hidden = false;
      toggle.setAttribute("aria-expanded", "false");
    }
  }

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      const open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      applyNavState();
    });
    mobileQuery.addEventListener("change", applyNavState);
    applyNavState();
  }

  const region = document.getElementById("toasts");

  /** Show a short-lived message at the bottom of the screen. */
  window.showToast = function (message, variant) {
    if (!region) return;
    const toast = document.createElement("div");
    toast.className = "toast" + (variant === "error" ? " toast--error" : "");
    toast.textContent = message;
    region.appendChild(toast);
    window.setTimeout(function () {
      toast.remove();
    }, 2600);
  };
})();
