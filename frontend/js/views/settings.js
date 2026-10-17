/* Settings view */

async function renderSettingsView() {
  const container = document.getElementById("view-settings");

  let s = { permission_mode: "safe_edit", check_updates: true };
  if (api) {
    try { s = await api.get_settings(); } catch (e) {}
  }

  const isSafe = s.permission_mode === "safe_edit";

  container.innerHTML = `
    <h1 class="view-title">Settings</h1>
    <p class="view-subtitle">Configure GodotBridge behavior.</p>

    <div class="section">
      <div class="section-title">Permission Mode</div>
      <div class="card">
        <div class="card-subtitle" style="margin-bottom:14px">Controls what the AI agent is allowed to do. Applied to all configured MCP clients.</div>
        <div class="toggle-group">
          <button class="toggle-option ${isSafe ? "active" : ""}" onclick="setPermission('safe_edit')">
            Safe Edit
          </button>
          <button class="toggle-option ${!isSafe ? "active" : ""}" onclick="setPermission('full_control')">
            Full Control
          </button>
        </div>
        <div style="margin-top:12px;font-size:12.5px;color:var(--text-dim)">
          ${isSafe
            ? "<strong>Safe Edit:</strong> AI can read, create and edit. Asks before destructive actions (delete, run, export)."
            : "<strong>Full Control:</strong> All actions enabled. No confirmation prompts from the bridge."
          }
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Updates</div>
      <div class="card">
        <label style="display:flex;align-items:center;gap:10px;cursor:pointer">
          <input type="checkbox" id="autoUpdateCheck" ${s.check_updates ? "checked" : ""} onchange="toggleAutoUpdate()" style="accent-color:var(--accent);width:16px;height:16px" />
          <span style="font-size:13.5px">Check for updates on startup</span>
        </label>
        <div style="margin-top:14px">
          <button class="btn btn-secondary btn-sm" onclick="checkUpdatesNow()">Check Now</button>
          <span id="updateResult" style="margin-left:10px;font-size:12.5px;color:var(--text-dim)"></span>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">About</div>
      <div class="card">
        <div style="font-size:13px;color:var(--text-dim);display:flex;flex-direction:column;gap:6px">
          <div><strong>GodotBridge Desktop</strong> v1.0.0</div>
          <div>MCP server with 345 tools for Godot 4.x</div>
          <div style="display:flex;gap:16px;margin-top:6px">
            <a href="https://godotbridge.com" style="color:var(--accent)" target="_blank">Website</a>
            <a href="https://godotbridge.com/docs" style="color:var(--accent)" target="_blank">Documentation</a>
            <a href="https://github.com/godotbridge/releases" style="color:var(--accent)" target="_blank">GitHub</a>
          </div>
        </div>
      </div>
    </div>
  `;
}

async function setPermission(mode) {
  if (!api) return;
  const result = await api.set_permission_mode(mode);
  if (result.success) {
    showToast(`Permission mode set to ${mode === "safe_edit" ? "Safe Edit" : "Full Control"}`);
    renderSettingsView();
  }
}

async function toggleAutoUpdate() {
  if (!api) return;
  const checked = document.getElementById("autoUpdateCheck").checked;
  await api.set_setting("check_updates", checked);
}

async function checkUpdatesNow() {
  if (!api) return;
  const el = document.getElementById("updateResult");
  el.textContent = "Checking...";
  const result = await api.check_for_updates();
  if (result.available) {
    el.innerHTML = `<span style="color:var(--ok)">v${esc(result.latest)} available!</span> <button class="btn btn-primary btn-sm" onclick="downloadUpdate('${result.download_url}')">Download</button>`;
  } else if (result.error) {
    el.innerHTML = `<span style="color:var(--error)">Error: ${esc(result.error)}</span>`;
  } else {
    el.innerHTML = `<span style="color:var(--ok)">You're up to date (v${esc(result.current)}).</span>`;
  }
}

async function downloadUpdate(url) {
  if (!api) return;
  const el = document.getElementById("updateResult");
  el.textContent = "Downloading...";
  const result = await api.download_update(url);
  if (result.success) {
    el.innerHTML = `<span style="color:var(--ok)">Downloaded to ${esc(result.path)}</span>`;
  } else {
    el.innerHTML = `<span style="color:var(--error)">${esc(result.error)}</span>`;
  }
}
