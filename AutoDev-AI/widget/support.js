(() => {
  const script = document.currentScript;
  const apiBase = (script?.dataset.api || new URL(script.src).origin).replace(/\/$/, "");
  const css = document.createElement("link");
  css.rel = "stylesheet";
  css.href = `${apiBase}/widget/support.css`;
  document.head.appendChild(css);

  const button = document.createElement("button");
  button.className = "autodev-launcher";
  button.type = "button";
  button.textContent = "Ajuda";
  button.setAttribute("aria-label", "Abrir suporte");
  const panel = document.createElement("section");
  panel.className = "autodev-panel";
  panel.innerHTML = `
    <header><strong>Como podemos ajudar?</strong><button type="button" class="autodev-close" aria-label="Fechar">×</button></header>
    <form class="autodev-form">
      <label>O que aconteceu?<input name="title" maxlength="120" required minlength="4" placeholder="Ex.: Não consigo concluir cadastro"></label>
      <label>Conte mais detalhes<textarea name="description" maxlength="3000" required minlength="10" placeholder="Descreva o que você estava fazendo..."></textarea></label>
      <label>E-mail (opcional)<input name="email" type="email" maxlength="254" placeholder="voce@email.com"></label>
      <button class="autodev-send" type="submit">Enviar relato</button>
      <p class="autodev-message" role="status"></p>
    </form>`;
  document.body.append(button, panel);

  button.addEventListener("click", () => panel.classList.toggle("open"));
  panel.querySelector(".autodev-close").addEventListener("click", () => panel.classList.remove("open"));
  panel.querySelector("form").addEventListener("submit", async event => {
    event.preventDefault();
    const form = event.currentTarget;
    const send = form.querySelector("button[type=submit]");
    const message = form.querySelector(".autodev-message");
    send.disabled = true;
    message.textContent = "Enviando...";
    const data = Object.fromEntries(new FormData(form).entries());
    data.page_url = location.href;
    try {
      const response = await fetch(`${apiBase}/api/reports`, {
        method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(data)
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Não foi possível enviar.");
      form.reset();
      message.textContent = `Relato enviado! Protocolo #${result.id}.`;
    } catch (error) {
      message.textContent = error.message || "Erro ao enviar. Tente novamente.";
    } finally {
      send.disabled = false;
    }
  });
})();
