/* GodotBridge Desktop — SPA Router & pywebview bridge */

let api = null;
let activeProject = null;

function esc(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

function showToast(msg, type = "ok") {
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  document.body.appendChild(el);
  requestAnimationFrame(() => el.classList.add("visible"));
  setTimeout(() => {
    el.classList.remove("visible");
    setTimeout(() => el.remove(), 300);
  }, 3000);
}

const views = {
  "/project": { el: "view-project", render: renderProjectView },
  "/setup":   { el: "view-setup",   render: renderSetupView },
  "/license": { el: "view-license", render: renderLicenseView },
  "/settings":{ el: "view-settings",render: renderSettingsView },
};

function navigate(hash) {
  const path = (hash || "#/project").replace("#", "");
  const view = views[path];
  if (!view) return navigate("#/project");

  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.getElementById(view.el).classList.add("active");

  document.querySelectorAll(".sidebar-nav a").forEach(a => {
    a.classList.toggle("active", a.getAttribute("data-view") === path.slice(1));
  });

  view.render();
}

async function updateTierBadge() {
  if (!api) return;
  try {
    const info = await api.get_license_info();
    const badge = document.getElementById("tierBadge");
    if (info.tier === "full") {
      badge.textContent = "FULL";
      badge.className = "tier-badge tier-full";
    } else {
      badge.textContent = "LITE";
      badge.className = "tier-badge tier-lite";
    }
  } catch (e) {}
}

function setActiveProject(path, name) {
  activeProject = { path, name };
  navigate("#/setup");
}

window.addEventListener("hashchange", () => navigate(location.hash));

window.addEventListener("pywebviewready", () => {
  api = window.pywebview.api;
  updateTierBadge();
  navigate(location.hash || "#/project");
});

// Fallback for dev mode (no pywebview)
setTimeout(() => {
  if (!api) {
    console.warn("pywebview not ready — running in dev/browser mode");
    api = null;
    navigate(location.hash || "#/project");
  }
}, 1000);
