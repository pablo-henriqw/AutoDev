const list = document.querySelector("#report-list");

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, c => ({
    "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
  }[c]));
}

async function loadReports() {
  list.innerHTML = '<p class="muted">Carregando...</p>';
  try {
    const response = await fetch("/api/reports");
    if (response.status === 401) { location.href = "/login"; return; }
    const reports = await response.json();
    document.querySelector("#total").textContent = reports.length;
    document.querySelector("#pending").textContent = reports.filter(r => r.status === "new").length;
    document.querySelector("#high").textContent = reports.filter(r => r.risk === "high").length;

    if (!reports.length) {
      list.innerHTML = '<p class="muted">Nenhum relato ainda. Envie um teste pelo widget do site.</p>';
      return;
    }
    list.innerHTML = reports.map(r => `
      <article class="report">
        <div>
          <h3>#${r.id} · ${escapeHtml(r.title)}</h3>
          <p>${escapeHtml(r.description)}</p>
          <div class="meta">${escapeHtml(r.page_url || "Página não informada")} · ${escapeHtml(r.created_at)}</div>
          <div class="actions">
            <button class="secondary analyze" data-id="${r.id}">${r.analysis ? "Analisar novamente" : "Analisar com IA"}</button>
          </div>
        </div>
        <span class="pill ${r.risk || ""}">${escapeHtml(r.risk || r.status)}</span>
        ${r.analysis ? `<div class="analysis">${escapeHtml(r.analysis)}</div>` : ""}
      </article>`).join("");
    document.querySelectorAll(".analyze").forEach(button => {
      button.addEventListener("click", () => analyze(button));
    });
  } catch {
    list.innerHTML = '<p class="muted">Não foi possível carregar os relatos.</p>';
  }
}

async function analyze(button) {
  button.disabled = true;
  button.textContent = "Analisando...";
  try {
    const response = await fetch(`/api/reports/${button.dataset.id}/analyze`, {method:"POST"});
    if (!response.ok) throw new Error("Falha na análise");
    await loadReports();
  } catch {
    button.disabled = false;
    button.textContent = "Tentar novamente";
    alert("Não foi possível analisar este relato.");
  }
}

document.querySelector("#refresh").addEventListener("click", loadReports);
loadReports();
