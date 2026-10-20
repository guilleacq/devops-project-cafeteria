"""
Pruebas de inicio de sesión y control de roles.
"""


def test_login_returns_a_token_and_the_user(client):
    response = client.post("/api/auth/login", json={"email": "alumno1@cafeteria.test", "password": "alumno123"})

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["user"]["role"] == "student"
    assert "password_hash" not in body["user"]


def test_login_with_wrong_password_is_rejected(client):
    response = client.post("/api/auth/login", json={"email": "alumno1@cafeteria.test", "password": "otra"})

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"


def test_endpoints_require_a_session(client):
    response = client.get("/api/products")

    assert response.status_code == 401


def test_me_returns_the_logged_in_user(client, cafeteria_headers):
    response = client.get("/api/auth/me", headers=cafeteria_headers)

    assert response.status_code == 200
    assert response.json()["role"] == "cafeteria"


def test_students_cannot_use_cafeteria_endpoints(client, student_headers):
    response = client.get("/api/cafeteria/next-recess", headers=student_headers)

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"
