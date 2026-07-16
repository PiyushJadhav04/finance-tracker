async def test_signup_creates_user(client):
    response = await client.post(
        "/auth/signup", json={"email": "alice@example.com", "password": "supersecret123"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert "id" in body
    assert "password" not in body
    assert "password_hash" not in body


async def test_signup_rejects_duplicate_email(client):
    await client.post(
        "/auth/signup", json={"email": "alice@example.com", "password": "supersecret123"}
    )
    response = await client.post(
        "/auth/signup", json={"email": "alice@example.com", "password": "anotherpassword"}
    )
    assert response.status_code == 400


async def test_signup_rejects_short_password(client):
    response = await client.post(
        "/auth/signup", json={"email": "alice@example.com", "password": "short"}
    )
    assert response.status_code == 422


async def test_login_succeeds_with_correct_credentials(client):
    await client.post(
        "/auth/signup", json={"email": "alice@example.com", "password": "supersecret123"}
    )
    response = await client.post(
        "/auth/login", data={"username": "alice@example.com", "password": "supersecret123"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


async def test_login_rejects_wrong_password(client):
    await client.post(
        "/auth/signup", json={"email": "alice@example.com", "password": "supersecret123"}
    )
    response = await client.post(
        "/auth/login", data={"username": "alice@example.com", "password": "wrong-password"}
    )
    assert response.status_code == 401


async def test_login_rejects_unknown_email(client):
    response = await client.post(
        "/auth/login", data={"username": "nobody@example.com", "password": "supersecret123"}
    )
    assert response.status_code == 401


async def test_me_returns_current_user_with_valid_token(client):
    await client.post(
        "/auth/signup", json={"email": "alice@example.com", "password": "supersecret123"}
    )
    login_response = await client.post(
        "/auth/login", data={"username": "alice@example.com", "password": "supersecret123"}
    )
    token = login_response.json()["access_token"]

    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


async def test_me_rejects_missing_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


async def test_me_rejects_invalid_token(client):
    response = await client.get("/auth/me", headers={"Authorization": "Bearer garbage-token"})
    assert response.status_code == 401
