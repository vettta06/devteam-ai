const API_BASE = "http://localhost:8000";

function render(page) {
  const app = document.getElementById("app");
  switch (page) {
    case 'login':
        app.innerHTML = `
            <div class="auth-container">
            <h2 class="auth-title">Вход</h2>
            <form id="login-form" class="auth-form">
                <input type="email" placeholder="Email" required />
                <input type="password" placeholder="Пароль" required />
                <button type="submit">Войти</button>
            </form>
            <p class="auth-link"><a href="#/register">Нет аккаунта? Зарегистрироваться</a></p>
            </div>
        `;
        document.getElementById('login-form').addEventListener('submit', handleLogin);
        break;

    case "register":
      app.innerHTML = `
        <h2>Регистрация</h2>
        <form id="register-form">
          <input type="email" placeholder="Email" required /><br><br>
          <input type="password" placeholder="Пароль" required /><br><br>
          <button type="submit">Зарегистрироваться</button>
        </form>
        <p><a href="#/login">Уже есть аккаунт? Войти</a></p>
        <div id="register-error" style="color: red; margin-top: 10px;"></div>
      `;
      document
        .getElementById("register-form")
        .addEventListener("submit", handleRegister);
      break;

    case "tasks":
      app.innerHTML = `
            <h2>Мои задачи <button id="create-task-btn" class="create-task-btn">+</button></h2>
            <div id="task-form" style="display: none; margin: 20px 0;">
            <h3>Новая задача</h3>
            <form id="new-task-form">
                <input type="text" placeholder="Название задачи" required /><br><br>
                <textarea placeholder="Описание (опционально)"></textarea><br><br>
                <select required>
                <option value="">Выберите статус</option>
                <option value="pending">В ожидании</option>
                <option value="in_progress">В работе</option>
                <option value="completed">Завершена</option>
                </select><br><br>
                <button type="submit">Сохранить</button>
                <button type="button" id="cancel-create">Отмена</button>
            </form>
            <div id="task-form-error" style="color: red; margin-top: 10px;"></div>
            </div>
            <div id="tasks-list">
            <p>Загрузка задач...</p>
            </div>
            <button onclick="logout()">Выйти</button>
        `;
      loadTasks();

      document
        .getElementById("create-task-btn")
        .addEventListener("click", () => {
          document.getElementById("task-form").style.display = "block";
        });

      document.getElementById("cancel-create").addEventListener("click", () => {
        document.getElementById("task-form").style.display = "none";
        document.getElementById("task-form-error").textContent = "";
      });

      document
        .getElementById("new-task-form")
        .addEventListener("submit", handleCreateTask);
      break;

    default:
      const token = localStorage.getItem("access_token");
      if (token) {
        window.location.hash = "#/tasks";
      } else {
        window.location.hash = "#/login";
      }
      return;
  }
}

async function handleLogin(e) {
  e.preventDefault();
  const form = e.target;
  const email = form.querySelector('input[type="email"]').value;
  const password = form.querySelector('input[type="password"]').value;
  const errorDiv = document.getElementById("login-error");

  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (res.ok) {
      localStorage.setItem("access_token", data.access_token);
      window.location.hash = "#/tasks";
    } else {
      errorDiv.textContent = data.detail || "Ошибка входа";
    }
  } catch (err) {
    errorDiv.textContent = "Не удалось подключиться к серверу";
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const form = e.target;
  const email = form.querySelector('input[type="email"]').value;
  const password = form.querySelector('input[type="password"]').value;
  const errorDiv = document.getElementById("register-error");

  try {
    const regRes = await fetch(`${API_BASE}/users/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const regData = await regRes.json();

    if (regRes.ok) {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const loginRes = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        body: formData,
      });
      const loginData = await loginRes.json();

      if (loginRes.ok) {
        localStorage.setItem("access_token", loginData.access_token);
        window.location.hash = "#/tasks";
      } else {
        errorDiv.textContent =
          loginData.detail || "Регистрация прошла, но вход не удался";
      }
    } else {
      errorDiv.textContent = regData.detail || "Ошибка регистрации";
    }
  } catch (err) {
    errorDiv.textContent = "Не удалось подключиться к серверу";
  }
}

async function loadTasks() {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.hash = "#/login";
    return;
  }

  const tasksList = document.getElementById("tasks-list");

  try {
    const res = await fetch(`${API_BASE}/tasks/`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (res.status === 401) {
      localStorage.removeItem("access_token");
      window.location.hash = "#/login";
      return;
    }

    const data = await res.json();

    if (res.ok) {
      if (data.length === 0) {
        tasksList.innerHTML = "<p>У вас пока нет задач.</p>";
      } else {
        tasksList.innerHTML = data
          .map(
            (task) => `
          <div style="border: 1px solid #ccc; padding: 10px; margin: 10px 0;">
            <h3>${task.title}</h3>
            <p>${task.description || "Без описания"}</p>
            <p><strong>Статус:</strong> ${task.status}</p>
            <p><strong>Создано:</strong> ${new Date(task.created_at).toLocaleString()}</p>
          </div>
        `,
          )
          .join("");
      }
    } else {
      tasksList.innerHTML = `<p style="color: red;">Ошибка: ${data.detail || "Неизвестная ошибка"}</p>`;
    }
  } catch (err) {
    tasksList.innerHTML = `<p style="color: red;">Не удалось загрузить задачи</p>`;
  }
}

async function handleCreateTask(e) {
  e.preventDefault();
  const form = e.target;
  const title = form.querySelector('input[type="text"]').value;
  const description = form.querySelector("textarea").value;
  const status = form.querySelector("select").value;
  const errorDiv = document.getElementById("task-form-error");

  if (!status) {
    errorDiv.textContent = "Выберите статус задачи";
    return;
  }

  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.hash = "#/login";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/tasks/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ title, description, status }),
    });

    const data = await res.json();

    if (res.ok) {
      document.getElementById("task-form").style.display = "none";
      loadTasks();
    } else {
      errorDiv.textContent = data.detail || "Ошибка при создании задачи";
    }
  } catch (err) {
    errorDiv.textContent = "Не удалось подключиться к серверу";
  }
}

function logout() {
  localStorage.removeItem("access_token");
  window.location.hash = "#/login";
}

window.addEventListener("hashchange", () => {
  const page = window.location.hash.slice(2) || "";
  render(page);
});

render(window.location.hash.slice(2) || "");
