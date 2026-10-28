const icons = {
  dashboard: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  car: '<path d="M3 13l2-5a2 2 0 0 1 1.9-1.3h10.2A2 2 0 0 1 19 8l2 5"/><path d="M3 13h18v4H3z"/><circle cx="7" cy="17" r="1.5"/><circle cx="17" cy="17" r="1.5"/>',
  clipboard: '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M9 14l2 2 4-4"/>',
  chart: '<path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6" rx="1"/><rect x="12" y="8" width="3" height="10" rx="1"/><rect x="17" y="5" width="3" height="13" rx="1"/>',
  gear: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  pdf: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8M8 17h6"/>',
  whatsapp: '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>'
};

const icon = (name) =>
  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${icons[name] || ""}</svg>`;

const nav = [
  {
    section: "Principal",
    items: [
      { id: "dashboard", label: "Dashboard", href: "t01-dashboard.html", icon: "dashboard" },
      { id: "os", label: "Ordens de Serviço", href: "t04-ordens-servico.html", icon: "clipboard" }
    ]
  },
  {
    section: "Cadastros",
    items: [
      { id: "clientes", label: "Clientes", href: "t02-clientes.html", icon: "users" },
      { id: "veiculos", label: "Veículos", href: "t03-veiculos.html", icon: "car" }
    ]
  },
  {
    section: "Gestão",
    items: [
      { id: "relatorios", label: "Relatórios", href: "t07-relatorios.html", icon: "chart" },
      { id: "config", label: "Configurações", href: "t08-configuracoes.html", icon: "gear" }
    ]
  }
];

const activeMap = {
  dashboard: "dashboard",
  clientes: "clientes",
  veiculos: "veiculos",
  os: "os",
  editor: "os",
  orcamento: "os",
  relatorios: "relatorios",
  config: "config"
};

const params = new URLSearchParams(location.search);
const isEmbedded = params.get("embed") === "1";
if (isEmbedded) document.body.classList.add("embed");

// Permite capturar a tela de lista sem o drawer de exemplo.
if (params.get("list") === "1") {
  const overlay = document.querySelector(".drawer-overlay");
  if (overlay) overlay.style.display = "none";
}

const sidebar = document.getElementById("sidebar");
if (sidebar) {
  const current = activeMap[document.body.dataset.screen] || "";
  const groups = nav
    .map(
      (group) => `
      <div class="nav-label">${group.section}</div>
      <div class="nav">
        ${group.items
          .map(
            (item) => `
          <a href="${item.href}" data-goto class="${item.id === current ? "active" : ""}">
            ${icon(item.icon)}
            <span>${item.label}</span>
          </a>`
          )
          .join("")}
      </div>`
    )
    .join("");

  sidebar.innerHTML = `
    <div class="brand">
      <img src="../../../assets/logo.svg" alt="DevSolo Studio">
      <div>
        <div class="name">DevSolo Studio</div>
        <div class="product">OficinaPro</div>
      </div>
    </div>
    ${groups}
    <div class="sidebar-footer">
      OficinaPro v1.0<br>
      Protótipo de interface • Etapa 2
    </div>
  `;
}

// Navegação interna preserva o modo embutido do protótipo.
document.addEventListener("click", (event) => {
  const link = event.target.closest("a[data-goto]");
  if (!link || !isEmbedded) return;
  event.preventDefault();
  const url = new URL(link.getAttribute("href"), location.href);
  url.searchParams.set("embed", "1");
  location.href = url.toString();
});

// Pequenas interações para a demonstração.
document.querySelectorAll(".tabs .tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    tab.parentElement.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
  });
});

document.querySelectorAll(".chip[data-filter]").forEach((chip) => {
  chip.addEventListener("click", () => {
    chip.parentElement.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
    chip.classList.add("active");
  });
});

function showToast(message) {
  let toast = document.querySelector(".toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add("show");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("show"), 2400);
}

document.addEventListener("click", (event) => {
  const el = event.target.closest("[data-toast]");
  if (!el) return;
  event.preventDefault();
  showToast(el.dataset.toast);
});
