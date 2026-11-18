def make_city(client, headers, name="Cairo", country="Egypt"):
    res = client.post("/cities", json={"name": name, "country": country}, headers=headers)
    return res.json()["id"]


def test_register_and_login(client):
    res = client.post("/auth/register", json={"username": "habiba", "password": "secret123"})
    assert res.status_code == 201

    res = client.post("/auth/login", data={"username": "habiba", "password": "secret123"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "habiba", "password": "secret123"})
    res = client.post("/auth/login", data={"username": "habiba", "password": "wrong"})
    assert res.status_code == 401


def test_create_city_needs_token(client):
    res = client.post("/cities", json={"name": "Cairo", "country": "Egypt"})
    assert res.status_code == 401


def test_invalid_token_rejected(client):
    res = client.post(
        "/cities",
        json={"name": "Cairo", "country": "Egypt"},
        headers={"Authorization": "Bearer not.a.real.token"},
    )
    assert res.status_code == 401


def test_create_and_list_cities(client, auth_headers):
    make_city(client, auth_headers, "Cairo")
    make_city(client, auth_headers, "Alexandria")

    res = client.get("/cities")
    assert res.status_code == 200
    assert [c["name"] for c in res.json()] == ["Alexandria", "Cairo"]


def test_reading_for_missing_city_returns_404(client, auth_headers):
    res = client.post("/cities/999/readings", json={"temperature": 30}, headers=auth_headers)
    assert res.status_code == 404


def test_add_reading_and_filter_by_date(client, auth_headers):
    city_id = make_city(client, auth_headers)
    for temp, day in [(30, "2026-07-01"), (35, "2026-07-10"), (40, "2026-07-20")]:
        client.post(
            f"/cities/{city_id}/readings",
            json={"temperature": temp, "recorded_at": f"{day}T12:00:00"},
            headers=auth_headers,
        )

    res = client.get(
        f"/cities/{city_id}/readings",
        params={"from": "2026-07-05T00:00:00", "to": "2026-07-15T00:00:00"},
    )
    assert res.status_code == 200
    assert [r["temperature"] for r in res.json()] == [35]


def test_stats(client, auth_headers):
    city_id = make_city(client, auth_headers)
    for temp in (30, 35, 40):
        client.post(f"/cities/{city_id}/readings", json={"temperature": temp}, headers=auth_headers)

    res = client.get(f"/cities/{city_id}/stats")
    assert res.status_code == 200
    assert res.json()["min_temp"] == 30
    assert res.json()["max_temp"] == 40
    assert res.json()["avg_temp"] == 35


def test_unrealistic_temperature_rejected(client, auth_headers):
    city_id = make_city(client, auth_headers)
    res = client.post(
        f"/cities/{city_id}/readings", json={"temperature": 500}, headers=auth_headers
    )
    assert res.status_code == 422
