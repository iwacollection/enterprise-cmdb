const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers = {"Content-Type": "application/json", ...(options.headers || {})};
  if (!['GET', 'HEAD'].includes(method)) {
    const actor = $("#actor").value.trim();
    if (!actor) throw new Error("写操作前请填写操作人");
    headers["X-CMDB-Actor"] = actor;
  }
  const response = await fetch(path, {...options, method, headers});
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
  if (response.status === 204) return null;
  return response.json();
}

function showMessage(text, error = false) {
  const box = $("#message");
  box.textContent = text;
  box.className = `message${error ? " error" : ""}`;
  setTimeout(() => box.classList.add("hidden"), 3500);
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function table(headers, rows) {
  return `<table><thead><tr>${headers.map(h => `<th>${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}

async function loadOverview() {
  const [assets, services, teams, environments] = await Promise.all([
    api("/assets"), api("/services"), api("/teams"), api("/environments")
  ]);
  const byType = Object.entries(assets.reduce((acc, item) => {
    acc[item.asset_type] = (acc[item.asset_type] || 0) + 1;
    return acc;
  }, {}));
  $("#overview").innerHTML = `
    <h2>Overview</h2>
    <div class="grid">
      <div class="card"><div>Assets</div><div class="metric">${assets.length}</div></div>
      <div class="card"><div>Services</div><div class="metric">${services.length}</div></div>
      <div class="card"><div>Teams</div><div class="metric">${teams.length}</div></div>
      <div class="card"><div>Environments</div><div class="metric">${environments.length}</div></div>
    </div>
    <h3>Assets by type</h3>
    ${table(["Type", "Count"], byType.map(([type, count]) => [esc(type), count]))}`;
}

async function loadEnvironments() {
  const items = await api("/environments");
  $("#environments").innerHTML = `
    <h2>Environments</h2>
    <form id="environment-form">
      <h3 id="environment-form-title">Create environment</h3>
      <input name="name" maxlength="128" placeholder="production" required>
      <input name="description" placeholder="description">
      <button id="environment-submit" class="primary">Create</button>
      <button id="environment-cancel" type="button" class="hidden">Cancel</button>
    </form>
    ${table(["Name", "Description", "ID", "Actions"], items.map(x => [
      esc(x.name), esc(x.description), `<code>${esc(x.id)}</code>`,
      `<button data-edit-environment="${esc(x.id)}">Edit</button> <button data-delete-environment="${esc(x.id)}">Delete</button>`
    ]))}`;

  const form = $("#environment-form");
  form.onsubmit = async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    const id = form.dataset.environmentId;
    try {
      await api(id ? `/environments/${id}` : "/environments", {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(data),
      });
      showMessage(id ? "Environment updated" : "Environment created");
      await loadEnvironments();
    } catch (error) { showMessage(error.message, true); }
  };
  $("#environment-cancel").onclick = () => loadEnvironments();

  document.querySelectorAll("[data-edit-environment]").forEach(button => button.onclick = () => {
    const item = items.find(x => x.id === button.dataset.editEnvironment);
    form.dataset.environmentId = item.id;
    form.elements.name.value = item.name;
    form.elements.description.value = item.description || "";
    $("#environment-form-title").textContent = "Edit environment";
    $("#environment-submit").textContent = "Update";
    $("#environment-cancel").classList.remove("hidden");
  });
  document.querySelectorAll("[data-delete-environment]").forEach(button => button.onclick = async () => {
    if (!confirm("Delete this environment?")) return;
    try {
      await api(`/environments/${button.dataset.deleteEnvironment}`, {method: "DELETE"});
      showMessage("Environment deleted");
      await loadEnvironments();
    } catch (error) { showMessage(error.message, true); }
  });
}

async function loadTeams() {
  const items = await api("/teams");
  $("#teams").innerHTML = `
    <h2>Teams</h2>
    <form id="team-form">
      <h3 id="team-form-title">Create team</h3>
      <input name="name" maxlength="128" placeholder="platform" required>
      <input name="description" placeholder="description">
      <button id="team-submit" class="primary">Create</button>
      <button id="team-cancel" type="button" class="hidden">Cancel</button>
    </form>
    ${table(["Name", "Description", "ID", "Actions"], items.map(x => [
      esc(x.name), esc(x.description), `<code>${esc(x.id)}</code>`,
      `<button data-edit-team="${esc(x.id)}">Edit</button> <button data-delete-team="${esc(x.id)}">Delete</button>`
    ]))}`;

  const form = $("#team-form");
  form.onsubmit = async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    const id = form.dataset.teamId;
    try {
      await api(id ? `/teams/${id}` : "/teams", {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(data),
      });
      showMessage(id ? "Team updated" : "Team created");
      await loadTeams();
    } catch (error) { showMessage(error.message, true); }
  };
  $("#team-cancel").onclick = () => loadTeams();

  document.querySelectorAll("[data-edit-team]").forEach(button => button.onclick = () => {
    const item = items.find(x => x.id === button.dataset.editTeam);
    form.dataset.teamId = item.id;
    form.elements.name.value = item.name;
    form.elements.description.value = item.description || "";
    $("#team-form-title").textContent = "Edit team";
    $("#team-submit").textContent = "Update";
    $("#team-cancel").classList.remove("hidden");
  });
  document.querySelectorAll("[data-delete-team]").forEach(button => button.onclick = async () => {
    if (!confirm("Delete this team?")) return;
    try {
      await api(`/teams/${button.dataset.deleteTeam}`, {method: "DELETE"});
      showMessage("Team deleted");
      await loadTeams();
    } catch (error) { showMessage(error.message, true); }
  });
}

