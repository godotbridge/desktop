/* Setup view — addon install, client config, prerequisites */

async function renderSetupView() {
  const container = document.getElementById("view-setup");

  if (!activeProject) {
    container.innerHTML = `
      <h1 class="view-title">Setup</h1>
      <p class="view-subtitle">Select a project first.</p>
      <button class="btn btn-secondary" onclick="navigate('#/project')">Go to Project</button>
    `;
    return;
  }

  container.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">
      <h1 class="view-title">${esc(activeProject.name)}</h1>
      <button class="btn btn-ghost btn-sm" onclick="navigate('#/project')">Change Project</button>
    </div>
    <p class="view-subtitle" style="font-family:var(--font-mono);font-size:12px">${esc(activeProject.path)}</p>

    <div id="setup-addon" class="section">
      <div class="section-title">Addon</div>
      <div class="card"><div class="loading"><div class="spinner"></div> Checking addon status...</div></div>
    </div>

    <div id="setup-clients" class="section">
      <div class="section-title">AI Clients</div>
      <div class="card"><div class="loading"><div class="spinner"></div> Detecting clients...</div></div>
    </div>

    <div id="setup-prereqs" class="section">
      <div class="section-title">Prerequisites</div>
      <div class="card"><div class="loading"><div class="spinner"></div> Checking prerequisites...</div></div>
    </div>
  `;

  if (api) {
    loadAddonSection();
    loadClientsSection();
    loadPrereqsSection();
  }
}

async function loadAddonSection() {
  const el = document.querySelector("#setup-addon .card");
  try {
    const status = await api.get_addon_status(activeProject.path);
    let actionBtn = "";
    let badge = "";

    if (!status.installed) {
      badge = `<span class="badge badge-warn"><span class="badge-dot"></span> Not Installed</span>`;
      actionBtn = `<button class="btn btn-primary btn-sm" onclick="installAddon()">Install</button>`;
    } else if (status.needs_update) {
      badge = `<span class="badge badge-warn"><span class="badge-dot"></span> Update Available</span>`;
      actionBtn = `<button class="btn btn-primary btn-sm" onclick="installAddon()">Update to ${esc(status.bundled_version)}</button>`;
    } else {
      badge = `<span class="badge badge-ok"><span class="badge-dot"></span> Installed</span>`;
      actionBtn = `<button class="btn btn-ghost btn-sm" onclick="installAddon()">Reinstall</button>`;
    }

    el.innerHTML = `
      <div class="card-header">
        <div>
          <div class="card-title">GodotBridge Addon</div>
          <div class="card-subtitle">Version: ${esc(status.installed_version || status.bundled_version)}</div>
        </div>
        <div style="display:flex;align-items:center;gap:10px">
          ${badge}
          ${actionBtn}
        </div>
      </div>
    `;
  } catch (e) {
    el.innerHTML = `<div style="color:var(--error)">Error checking addon: ${esc(e.message || String(e))}</div>`;
  }
}

async function installAddon() {
  if (!api || !activeProject) return;
  const result = await api.install_addon(activeProject.path);
  if (result.success) {
    showToast("Addon installed successfully");
    loadAddonSection();
  } else {
    showToast(result.error || "Install failed", "error");
  }
}

async function loadClientsSection() {
  const section = document.getElementById("setup-clients");
  try {
    const clients = await api.detect_clients();
    let html = `<div class="section-title">AI Clients</div><div class="client-grid">`;

    for (const c of clients) {
      let statusBadge, actionBtn;
      if (!c.detected) {
        statusBadge = `<span class="badge badge-neutral">Not Installed</span>`;
        actionBtn = "";
      } else if (c.configured) {
        statusBadge = `<span class="badge badge-ok"><span class="badge-dot"></span> Configured</span>`;
        actionBtn = `<button class="btn btn-ghost btn-sm" onclick="configureClient('${c.id}')">Reconfigure</button>`;
      } else {
        statusBadge = `<span class="badge badge-warn"><span class="badge-dot"></span> Not Configured</span>`;
        actionBtn = `<button class="btn btn-primary btn-sm" onclick="configureClient('${c.id}')">Configure</button>`;
      }

      html += `
        <div class="client-card">
          <div class="client-name">${esc(c.label)}</div>
          <div class="client-status">${statusBadge}</div>
          ${actionBtn}
        </div>
      `;
    }
    html += `</div>`;
    section.innerHTML = html;
  } catch (e) {
    section.innerHTML = `<div class="section-title">AI Clients</div><div class="card" style="color:var(--error)">Error: ${esc(String(e))}</div>`;
  }
}

async function configureClient(clientId) {
  if (!api) return;
  const result = await api.write_client_config(clientId);
  if (result.success) {
    showToast("Client configured successfully");
    loadClientsSection();
  } else {
    showToast(result.error || "Configuration failed", "error");
  }
}

async function loadPrereqsSection() {
  const section = document.getElementById("setup-prereqs");
  try {
    const prereqs = await api.check_prerequisites();
    const items = [
      { label: "Python 3.10+", ok: prereqs.python.ok, detail: prereqs.python.version || "Not found" },
      { label: "uv", ok: prereqs.uv.installed, detail: prereqs.uv.version || "Not found" },
      { label: "uvx", ok: prereqs.uvx.installed, detail: prereqs.uvx.version || "Not found" },
    ];

    let html = `<div class="section-title">Prerequisites</div><ul class="prereq-list">`;
    for (const item of items) {
      html += `
        <li class="prereq-item">
          <span class="prereq-icon ${item.ok ? "prereq-ok" : "prereq-fail"}">${item.ok ? "&#10003;" : "&#10007;"}</span>
          <span style="font-weight:600">${esc(item.label)}</span>
          <span style="color:var(--text-dim);margin-left:auto;font-size:12px;font-family:var(--font-mono)">${esc(item.detail)}</span>
        </li>
      `;
    }
    html += `</ul>`;

    if (!prereqs.ready) {
      html += `<p style="margin-top:12px;font-size:12.5px;color:var(--warning)">Install <a href="https://docs.astral.sh/uv/getting-started/installation/" style="color:var(--accent)" target="_blank">uv</a> and Python 3.10+ to use GodotBridge.</p>`;
    }

    section.innerHTML = html;
  } catch (e) {
    section.innerHTML = `<div class="section-title">Prerequisites</div><div class="card" style="color:var(--error)">Error: ${esc(String(e))}</div>`;
  }
}
