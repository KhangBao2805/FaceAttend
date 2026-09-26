/* FaceAttend client utils: api, theme, toast, modal, avatar, badge, camera */
// --- API wrapper (utils/api) ---
async function api(url, method = "GET", body = null) {
  const r = await fetch(url, {
    method, headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : null
  });
  if (r.status === 401) { location.href = "/login"; throw new Error("auth"); }
  return r.json();
}
// --- Theme (hooks/useTheme) ---
(function initTheme() {
  document.documentElement.dataset.theme = localStorage.getItem("fa-theme") || "light";
})();
function toggleTheme() {
  const t = document.documentElement.dataset.theme === "light" ? "dark" : "light";
  document.documentElement.dataset.theme = t;
  localStorage.setItem("fa-theme", t);
}
// --- Sidebar ---
function toggleSidebar() {
  if (window.innerWidth <= 768) document.body.classList.toggle("nav-open");
  else document.body.classList.toggle("collapsed");
}
// --- Toast (components/Toast) ---
function toast(msg, type = "") {
  const w = document.getElementById("toasts") || (() => {
    const d = document.createElement("div"); d.id = "toasts"; d.className = "toast-wrap";
    document.body.appendChild(d); return d;
  })();
  const t = document.createElement("div");
  t.className = "toast " + type; t.textContent = msg;
  w.appendChild(t); setTimeout(() => t.remove(), 3600);
}
// --- Modal (components/Modal) ---
function openModal(html) {
  closeModal();
  const bg = document.createElement("div");
  bg.className = "modal-bg"; bg.id = "modalBg";
  bg.innerHTML = `<div class="modal">${html}</div>`;
  bg.onclick = e => { if (e.target === bg) closeModal(); };
  document.body.appendChild(bg);
}
function closeModal() { document.getElementById("modalBg")?.remove(); }
function confirmModal(title, msg, onOk) {
  openModal(`<h3>${title}</h3><p class="muted">${msg}</p>
    <div style="display:grid;gap:8px;margin-top:14px">
    <button class="btn red" id="cfOk">Xác nhận</button>
    <button class="btn ghost" onclick="closeModal()">Hủy</button></div>`);
  document.getElementById("cfOk").onclick = () => { closeModal(); onOk(); };
}
// --- Avatar / Badge (components) ---
function avatarHTML(name, color, size = 34) {
  const ini = (name || "?").trim().split(/\s+/).slice(-2).map(w => w[0]).join("").toUpperCase();
  return `<span class="avatar" style="background:${color || "#2563eb"};width:${size}px;height:${size}px">${ini}</span>`;
}
function statusBadge(s) {
  if (s === "Có mặt") return '<span class="badge b-green">● Có mặt</span>';
  if (s === "Đi trễ") return '<span class="badge b-amber">● Đi trễ</span>';
  if (s === "Vắng") return '<span class="badge b-red">● Vắng</span>';
  if (s === "Có phép") return '<span class="badge b-blue">● Có phép</span>';
  return '<span class="badge b-gray">○ Chưa điểm danh</span>';
}
function emptyHTML(title, sub) {
  return `<div class="empty"><div class="big">📭</div><b>${title}</b><div class="small">${sub || ""}</div></div>`;
}
function skeletonRows(n = 4) {
  return Array.from({ length: n }, () => `<tr><td colspan="8"><div class="skel">&nbsp;</div></td></tr>`).join("");
}
// --- Mock embedding (dùng khi chưa có model thật; KHÔNG lưu localStorage) ---
function mockEmbedding(seed = "") {
  let h = 0; for (const c of seed) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  const v = [];
  for (let i = 0; i < 128; i++) { h = (h * 1103515245 + 12345) >>> 0; v.push(+(((h % 2000) / 1000 - 1).toFixed(4))); }
  return v;
}
// --- CameraScanner (components/CameraScanner): xin quyền TRƯỚC, không tự bật ---
const CameraScanner = {
  stream: null,
  async start(videoEl) {
    this.stop();
    this.stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
    videoEl.srcObject = this.stream;
    await videoEl.play().catch(() => {});
    return this.stream;
  },
  stop() { this.stream?.getTracks().forEach(t => t.stop()); this.stream = null; }
};
