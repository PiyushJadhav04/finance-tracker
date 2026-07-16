from app.models.category import Category
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
