/* AcademiaLMS — main.js */
(function () {
  "use strict";

  // ── Sidebar toggle (mobile) ────────────────────────────────
  const sidebar  = document.getElementById("sidebar");
  const sbOpen   = document.getElementById("sbOpen");
  const sbClose  = document.getElementById("sbClose");
  const overlay  = document.getElementById("sbOverlay");

  function openSb()  {
    if (sidebar) sidebar.classList.add("open");
    if (overlay) overlay.classList.add("show");
    document.body.style.overflow = "hidden";
  }
  function closeSb() {
    if (sidebar) sidebar.classList.remove("open");
    if (overlay) overlay.classList.remove("show");
    document.body.style.overflow = "";
  }

  if (sbOpen)   sbOpen.addEventListener("click", openSb);
  if (sbClose)  sbClose.addEventListener("click", closeSb);
  if (overlay)  overlay.addEventListener("click", closeSb);
  document.addEventListener("keydown", e => { if (e.key === "Escape") closeSb(); });

  // ── Active nav link ────────────────────────────────────────
  const path = window.location.pathname;
  document.querySelectorAll(".sb-nav a").forEach(link => {
    if (link.getAttribute("href") === path) link.classList.add("active");
  });

  // ── Auto-dismiss flash messages after 5 s ─────────────────
  document.querySelectorAll(".flash").forEach(el => {
    setTimeout(() => {
      el.style.transition = "opacity .4s";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });

  // ── File input — enforce size limit client-side ────────────
  document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener("change", function () {
      const f = this.files[0];
      if (f && f.size > 50 * 1024 * 1024) {
        alert("File exceeds the 50 MB size limit.");
        this.value = "";
      }
    });
  });

}());
