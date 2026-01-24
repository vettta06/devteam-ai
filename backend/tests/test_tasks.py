def test_create_task(client, auth_token):
    """Создание задачи."""
    response = client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "Test Description"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["user_id"] is not None


def test_get_tasks(client, auth_token):
    """Получение задач."""
    response = client.get("/tasks/", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_task(client, auth_token):
    create_response = client.post(
        "/tasks/",
        json={"title": "Original Title"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    task_id = create_response.json()["id"]
    update_response = client.put(
        f"/tasks/{task_id}",
        json={"status": "in_progress"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "in_progress"


def test_delete_task(client, auth_token):
    create_response = client.post(
        "/tasks/",
        json={"title": "To Delete"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    task_id = create_response.json()["id"]
    delete_response = client.delete(
        f"/tasks/{task_id}", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Task deleted successfully"
