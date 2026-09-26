// Tiện ích dùng chung: dark mode, toast, gọi API
(function(){
  // Dark / Light mode
  const root = document.documentElement;
  root.dataset.theme = localStorage.getItem("theme") || "light";
  window.toggleTheme = () => {
    root.dataset.theme = root.dataset.theme === "light" ? "dark" : "light";
    localStorage.setItem("theme", root.dataset.theme);
  };
  // Sidebar mobile
  window.toggleSidebar = () => document.querySelector(".sidebar")?.classList.toggle("open");
  // Toast thông báo
  window.toast = (msg) => {
    const t = document.createElement("div");
    t.className = "toast"; t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3500);
  };
  // Gọi API JSON
  window.api = async (url, method = "GET", body = null) => {
    const r = await fetch(url, {
      method, headers: {"Content-Type": "application/json"},
      body: body ? JSON.stringify(body) : null
    });
    return r.json();
  };
  // Tạo embedding GIẢ LẬP 128 số (demo khi chưa cài thư viện thật)
  window.mockEmbedding = (seed = "") => {
    let h = 0; for (const c of seed) h = (h * 31 + c.charCodeAt(0)) >>> 0;
    const v = [];
    for (let i = 0; i < 128; i++) {
      h = (h * 1103515245 + 12345) >>> 0;
      v.push(+(((h % 2000) / 1000 - 1).toFixed(4)));
    }
    return v;
  };
})();
