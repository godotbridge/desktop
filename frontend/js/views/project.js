/* Project selection view */

const FOLDER_ICON = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>`;

async function renderProjectView() {
  const container = document.getElementById("view-project");

  let recentHTML = "";
  if (api) {
    try {
      const projects = await api.get_recent_projects();
      if (projects.length > 0) {
        recentHTML = `
          <div class="section">
            <div class="section-title">Recent Projects</div>
            <div class="project-grid">
              ${projects.map(p => `
                <div class="project-card" onclick="openRecent('${p.path.replace(/\\/g, "\\\\").replace(/'/g, "\\'")}', '${p.name.replace(/'/g, "\\'")}')">
                  <div class="icon">${FOLDER_ICON}</div>
                  <div class="info">
                    <div class="name">${esc(p.name)}</div>
                    <div class="path">${esc(p.path)}</div>
                  </div>
                </div>
              `).join("")}
            </div>
          </div>
        `;
      }
    } catch (e) {}
  }

  container.innerHTML = `
    <h1 class="view-title">Select a Godot Project</h1>
    <p class="view-subtitle">Choose a folder containing a <code style="font-family:var(--font-mono);background:var(--bg-elevated);padding:2px 6px;border-radius:4px">project.godot</code> file.</p>

    <button class="btn btn-primary" onclick="selectProject()" style="margin-bottom:32px">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/><line x1="12" y1="11" x2="12" y2="17"/><line x1="9" y1="14" x2="15" y2="14"/></svg>
      Browse for Project
    </button>

    ${recentHTML}
  `;
}

async function selectProject() {
  if (!api) return;
  const result = await api.select_project();
  if (result.success) {
    setActiveProject(result.path, result.name);
  } else if (result.error && result.error !== "Cancelled") {
    showToast(result.error, "error");
  }
}

async function openRecent(path, name) {
  if (!api) return;
  const result = await api.set_active_project(path);
  if (result.success) {
    setActiveProject(result.path, result.name);
  } else {
    showToast(result.error || "Project not found", "error");
  }
}

