// URL base de tu API - ejecutandose en local con uvicorn
const API_URL = "https://user-auth-api-ro55.onrender.com";

// Referencias a los elementos del HTML que vamos a usar
const authView = document.getElementById("auth-view");
const dashboardView = document.getElementById("dashboard-view");
const authMessage = document.getElementById("auth-message");
const welcomeUsername = document.getElementById("welcome-username");
const itemsList = document.getElementById("items-list");

// Al cargar la pagina, comprobamos si ya habia un token guardado
// (por ejemplo, si el usuario recargo la pagina sin cerrar sesion)
window.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    if (token) {
        mostrarDashboard();
    }
});


// --- REGISTRO ---
document.getElementById("register-btn").addEventListener("click", async () => {
    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            authMessage.textContent = "Cuenta creada. Ahora inicia sesión.";
            authMessage.style.color = "#16a34a";
        } else {
            const error = await response.json();
            authMessage.textContent = error.detail;
            authMessage.style.color = "#dc2626";
        }
    } catch (err) {
        authMessage.textContent = "No se pudo conectar con la API.";
    }
});


// --- LOGIN ---
document.getElementById("login-btn").addEventListener("click", async () => {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    // El login espera form-data, no JSON (recuerdalo de las pruebas en Swagger)
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            // Guardamos el token en localStorage para no perderlo si recargas la pagina
            localStorage.setItem("token", data.access_token);
            mostrarDashboard();
        } else {
            authMessage.textContent = "Usuario o contraseña incorrectos.";
            authMessage.style.color = "#dc2626";
        }
    } catch (err) {
        authMessage.textContent = "No se pudo conectar con la API.";
    }
});


// --- LOGOUT ---
document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.removeItem("token");
    dashboardView.style.display = "none";
    authView.style.display = "block";
});


// --- Mostrar el dashboard y cargar los datos del usuario ---
async function mostrarDashboard() {
    const token = localStorage.getItem("token");

    const response = await fetch(`${API_URL}/me`, {
        headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
        // El token no es valido o caduco - volvemos a la vista de login
        localStorage.removeItem("token");
        return;
    }

    const user = await response.json();
    welcomeUsername.textContent = user.username;

    authView.style.display = "none";
    dashboardView.style.display = "block";

    cargarItems();
}


// --- Cargar los items del usuario autenticado ---
async function cargarItems() {
    const token = localStorage.getItem("token");

    const response = await fetch(`${API_URL}/items`, {
        headers: { Authorization: `Bearer ${token}` },
    });

    const items = await response.json();

    itemsList.innerHTML = "";
    items.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item.title;
        itemsList.appendChild(li);
    });
}


// --- Añadir un item nuevo ---
document.getElementById("add-item-btn").addEventListener("click", async () => {
    const token = localStorage.getItem("token");
    const title = document.getElementById("new-item-title").value;

    if (!title) return;

    await fetch(`${API_URL}/items`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title }),
    });

    document.getElementById("new-item-title").value = "";
    cargarItems();
});