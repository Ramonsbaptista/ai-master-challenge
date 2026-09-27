document.addEventListener("DOMContentLoaded", () => {
  const ticket = document.querySelector("#ticket");
  const count = document.querySelector("#char-count");
  const updateCount = () => { if (ticket && count) count.textContent = `${ticket.value.length} caracteres`; };
  if (ticket) {
    updateCount(); ticket.addEventListener("input", updateCount);
    document.querySelectorAll("[data-example]").forEach(button => button.addEventListener("click", () => {
      ticket.value = button.dataset.example; updateCount(); ticket.focus();
    }));
  }
  const target = document.querySelector("#evaluation-result[data-result-url]");
  if (target) fetch(target.dataset.resultUrl).then(async response => {
    if (!response.ok) { const data = await response.json(); throw new Error(`${data.error} ${data.detail || ""}`); }
    return response.text();
  }).then(html => { target.classList.remove("loading"); target.innerHTML = html; })
    .catch(error => { target.classList.remove("loading"); target.classList.add("notice", "error"); target.innerHTML = `<h2>A avaliação não pôde ser concluída</h2><p>${error.message}</p>`; });
});
