def test_login_success(client, test_user):
    """Проверка регистрации."""
    client.post("/users/", json=test_user)
    response = client.post(
        "/auth/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_login_invalid_password(client, test_user):
    """Вход с неверным паролем."""
    client.post("/users/", json=test_user)
    response = client.post(
        "/auth/login", data={"username": test_user["email"], "password": "wrong"}
    )
    assert response.status_code == 401
