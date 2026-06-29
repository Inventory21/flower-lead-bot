// ====== Конфигурация ======
const API_URL = "https://flora-admin.duckdns.org/api"; // локально: http://localhost:8001
const ADMIN_TOKEN = "admin_secret_token_change_me";    // = ADMIN_TOKEN из .env

const headers = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${ADMIN_TOKEN}`,
};

// Инициализация Telegram Mini App (если открыто внутри Telegram)
if (window.Telegram && window.Telegram.WebApp) {
    Telegram.WebApp.ready();
    Telegram.WebApp.expand();
}

// ====== Ассортимент ======
async function loadProducts() {
    const list = document.getElementById("products-list");
    try {
        const res = await fetch(`${API_URL}/products`, { headers });
        const products = await res.json();
        if (!products.length) {
            list.innerHTML = `<div class="empty">Ассортимент пуст</div>`;
            return;
        }
        list.innerHTML = products.map(p => `
            <div class="card">
                <div class="card-info">
                    <b>${escapeHtml(p.name)}</b>
                    ${p.price ? `— ${p.price} ₽` : ""}
                    <div class="card-meta">
                        ${p.category ? `Категория: ${escapeHtml(p.category)}` : ""}
                        ${p.description ? `<br>${escapeHtml(p.description)}` : ""}
                    </div>
                </div>
                <button class="btn-del" onclick="deleteProduct(${p.id})">Удалить</button>
            </div>
        `).join("");
    } catch (e) {
        list.innerHTML = `<div class="empty">Ошибка загрузки</div>`;
    }
}

async function deleteProduct(id) {
    if (!confirm("Удалить позицию?")) return;
    await fetch(`${API_URL}/products/${id}`, { method: "DELETE", headers });
    loadProducts();
}

document.getElementById("product-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const body = {
        name: document.getElementById("p-name").value,
        category: document.getElementById("p-category").value || null,
        price: parseFloat(document.getElementById("p-price").value) || null,
        description: document.getElementById("p-desc").value || null,
    };
    await fetch(`${API_URL}/products`, {
        method: "POST",
        headers,
        body: JSON.stringify(body),
    });
    e.target.reset();
    loadProducts();
});

// ====== Лиды ======
async function loadLeads() {
    const list = document.getElementById("leads-list");
    try {
        const res = await fetch(`${API_URL}/leads`, { headers });
        const leads = await res.json();
        if (!leads.length) {
            list.innerHTML = `<div class="empty">Лидов пока нет</div>`;
            return;
        }
        list.innerHTML = leads.map(l => `
            <div class="card">
                <div class="card-info">
                    <b>${escapeHtml(l.name || "Без имени")}</b>
                    ${l.phone ? `— 📞 ${escapeHtml(l.phone)}` : ""}
                    <div class="card-meta">
                        ${l.username ? `Telegram: <a href="https://t.me/${escapeHtml(l.username)}" target="_blank">@${escapeHtml(l.username)}</a>` : `ID: ${l.telegram_id}`}
                        ${l.notes ? `<br>Заметка: ${escapeHtml(l.notes)}` : ""}
                        <br><span style="color:#bbb">${l.created_at}</span>
                    </div>
                </div>
            </div>
        `).join("");
    } catch (e) {
        list.innerHTML = `<div class="empty">Ошибка загрузки</div>`;
    }
}

// ====== Утилита защиты от XSS ======
function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

// ====== Автообновление ======
loadProducts();
loadLeads();
setInterval(loadLeads, 15000); // обновляем лиды каждые 15 сек