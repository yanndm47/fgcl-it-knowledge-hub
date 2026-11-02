/**
 * Fonctions partagées par toutes les pages : appel de l'API, gestion du
 * jeton de connexion (stocké dans le navigateur via localStorage — ce
 * n'est pas un artifact Claude, c'est une vraie page web autonome, donc
 * localStorage fonctionne normalement ici).
 */

// En local (développement) : parle au backend local. Une fois déployé
// (ex. sur GitHub Pages), parle au backend en ligne (ex. Render) — à
// remplacer ci-dessous par la vraie adresse une fois le backend déployé.
const DEPLOYED_API_BASE = "https://REMPLACE-MOI.onrender.com";
const API_BASE = (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost")
  ? "http://127.0.0.1:8000"
  : DEPLOYED_API_BASE;

function getToken() {
  return localStorage.getItem("ikh_token");
}

function setToken(token) {
  localStorage.setItem("ikh_token", token);
}

function clearToken() {
  localStorage.removeItem("ikh_token");
}

function requireAuth() {
  // À appeler en haut de chaque page qui exige d'être connecté.
  if (!getToken()) {
    window.location.href = "login.html";
  }
}

function logout() {
  clearToken();
  window.location.href = "login.html";
}

/**
 * Appelle l'API et renvoie le JSON de la réponse.
 * Ajoute automatiquement le jeton s'il existe.
 * Lève une erreur avec le message renvoyé par le backend en cas d'échec.
 */
async function apiFetch(path, options = {}) {
  const headers = options.headers || {};
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (response.status === 204) {
    return null; // pas de contenu (ex. rejet d'un compte)
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = data.detail || "Une erreur est survenue.";
    throw new Error(message);
  }

  return data;
}

/** Récupère les infos du technicien connecté ; redirige vers login si le jeton est invalide/expiré. */
async function fetchCurrentTechnician() {
  try {
    return await apiFetch("/auth/me");
  } catch (err) {
    clearToken();
    window.location.href = "login.html";
    return null;
  }
}

/** Remplit un <select> avec la liste des départements. */
async function populateDepartments(selectElement) {
  const departments = await apiFetch("/departments");
  departments.forEach((dept) => {
    const option = document.createElement("option");
    option.value = dept.id;
    option.textContent = dept.nom;
    selectElement.appendChild(option);
  });
}

function statusPill(status) {
  const label = status === "ferme" ? "Fermé" : "Ouvert";
  const cls = status === "ferme" ? "pill-ferme" : "pill-ouvert";
  return `<span class="pill ${cls}"><span class="dot"></span>${label}</span>`;
}

function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" });
}

function shortId(id) {
  return id ? id.slice(0, 8) : "";
}

/**
 * Construit la barre latérale (sidebar), fidèle à la maquette fournie :
 * logo, navigation principale, puis section basse (notifications, profil,
 * déconnexion). 'page' identifie la page active pour la surligner.
 */
function renderSidebar(me, page) {
  const link = (href, icon, label, key) =>
    `<a href="${href}" class="sidebar-link ${page === key ? "active" : ""}"><span class="icon">${icon}</span>${label}</a>`;

  const disabledLink = (icon, label) =>
    `<span class="sidebar-link disabled" title="Extension future, hors périmètre actuel"><span class="icon">${icon}</span>${label}</span>`;

  const adminLink = me.role === "admin"
    ? link("admin-dashboard.html", "🛡️", "Espace admin", "admin")
    : "";

  return `
    <div class="sidebar-logo">
      <img src="assets/logo.png" alt="FGCL">
    </div>
    <nav class="sidebar-nav">
      ${link("dashboard.html", "🏠", "Accueil", "dashboard")}
      ${link("chatbot.html", "🤖", "Assistant IA", "chatbot")}
      ${link("incidents.html", "📋", "Incidents", "incidents")}
      ${disabledLink("🗂️", "Problèmes")}
      ${link("connaissances.html", "📚", "Connaissances", "connaissances")}
      ${link("historique.html", "🕒", "Historique", "historique")}
      ${link("favoris.html", "⭐", "Favoris", "favoris")}
      ${adminLink}
    </nav>
    <div class="sidebar-footer">
      <a href="#" class="sidebar-link" id="sidebar-notif-link"><span class="icon">🔔</span>Notifications</a>
      ${link("profil.html", "👤", "Profil", "profil")}
      <a href="#" class="sidebar-link" id="logout-link"><span class="icon">🚪</span>Déconnexion</a>
    </div>
  `;
}

/**
 * Barre supérieure : recherche (décorative pour l'instant) + identité du
 * technicien connecté, avec ses initiales en avatar.
 */
function renderTopheader(me) {
  const initials = me.email.slice(0, 2).toUpperCase();
  return `
    <button class="menu-toggle" id="menu-toggle" aria-label="Ouvrir le menu">☰</button>
    <input type="text" class="search-input" placeholder="Rechercher incidents, solutions...">
    <div class="notif-wrapper">
      <button class="notif-bell" id="notif-bell" aria-label="Notifications">
        🔔<span class="notif-badge" id="notif-badge" style="display:none;">0</span>
      </button>
      <div class="notif-dropdown" id="notif-dropdown"></div>
    </div>
    <div class="user-chip">
      <div class="user-avatar">${initials}</div>
      <div class="user-meta">
        <div class="name">${me.email}</div>
        <div class="role">${me.role === "admin" ? "Administrateur" : "Technicien"}</div>
      </div>
    </div>
  `;
}

