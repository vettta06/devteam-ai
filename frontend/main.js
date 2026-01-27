const API_BASE = "http://localhost:8000";

function render(page) {
  const app = document.getElementById("app");
  switch (page) {
    case "login":
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
      document
        .getElementById("login-form")
        .addEventListener("submit", handleLogin);
      break;

    case "register":
      app.innerHTML = `
        <div class="auth-container">
          <h2 class="auth-title">Регистрация</h2>
          <form id="register-form" class="auth-form">
            <input type="email" placeholder="Email" required />
            <input type="password" placeholder="Пароль" required />
            <button type="submit">Зарегистрироваться</button>
          </form>
          <p class="auth-link"><a href="#/login">Уже есть аккаунт? Войти</a></p>
        </div>
      `;
      document
        .getElementById("register-form")
        .addEventListener("submit", handleRegister);
      break;

    case "tasks":
      app.innerHTML = `
        <div class="tasks-container">
          <div class="tasks-header">
            <h2>Мои задачи <button id="create-task-btn" class="create-task-btn">+</button></h2>
          </div>
          <div id="task-form" class="task-form" style="display: none;">
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
            <div id="task-form-error" class="error-message"></div>
          </div>
          <div id="tasks-list" class="tasks-list">
            <p>Загрузка задач...</p>
          </div>
          <button onclick="logout()" class="logout-btn">Выйти</button>
        </div>
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

// Обработка входа
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

// Обработка регистрации
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

// Загрузка задач
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
              <div class="task-card" data-id="${task.id}">
                <button class="task-delete-icon" data-id="${task.id}">×</button>
                <h3>${task.title}</h3>
                <p>${task.description || "Без описания"}</p>
                <p><strong>Статус:</strong> <span class="status status-${task.status}">${task.status}</span></p>
                <p><strong>Создано:</strong> ${task.created_at ? new Date(task.created_at).toLocaleString() : '—'}</p>
                <div class="task-actions">
                  <button class="task-action-btn edit" data-id="${task.id}">Редактировать</button>
                  <button class="task-action-btn ai-split" data-id="${task.id}" data-title="${task.title}" data-desc="${task.description || ""}">Разбить на подзадачи</button>
                </div>
                <div class="ai-result" id="ai-result-${task.id}" style="display: none;">
                  <div class="subtasks-list"></div>
                  <button class="toggle-log" data-target="log-${task.id}">Подробнее (лог рассуждений)</button>
                  <div class="reasoning-log" id="log-${task.id}" style="display: none;"></div>
                </div>
              </div>
            `,
          )
          .join("");
      }
    } else {
      tasksList.innerHTML = `<p class="error-message">${data.detail || "Неизвестная ошибка"}</p>`;
    }
  } catch (err) {
    tasksList.innerHTML = `<p class="error-message">Не удалось загрузить задачи</p>`;
  }

  // Добавляем обработчики после рендера
  setTimeout(() => {
    // Удаление через крестик
    document.querySelectorAll(".task-delete-icon").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const taskId = e.target.dataset.id;
        deleteTask(taskId);
      });
    });

    // Редактирование
    document.querySelectorAll(".task-action-btn.edit").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const taskId = e.target.dataset.id;
        editTask(taskId);
      });
    });

    // ИИ-разбиение
    document.querySelectorAll(".task-action-btn.ai-split").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        const taskId = e.target.dataset.id;
        const title = e.target.dataset.title;
        const desc = e.target.dataset.desc;
        const taskText = [title, desc].filter(Boolean).join(" ");
        await splitTask(taskId, taskText);
      });
    });

    // Лог рассуждений ("Подробнее")
    document.querySelectorAll(".toggle-log").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const targetId = e.target.dataset.target;
        const log = document.getElementById(targetId);
        const isVisible = log.style.display === "block";
        log.style.display = isVisible ? "none" : "block";
        e.target.textContent = isVisible
          ? "Подробнее (лог рассуждений)"
          : "Скрыть лог рассуждений";
      });
    });
  }, 0);
}

// Создание задачи
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

// Генерация подзадач через ИИ
async function splitTask(taskId, taskText) {
  const token = localStorage.getItem("access_token");
  if (!token) return;

  const button = document.querySelector(
    `.task-action-btn.ai-split[data-id="${taskId}"]`,
  );
  const resultContainer = document.getElementById(`ai-result-${taskId}`);
  const subtasksList = resultContainer.querySelector(".subtasks-list");
  const logContainer = resultContainer.querySelector(".reasoning-log");

  // Сохраняем исходный текст кнопки
  const originalText = button.textContent;
  button.disabled = true;
  button.textContent = "Генерация...";

  try {
    const res = await fetch(`${API_BASE}/ai/split-task`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ task: taskText }),
    });

    if (res.ok) {
      const data = await res.json();

      // Рендерим подзадачи
      subtasksList.innerHTML = data.subtasks
        .map(
          (sub) => `
            <div class="subtask-item">
              <strong>${sub.title}</strong>
              <p>${sub.description || ""}</p>
            </div>
          `,
        )
        .join("");

      // Рендерим лог рассуждений
      logContainer.innerHTML = data.reasoning_log
        .map((item) => `<p>${item}</p>`)
        .join("");

      // Показываем результат
      resultContainer.style.display = "block";
    } else {
      const errorData = await res.json().catch(() => ({}));
      alert(
        `Ошибка: ${errorData.detail || "Не удалось сгенерировать подзадачи"}`,
      );
    }
  } catch (err) {
    alert("Не удалось подключиться к серверу");
  } finally {
    button.disabled = false;
    button.textContent = originalText;
  }
}

// Удаление задачи
async function deleteTask(taskId) {
  const token = localStorage.getItem("access_token");
  if (!token) return;

  if (!confirm("Вы уверены, что хотите удалить эту задачу?")) return;

  try {
    const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (res.ok) {
      loadTasks();
    } else {
      alert("Ошибка при удалении задачи");
    }
  } catch (err) {
    alert("Не удалось подключиться к серверу");
  }
}

// Редактирование задачи (заглушка)
function editTask(taskId) {
  alert(
    `Редактирование задачи ID: ${taskId}\nВ будущем здесь будет форма редактирования.`,
  );
}

// Выход
function logout() {
  localStorage.removeItem("access_token");
  window.location.hash = "#/login";
}

window.addEventListener("hashchange", () => {
  const page = window.location.hash.slice(2) || "";
  render(page);
});

render(window.location.hash.slice(2) || "");
