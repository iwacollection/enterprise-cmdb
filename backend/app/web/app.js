const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const headers = {"Content-Type": "application/json", ...(options.headers || {})};
  if ((options.method || "GET") !== "GET") headers["X-CMDB-Actor"] = $("#actor").value;
  const response = await fetch(path, {...options, headers});
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
    <form id="environment-form"><h3>Create environment</h3><input name="name" placeholder="production" required><input name="description" placeholder="description"><button class="primary">Create</button></form>
    ${table(["Name", "Description", "ID"], items.map(x => [esc(x.name), esc(x.description), `<code>${esc(x.id)}</code>`]))}`;
  $("#environment-form").onsubmit = async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target));
    try { await api("/environments", {method: "POST", body: JSON.stringify(data)}); showMessage("Environment created"); await loadEnvironments(); }
    catch (error) { showMessage(error.message, true); }
  };
}

async function loadTeams() {
  const items = await api("/teams");
  $("#teams").innerHTML = `
    <h2>Teams</h2>
    <form id="team-form"><h3>Create team</h3><input name="name" placeholder="platform" required><input name="description" placeholder="description"><button class="primary">Create</button></form>
    ${table(["Name", "Description", "ID"], items.map(x => [esc(x.name), esc(x.description), `<code>${esc(x.id)}</code>`]))}`;
  $("#team-form").onsubmit = async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target));
    try { await api("/teams", {method: "POST", body: JSON.stringify(data)}); showMessage("Team created"); await loadTeams(); }
    catch (error) { showMessage(error.message, true); }
  };
}

async function loadServices() {
  const [items, teams] = await Promise.all([api("/services"), api("/teams")]);
  const teamName = Object.fromEntries(teams.map(x => [x.id, x.name]));
  $("#services").innerHTML = `
    <h2>Services</h2>
    <form id="service-form"><h3>Create service</h3><input name="name" placeholder="orders" required><select name="team_id" required><option value="">Owner team</option>${teams.map(x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`).join("")}</select><input name="description" placeholder="description"><button class="primary">Create</button></form>
    ${table(["Name", "Owner team", "Description", "ID"], items.map(x => [esc(x.name), esc(teamName[x.team_id] || x.team_id), esc(x.description), `<code>${esc(x.id)}</code>`]))}`;
  $("#service-form").onsubmit = async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target));
    try { await api("/services", {method: "POST", body: JSON.stringify(data)}); showMessage("Service created"); await loadServices(); }
    catch (error) { showMessage(error.message, true); }
  };
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
      <h3>Create asset</h3>
      <input name="name" placeholder="mysql-prod" required>
      <select name="asset_type">${types.map(x => `<option>${x}</option>`).join("")}</select>
      <select name="status"><option>active</option><option>inactive</option></select>
      <select name="environment_id" required><option value="">Environment</option>${environments.map(x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`).join("")}</select>
      <select name="team_id" required><option value="">Owner team</option>${teams.map(x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`).join("")}</select>
      <label>Services<select name="service_ids" multiple>${services.map(x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`).join("")}</select></label>
      <input name="description" placeholder="description">
      <label>Detail JSON<textarea name="detail" placeholder='{"engine":"mysql","version":"8.0"}'></textarea></label>
      <label>IPs JSON<textarea name="ips" placeholder='[{"address":"10.0.0.10/24","is_primary":true}]'></textarea></label>
      <label>Endpoints JSON<textarea name="endpoints" placeholder='[{"endpoint":"mysql.internal","port":3306,"protocol":"mysql"}]'></textarea></label>
      <button class="primary">Create</button>
    </form>
    ${table(["Name", "Type", "Status", "Environment", "Team", "Services", "IP / Endpoint", "Detail"], assets.map(x => [
      esc(x.name), esc(x.asset_type), esc(x.status), esc(envName[x.environment_id] || x.environment_id), esc(teamName[x.team_id] || x.team_id),
      x.service_ids.map(id => esc(serviceName[id] || id)).join("<br>"),
      [...x.ips.map(ip => esc(ip.address)), ...x.endpoints.map(ep => `${esc(ep.endpoint)}:${ep.port}`)].join("<br>"),
      `<code>${esc(JSON.stringify(x.detail))}</code>`
    ]))}`;
  $("#asset-form").onsubmit = async (event) => {
    event.preventDefault();
    const form = event.target;
    const data = Object.fromEntries(new FormData(form));
    data.service_ids = [...form.querySelector('[name="service_ids"]').selectedOptions].map(x => x.value);
    for (const field of ["detail", "ips", "endpoints"]) {
      const raw = form.elements[field].value.trim();
      data[field] = raw ? JSON.parse(raw) : (field === "detail" ? null : []);
    }
    try { await api("/assets", {method: "POST", body: JSON.stringify(data)}); showMessage("Asset created"); await loadAssets(); }
    catch (error) { showMessage(error.message, true); }
  };
}

async function loadRelations() {
  const assets = await api("/assets");
  $("#relations").innerHTML = `
    <h2>Relations</h2>
    <form id="relation-form"><h3>Create relation</h3>
      <select name="source_asset_id" required><option value="">Source asset</option>${assets.map(x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`).join("")}</select>
      <input name="relation_type" placeholder="depends_on" required>
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
      $("#relation-list").innerHTML = table(["Source", "Type", "Target"], items.map(x => [esc(x.source_asset_id), esc(x.relation_type), esc(x.target_asset_id)]));
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