/** Ouvre/ferme la sidebar sur mobile (bouton hamburger + fond assombri cliquable). */
function attachMobileMenu() {
  const toggle = document.getElementById("menu-toggle");
  const sidebar = document.getElementById("sidebar");
  if (!toggle || !sidebar) return;

  let overlay = document.getElementById("sidebar-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "sidebar-overlay";
    overlay.className = "sidebar-overlay";
    document.body.appendChild(overlay);
  }

  function closeMenu() {
    sidebar.classList.remove("open");
    overlay.classList.remove("visible");
  }

  toggle.addEventListener("click", () => {
    sidebar.classList.toggle("open");
    overlay.classList.toggle("visible");
  });
  overlay.addEventListener("click", closeMenu);
  sidebar.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
}

/** Injecte la sidebar + le topheader dans le squelette de page, et branche la déconnexion. */
function renderAppShell(me, page) {
  document.getElementById("sidebar").innerHTML = renderSidebar(me, page);
  document.getElementById("topheader").innerHTML = renderTopheader(me);
  attachLogout();
  attachMobileMenu();
  setupNotifications();
}

function attachLogout() {
  const link = document.getElementById("logout-link");
  if (link) {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      logout();
    });
  }
}

/* ============================================================
   Notifications en temps réel (WebSocket)
   ============================================================ */

let notifSocket = null;
let notifCache = [];

function timeAgo(isoString) {
  const diffMin = Math.round((Date.now() - new Date(isoString).getTime()) / 60000);
  if (diffMin < 1) return "à l'instant";
  if (diffMin < 60) return `il y a ${diffMin} min`;
  const diffH = Math.round(diffMin / 60);
  if (diffH < 24) return `il y a ${diffH} h`;
  return `il y a ${Math.round(diffH / 24)} j`;
}

function updateNotifBadge() {
  const badge = document.getElementById("notif-badge");
  if (!badge) return;
  const unread = notifCache.filter((n) => !n.is_read).length;
  badge.style.display = unread > 0 ? "inline-flex" : "none";
  badge.textContent = unread > 9 ? "9+" : String(unread);
}

function renderNotifDropdown() {
  const dropdown = document.getElementById("notif-dropdown");
  if (!dropdown) return;
  if (notifCache.length === 0) {
    dropdown.innerHTML = `<div class="notif-empty">Aucune notification pour l'instant.</div>`;
    return;
  }
  dropdown.innerHTML = notifCache.map((n) => `
    <div class="notif-item ${n.is_read ? "" : "unread"}" data-id="${n.id}" data-incident="${n.related_incident_id || ""}">
      <div class="notif-message">${n.message}</div>
      <div class="notif-time">${timeAgo(n.created_at)}</div>
    </div>
  `).join("");

  dropdown.querySelectorAll(".notif-item").forEach((el) => {
    el.addEventListener("click", async () => {
      const id = el.dataset.id;
      const incidentId = el.dataset.incident;
      try {
        await apiFetch(`/notifications/${id}/read`, { method: "POST" });
        const notif = notifCache.find((n) => n.id === id);
        if (notif) notif.is_read = true;
        updateNotifBadge();
        renderNotifDropdown();
      } catch (e) { /* silencieux : ce n'est qu'un marquage de lecture */ }
      if (incidentId) window.location.href = `incident-detail.html?id=${incidentId}`;
    });
  });
}

async function loadNotifications() {
  try {
    notifCache = await apiFetch("/notifications");
  } catch (e) {
    notifCache = [];
  }
  updateNotifBadge();
  renderNotifDropdown();
}

function connectNotificationSocket() {
  const token = getToken();
  if (!token) return;
  const wsProtocol = API_BASE.startsWith("https") ? "wss" : "ws";
  const wsUrl = `${API_BASE.replace(/^https?/, wsProtocol)}/notifications/ws?token=${encodeURIComponent(token)}`;

  notifSocket = new WebSocket(wsUrl);
  notifSocket.onmessage = (event) => {
    const notif = JSON.parse(event.data);
    notifCache.unshift(notif); // la plus récente en premier
    updateNotifBadge();
    renderNotifDropdown();
  };
  // Pas de reconnexion automatique dans cette version : une notification manquée
  // pendant une coupure reste consultable via GET /notifications au rechargement.
  notifSocket.onerror = () => {};
}

function attachNotifDropdownToggle() {
  const bell = document.getElementById("notif-bell");
  const dropdown = document.getElementById("notif-dropdown");
  const sidebarLink = document.getElementById("sidebar-notif-link");
  if (!bell || !dropdown) return;

  bell.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdown.classList.toggle("visible");
  });
  if (sidebarLink) {
    sidebarLink.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropdown.classList.toggle("visible");
    });
  }
  document.addEventListener("click", (e) => {
    if (!dropdown.contains(e.target) && e.target !== bell && e.target !== sidebarLink) {
      dropdown.classList.remove("visible");
    }
  });
}

/** À appeler une fois, juste après renderAppShell(), sur chaque page connectée. */
async function setupNotifications() {
  attachNotifDropdownToggle();
  await loadNotifications();
  connectNotificationSocket();
}
