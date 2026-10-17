/* License view */

async function renderLicenseView() {
  const container = document.getElementById("view-license");

  let info = { tier: "lite", activated: false };
  if (api) {
    try { info = await api.get_license_info(); } catch (e) {}
  }

  if (info.tier === "full" && info.activated) {
    container.innerHTML = `
      <h1 class="view-title">License</h1>
      <p class="view-subtitle">Your license is active.</p>

      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">GodotBridge Full</div>
            <div class="card-subtitle">All 345 tools unlocked</div>
          </div>
          <span class="badge badge-ok"><span class="badge-dot"></span> Active</span>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px;font-size:13px">
          <div><span style="color:var(--text-dim)">Email:</span> ${esc(info.email || "—")}</div>
          <div><span style="color:var(--text-dim)">Expires:</span> ${esc(info.expires || "Never")}</div>
          <div><span style="color:var(--text-dim)">Status:</span> ${esc(info.status || "Active")}</div>
          <div><span style="color:var(--text-dim)">Type:</span> ${esc(info.license_type || "—")}</div>
        </div>
        <div style="margin-top:20px">
          <button class="btn btn-danger btn-sm" onclick="deactivateLicense()">Deactivate</button>
        </div>
      </div>
    `;
  } else {
    container.innerHTML = `
      <h1 class="view-title">License</h1>
      <p class="view-subtitle">You are on the <strong>Lite</strong> plan — 65 free tools. Upgrade to Full for all 345 tools.</p>

      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Activate License</div>
            <div class="card-subtitle">Enter your license key to unlock all tools.</div>
          </div>
        </div>
        <div class="input-group">
          <input type="text" class="input" id="licenseKeyInput" placeholder="XXXX-XXXX-XXXX-XXXX-XXXX" spellcheck="false" />
          <button class="btn btn-primary" onclick="activateLicense()">Activate</button>
        </div>
        <div id="licenseError" style="margin-top:10px;font-size:12.5px;color:var(--error);display:none"></div>
      </div>

      <div style="margin-top:20px">
        <a href="https://godotbridge.com/#pricing" class="btn btn-secondary" style="text-decoration:none" target="_blank">
          Purchase a License &rarr;
        </a>
      </div>
    `;
  }
}

async function activateLicense() {
  if (!api) return;
  const input = document.getElementById("licenseKeyInput");
  const errorEl = document.getElementById("licenseError");
  const key = input.value.trim();

  if (!key) {
    errorEl.textContent = "Please enter a license key.";
    errorEl.style.display = "block";
    return;
  }

  errorEl.style.display = "none";
  input.disabled = true;

  const result = await api.activate_license(key);

  if (result.activated) {
    await updateTierBadge();
    renderLicenseView();
  } else {
    errorEl.textContent = result.__error_message__ || "Activation failed.";
    errorEl.style.display = "block";
    input.disabled = false;
  }
}

async function deactivateLicense() {
  if (!api) return;
  await api.deactivate_license();
  await updateTierBadge();
  renderLicenseView();
}
