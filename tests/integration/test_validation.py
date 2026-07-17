async def test_create_transaction_missing_amount_returns_consistent_shape(client, auth_headers):
    response = await client.post(
        "/transactions", json={"date": "2026-07-01"}, headers=auth_headers
    )
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)
    assert "amount" in response.json()["detail"]


async def test_create_transaction_missing_date_returns_consistent_shape(client, auth_headers):
    response = await client.post(
        "/transactions", json={"amount": "10.00"}, headers=auth_headers
    )
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)
    assert "date" in response.json()["detail"]


async def test_create_transaction_rejects_non_numeric_amount(client, auth_headers):
    response = await client.post(
        "/transactions",
        json={"amount": "not-a-number", "date": "2026-07-01"},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)


async def test_create_transaction_rejects_malformed_date(client, auth_headers):
    response = await client.post(
        "/transactions",
        json={"amount": "10.00", "date": "not-a-date"},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)


async def test_signup_missing_email_returns_consistent_shape(client):
    response = await client.post("/auth/signup", json={"password": "supersecret123"})
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)


async def test_signup_invalid_email_format_rejected(client):
    response = await client.post(
        "/auth/signup", json={"email": "not-an-email", "password": "supersecret123"}
    )
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)


async def test_application_errors_and_validation_errors_share_error_shape(client, auth_headers):
    # a 404 raised by our own code and a 422 from Pydantic validation
    # should both come back as {"detail": "<string>"} — not two shapes
    not_found = await client.get("/transactions/999999", headers=auth_headers)
    validation_error = await client.post(
        "/transactions", json={"date": "2026-07-01"}, headers=auth_headers
    )

    assert not_found.status_code == 404
    assert validation_error.status_code == 422
    assert isinstance(not_found.json()["detail"], str)
    assert isinstance(validation_error.json()["detail"], str)
    assert set(not_found.json().keys()) == {"detail"}
    assert set(validation_error.json().keys()) == {"detail"}