async function loadServices() {
  const [items, teams] = await Promise.all([api("/services"), api("/teams")]);
  const teamName = Object.fromEntries(teams.map(x => [x.id, x.name]));
  $("#services").innerHTML = `
    <h2>Services</h2>
    <form id="service-form">
      <h3 id="service-form-title">Create service</h3>
      <input name="name" maxlength="128" placeholder="orders" required>
      <select name="team_id" required><option value="">Owner team</option>${teams.map(x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`).join("")}</select>
      <input name="description" placeholder="description">
      <button id="service-submit" class="primary">Create</button>
      <button id="service-cancel" type="button" class="hidden">Cancel</button>
    </form>
    ${table(["Name", "Owner team", "Description", "ID", "Actions"], items.map(x => [
      esc(x.name), esc(teamName[x.team_id] || x.team_id), esc(x.description), `<code>${esc(x.id)}</code>`,
      `<button data-edit-service="${esc(x.id)}">Edit</button> <button data-delete-service="${esc(x.id)}">Delete</button>`
    ]))}`;

  const form = $("#service-form");
  form.onsubmit = async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    const id = form.dataset.serviceId;
    try {
      await api(id ? `/services/${id}` : "/services", {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(data),
      });
      showMessage(id ? "Service updated" : "Service created");
      await loadServices();
    } catch (error) { showMessage(error.message, true); }
  };
  $("#service-cancel").onclick = () => loadServices();

  document.querySelectorAll("[data-edit-service]").forEach(button => button.onclick = () => {
    const item = items.find(x => x.id === button.dataset.editService);
    form.dataset.serviceId = item.id;
    form.elements.name.value = item.name;
    form.elements.team_id.value = item.team_id;
    form.elements.description.value = item.description || "";
    $("#service-form-title").textContent = "Edit service";
    $("#service-submit").textContent = "Update";
    $("#service-cancel").classList.remove("hidden");
  });
  document.querySelectorAll("[data-delete-service]").forEach(button => button.onclick = async () => {
    if (!confirm("Delete this service?")) return;
    try {
      await api(`/services/${button.dataset.deleteService}`, {method: "DELETE"});
      showMessage("Service deleted");
      await loadServices();
    } catch (error) { showMessage(error.message, true); }
  });
}

async function loadAssets() {
  const [assets, environments, teams, services] = await Promise.all([
    api("/assets"), api("/environments"), api("/teams"), api("/services")
  ]);
  const envName = Object.fromEntries(environments.map(x => [x.id, x.name]));
  const teamName = Object.fromEntries(teams.map(x => [x.id, x.name]));
  const serviceName = Object.fromEntries(services.map(x => [x.id, x.name]));
  const types = ["server", "virtual_machine", "database", "redis", "message_queue", "load_balancer", "kubernetes_cluster"];
  $("#assets").innerHTML = `
    <h2>Assets</h2>
    <form id="asset-form">
      <h3 id="asset-form-title">Create asset</h3>
      <input name="name" maxlength="255" placeholder="mysql-prod" required>
      <select name="asset_type">${types.map(x => `<option>${x}</option>`).join("")}</select>
      <select name="status"><option>active</option><option>inactive</option></select>
      <select name="environment_id" required><option value="">Environment</option>${environments.map(x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`).join("")}</select>
      <select name="team_id" required><option value="">Owner team</option>${teams.map(x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`).join("")}</select>
      <label>Services<select name="service_ids" multiple>${services.map(x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`).join("")}</select></label>
      <input name="description" placeholder="description">
      <label>Detail JSON<textarea name="detail" placeholder='{"engine":"mysql","version":"8.0"}'></textarea></label>
      <label>IPs JSON<textarea name="ips" placeholder='[{"address":"10.0.0.10/24","is_primary":true}]'></textarea></label>
      <label>Endpoints JSON<textarea name="endpoints" placeholder='[{"endpoint":"mysql.internal","port":3306,"protocol":"mysql"}]'></textarea></label>
      <button id="asset-submit" class="primary">Create</button>
      <button id="asset-cancel" type="button" class="hidden">Cancel</button>
    </form>
    ${table(["Name", "Type", "Status", "Environment", "Team", "Services", "IP / Endpoint", "Detail", "Actions"], assets.map(x => [
      esc(x.name), esc(x.asset_type), esc(x.status), esc(envName[x.environment_id] || x.environment_id), esc(teamName[x.team_id] || x.team_id),
      x.service_ids.map(id => esc(serviceName[id] || id)).join("<br>"),
      [...x.ips.map(ip => esc(ip.address)), ...x.endpoints.map(ep => `${esc(ep.endpoint)}:${ep.port}`)].join("<br>"),
      `<code>${esc(JSON.stringify(x.detail))}</code>`,
      `<button data-edit-asset="${esc(x.id)}">Edit</button>`
    ]))}`;

  const form = $("#asset-form");
  form.onsubmit = async (event) => {
    event.preventDefault();
    try {
      const data = Object.fromEntries(new FormData(form));
      data.service_ids = [...form.querySelector('[name="service_ids"]').selectedOptions].map(x => x.value);
      for (const field of ["detail", "ips", "endpoints"]) {
        const raw = form.elements[field].value.trim();
        data[field] = raw ? JSON.parse(raw) : (field === "detail" ? null : []);
      }
      const id = form.dataset.assetId;
      await api(id ? `/assets/${id}` : "/assets", {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(data),
      });
      showMessage(id ? "Asset updated" : "Asset created");
      await loadAssets();
    } catch (error) { showMessage(error.message, true); }
  };
  $("#asset-cancel").onclick = () => loadAssets();

  document.querySelectorAll("[data-edit-asset]").forEach(button => button.onclick = () => {
    const item = assets.find(x => x.id === button.dataset.editAsset);
    form.dataset.assetId = item.id;
    form.elements.name.value = item.name;
    form.elements.asset_type.value = item.asset_type;
    form.elements.status.value = item.status;
    form.elements.environment_id.value = item.environment_id;
    form.elements.team_id.value = item.team_id;
    form.elements.description.value = item.description || "";
    [...form.elements.service_ids.options].forEach(option => {
      option.selected = item.service_ids.includes(option.value);
    });
    form.elements.detail.value = item.detail ? JSON.stringify(item.detail, null, 2) : "";
    form.elements.ips.value = item.ips.length ? JSON.stringify(item.ips.map(ip => ({
      address: ip.address,
      role: ip.role,
      is_primary: ip.is_primary,
    })), null, 2) : "";
    form.elements.endpoints.value = item.endpoints.length ? JSON.stringify(item.endpoints.map(endpoint => ({
      endpoint: endpoint.endpoint,
      port: endpoint.port,
      protocol: endpoint.protocol,
      role: endpoint.role,
      is_primary: endpoint.is_primary,
    })), null, 2) : "";
    $("#asset-form-title").textContent = "Edit asset";
    $("#asset-submit").textContent = "Update";
    $("#asset-cancel").classList.remove("hidden");
  });
}

async function loadRelations() {
  const assets = await api("/assets");
  const assetName = Object.fromEntries(assets.map(x => [x.id, x.name]));
  $("#relations").innerHTML = `
    <h2>Relations</h2>
    <form id="relation-form"><h3>Create relation</h3>
      <select name="source_asset_id" required><option value="">Source asset</option>${assets.map(x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`).join("")}</select>
      <input name="relation_type" maxlength="64" placeholder="depends_on" required>
      <select name="target_asset_id" required><option value="">Target asset</option>${assets.map(x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`).join("")}</select>
      <input name="description" placeholder="description"><button class="primary">Create</button></form>
    <div id="relation-list">Select an asset below to inspect relations.</div>
    ${table(["Asset", "Inspect"], assets.map(x => [esc(x.name), `<button data-relations="${esc(x.id)}">Show</button>`]))}`;
  $("#relation-form").onsubmit = async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target));
    try { await api("/relations", {method: "POST", body: JSON.stringify(data)}); showMessage("Relation created"); }
    catch (error) { showMessage(error.message, true); }
  };
  document.querySelectorAll("[data-relations]").forEach(button => button.onclick = async () => {
    try {
      const items = await api(`/assets/${button.dataset.relations}/relations?direction=both`);
      $("#relation-list").innerHTML = table(["Source", "Type", "Target", "Actions"], items.map(x => [
        esc(assetName[x.source_asset_id] || x.source_asset_id),
        esc(x.relation_type),
        esc(assetName[x.target_asset_id] || x.target_asset_id),
        `<button data-delete-relation="${esc(x.id)}">Delete</button>`
      ]));
      document.querySelectorAll("[data-delete-relation]").forEach(deleteButton => deleteButton.onclick = async () => {
        if (!confirm("Delete this relation?")) return;
        try {
          await api(`/relations/${deleteButton.dataset.deleteRelation}`, {method: "DELETE"});
          showMessage("Relation deleted");
          button.click();
        } catch (error) { showMessage(error.message, true); }
      });
    } catch (error) { showMessage(error.message, true); }
  });
}

async function loadChanges() {
  const items = await api("/changes");
  $("#changes").innerHTML = `<h2>Changes</h2>${table(["Time", "Actor", "Entity", "Action", "Before", "After"], items.map(x => [
    esc(x.created_at), esc(x.changed_by), `${esc(x.entity_type)}<br><code>${esc(x.entity_id)}</code>`, esc(x.action), `<code>${esc(JSON.stringify(x.before))}</code>`, `<code>${esc(JSON.stringify(x.after))}</code>`
  ]))}`;
}

const loaders = {overview: loadOverview, assets: loadAssets, services: loadServices, teams: loadTeams, environments: loadEnvironments, relations: loadRelations, changes: loadChanges};

document.querySelectorAll("nav button").forEach(button => button.onclick = async () => {
  document.querySelectorAll(".view").forEach(view => view.classList.add("hidden"));
  $(`#${button.dataset.view}`).classList.remove("hidden");
  try { await loaders[button.dataset.view](); } catch (error) { showMessage(error.message, true); }
});

loadOverview().catch(error => showMessage(error.message, true));
