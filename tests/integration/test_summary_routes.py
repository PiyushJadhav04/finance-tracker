from datetime import date

from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User


async def test_summary_requires_auth(client):
    response = await client.get("/summary", params={"year": 2026, "month": 7})
    assert response.status_code == 401


async def test_summary_empty_when_no_transactions(client, auth_headers):
    response = await client.get("/summary", params={"year": 2026, "month": 7}, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_spend"] == "0"
    assert body["by_category"] == []


async def test_summary_total_spend_sums_only_target_month(client, auth_headers):
    # inside July 2026
    await client.post(
        "/transactions", json={"amount": "10.00", "date": "2026-07-01"}, headers=auth_headers
    )
    await client.post(
        "/transactions", json={"amount": "20.00", "date": "2026-07-31"}, headers=auth_headers
    )
    # just outside the month on either side
    await client.post(
        "/transactions", json={"amount": "100.00", "date": "2026-06-30"}, headers=auth_headers
    )
    await client.post(
        "/transactions", json={"amount": "200.00", "date": "2026-08-01"}, headers=auth_headers
    )

    response = await client.get(
        "/summary", params={"year": 2026, "month": 7}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["total_spend"] == "30.00"


async def test_summary_groups_spend_by_category_with_uncategorized_bucket(
    client, auth_headers, db_session
):
    groceries = Category(name="Groceries", user_id=None)
    db_session.add(groceries)
    await db_session.commit()
    await db_session.refresh(groceries)

    await client.post(
        "/transactions",
        json={"amount": "15.00", "date": "2026-07-05", "category_id": groceries.id},
        headers=auth_headers,
    )
    await client.post(
        "/transactions",
        json={"amount": "5.00", "date": "2026-07-06", "category_id": groceries.id},
        headers=auth_headers,
    )
    await client.post(
        "/transactions", json={"amount": "7.00", "date": "2026-07-07"}, headers=auth_headers
    )

    response = await client.get(
        "/summary", params={"year": 2026, "month": 7}, headers=auth_headers
    )
    assert response.status_code == 200
    by_category = {item["category_name"]: item["total"] for item in response.json()["by_category"]}
    assert by_category == {"Groceries": "20.00", "Uncategorized": "7.00"}


async def test_summary_scoped_to_requesting_user(client, auth_headers, db_session):
    await client.post(
        "/transactions", json={"amount": "10.00", "date": "2026-07-01"}, headers=auth_headers
    )

    other_user = User(email="bob@example.com", password_hash="x")
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)
    db_session.add(
        Transaction(user_id=other_user.id, amount="999.00", date=date(2026, 7, 2))
    )
    await db_session.commit()

    response = await client.get(
        "/summary", params={"year": 2026, "month": 7}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["total_spend"] == "10.00"


async def test_summary_defaults_to_current_month_when_no_params_given(client, auth_headers):
    today = date.today()
    await client.post(
        "/transactions",
        json={"amount": "50.00", "date": today.isoformat()},
        headers=auth_headers,
    )

    response = await client.get("/summary", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["year"] == today.year
    assert body["month"] == today.month
    assert body["total_spend"] == "50.00"
