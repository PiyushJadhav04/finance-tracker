from datetime import date

from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User


async def test_create_transaction(client, auth_headers):
    response = await client.post(
        "/transactions",
        json={"amount": "42.50", "description": "Groceries", "date": "2026-07-01"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["amount"] == "42.50"
    assert body["description"] == "Groceries"
    assert body["date"] == "2026-07-01"
    assert body["category_id"] is None
    assert "id" in body


async def test_create_transaction_requires_auth(client):
    response = await client.post(
        "/transactions", json={"amount": "10.00", "date": "2026-07-01"}
    )
    assert response.status_code == 401


async def test_create_transaction_rejects_unknown_category(client, auth_headers):
    response = await client.post(
        "/transactions",
        json={"amount": "10.00", "date": "2026-07-01", "category_id": 999},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_create_transaction_accepts_global_category(client, auth_headers, db_session):
    global_category = Category(name="Groceries", user_id=None)
    db_session.add(global_category)
    await db_session.commit()
    await db_session.refresh(global_category)

    response = await client.post(
        "/transactions",
        json={"amount": "10.00", "date": "2026-07-01", "category_id": global_category.id},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["category_id"] == global_category.id


async def test_create_transaction_rejects_other_users_category(client, auth_headers, db_session):
    other_user = User(email="bob@example.com", password_hash="x")
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    private_category = Category(name="Bob's Secret", user_id=other_user.id)
    db_session.add(private_category)
    await db_session.commit()
    await db_session.refresh(private_category)

    response = await client.post(
        "/transactions",
        json={"amount": "10.00", "date": "2026-07-01", "category_id": private_category.id},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_list_transactions_requires_auth(client):
    response = await client.get("/transactions")
    assert response.status_code == 401


async def test_list_transactions_empty_when_none(client, auth_headers):
    response = await client.get("/transactions", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


async def test_list_transactions_returns_only_own_transactions(client, auth_headers, db_session):
    await client.post(
        "/transactions",
        json={"amount": "10.00", "date": "2026-07-01"},
        headers=auth_headers,
    )
    await client.post(
        "/transactions",
        json={"amount": "20.00", "date": "2026-07-02"},
        headers=auth_headers,
    )

    other_user = User(email="bob@example.com", password_hash="x")
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)
    db_session.add(
        Transaction(user_id=other_user.id, amount="999.00", date=date(2026, 7, 3))
    )
    await db_session.commit()

    response = await client.get("/transactions", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert all(item["amount"] in ("10.00", "20.00") for item in body)


async def test_list_transactions_orders_by_date_descending(client, auth_headers):
    await client.post(
        "/transactions", json={"amount": "1.00", "date": "2026-07-01"}, headers=auth_headers
    )
    await client.post(
        "/transactions", json={"amount": "2.00", "date": "2026-07-03"}, headers=auth_headers
    )
    await client.post(
        "/transactions", json={"amount": "3.00", "date": "2026-07-02"}, headers=auth_headers
    )

    response = await client.get("/transactions", headers=auth_headers)
    dates = [item["date"] for item in response.json()]
    assert dates == ["2026-07-03", "2026-07-02", "2026-07-01"]


async def test_list_transactions_respects_limit_and_offset(client, auth_headers):
    for i in range(5):
        await client.post(
            "/transactions",
            json={"amount": "1.00", "date": f"2026-07-{i + 1:02d}"},
            headers=auth_headers,
        )

    first_page = await client.get(
        "/transactions", params={"limit": 2, "offset": 0}, headers=auth_headers
    )
    second_page = await client.get(
        "/transactions", params={"limit": 2, "offset": 2}, headers=auth_headers
    )
    assert [item["date"] for item in first_page.json()] == ["2026-07-05", "2026-07-04"]
    assert [item["date"] for item in second_page.json()] == ["2026-07-03", "2026-07-02"]


async def test_get_transaction_returns_own_transaction(client, auth_headers):
    created = await client.post(
        "/transactions",
        json={"amount": "42.50", "date": "2026-07-01"},
        headers=auth_headers,
    )
    transaction_id = created.json()["id"]

    response = await client.get(f"/transactions/{transaction_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == transaction_id


async def test_get_transaction_requires_auth(client, auth_headers):
    created = await client.post(
        "/transactions",
        json={"amount": "42.50", "date": "2026-07-01"},
        headers=auth_headers,
    )
    transaction_id = created.json()["id"]

    response = await client.get(f"/transactions/{transaction_id}")
    assert response.status_code == 401


async def test_get_transaction_404_when_not_found(client, auth_headers):
    response = await client.get("/transactions/999999", headers=auth_headers)
    assert response.status_code == 404


async def test_get_transaction_404_when_belongs_to_other_user(client, auth_headers, db_session):
    other_user = User(email="bob@example.com", password_hash="x")
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    other_transaction = Transaction(user_id=other_user.id, amount="999.00", date=date(2026, 7, 3))
    db_session.add(other_transaction)
    await db_session.commit()
    await db_session.refresh(other_transaction)

    response = await client.get(
        f"/transactions/{other_transaction.id}", headers=auth_headers
    )
    assert response.status_code == 404


async def test_update_transaction_updates_only_provided_fields(client, auth_headers):
    created = await client.post(
        "/transactions",
        json={"amount": "10.00", "description": "Original", "date": "2026-07-01"},
        headers=auth_headers,
    )
    transaction_id = created.json()["id"]

    response = await client.put(
        f"/transactions/{transaction_id}", json={"amount": "20.00"}, headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["amount"] == "20.00"
    assert body["description"] == "Original"
    assert body["date"] == "2026-07-01"


async def test_update_transaction_requires_auth(client, auth_headers):
    created = await client.post(
        "/transactions", json={"amount": "10.00", "date": "2026-07-01"}, headers=auth_headers
    )
    transaction_id = created.json()["id"]

    response = await client.put(f"/transactions/{transaction_id}", json={"amount": "20.00"})
    assert response.status_code == 401


async def test_update_transaction_404_when_not_found(client, auth_headers):
    response = await client.put(
        "/transactions/999999", json={"amount": "20.00"}, headers=auth_headers
    )
    assert response.status_code == 404


async def test_update_transaction_404_when_belongs_to_other_user(
    client, auth_headers, db_session
):
    other_user = User(email="bob@example.com", password_hash="x")
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    other_transaction = Transaction(user_id=other_user.id, amount="999.00", date=date(2026, 7, 3))
    db_session.add(other_transaction)
    await db_session.commit()
    await db_session.refresh(other_transaction)

    response = await client.put(
        f"/transactions/{other_transaction.id}",
        json={"amount": "1.00"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_update_transaction_rejects_unknown_category(client, auth_headers):
    created = await client.post(
        "/transactions", json={"amount": "10.00", "date": "2026-07-01"}, headers=auth_headers
    )
    transaction_id = created.json()["id"]

    response = await client.put(
        f"/transactions/{transaction_id}",
        json={"category_id": 999999},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_update_transaction_rejects_other_users_category(client, auth_headers, db_session):
    created = await client.post(
        "/transactions", json={"amount": "10.00", "date": "2026-07-01"}, headers=auth_headers
    )
    transaction_id = created.json()["id"]

    other_user = User(email="bob@example.com", password_hash="x")
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    private_category = Category(name="Bob's Secret", user_id=other_user.id)
    db_session.add(private_category)
    await db_session.commit()
    await db_session.refresh(private_category)

    response = await client.put(
        f"/transactions/{transaction_id}",
        json={"category_id": private_category.id},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_update_transaction_rejects_explicit_null_amount(client, auth_headers):
    created = await client.post(
        "/transactions", json={"amount": "10.00", "date": "2026-07-01"}, headers=auth_headers
    )
    transaction_id = created.json()["id"]

    response = await client.put(
        f"/transactions/{transaction_id}", json={"amount": None}, headers=auth_headers
    )
    assert response.status_code == 422
