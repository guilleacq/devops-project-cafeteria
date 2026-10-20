"""
Pruebas de pedidos, sobre todo la regla de la hora límite.

El reloj arranca a las 09:00. El primer recreo es a las 09:30 y X = 15,
así que los pedidos para ese recreo cierran a las 09:15.
"""

from tests.conftest import CAFE_ID, FIRST_RECESS_ID, MEDIALUNA_ID, SECOND_RECESS_ID, montevideo_time, place_order


# ---------------------------------------------------------------------------
# Hora límite
# ---------------------------------------------------------------------------

def test_order_before_closing_time_is_accepted(client, student_headers, clock):
    clock.move_to(montevideo_time(9, 14))

    response = place_order(client, student_headers)

    assert response.status_code == 201
    order = response.json()
    assert order["status"] == "pending"
    assert order["recess_name"] == "Primer recreo"
    assert order["total"] == 2 * 35 + 60


def test_order_after_closing_time_is_rejected_with_a_clear_message(client, student_headers, clock):
    clock.move_to(montevideo_time(9, 16))

    response = place_order(client, student_headers)

    assert response.status_code == 422
    error = response.json()
    assert error["code"] == "ORDERING_CLOSED"
    assert "09:15" in error["detail"]
    assert "09:30" in error["detail"]


def test_order_exactly_at_closing_time_is_rejected(client, student_headers, clock):
    clock.move_to(montevideo_time(9, 15))

    response = place_order(client, student_headers)

    assert response.status_code == 422


def test_after_one_recess_closes_you_can_still_order_for_the_next(client, student_headers, clock):
    clock.move_to(montevideo_time(9, 20))

    response = place_order(client, student_headers, recess_id=SECOND_RECESS_ID)

    assert response.status_code == 201


def test_changing_x_applies_immediately_without_restarting(client, student_headers, cafeteria_headers, clock):
    clock.move_to(montevideo_time(9, 0))

    response = client.put("/api/configuration/order-cutoff", json={"order_cutoff_minutes": 45}, headers=cafeteria_headers)
    assert response.status_code == 200

    # Con X = 45 los pedidos para las 09:30 cerraron a las 08:45.
    response = place_order(client, student_headers)
    assert response.status_code == 422
    assert "08:45" in response.json()["detail"]


def test_todays_recesses_tell_if_they_accept_orders(client, student_headers, clock):
    clock.move_to(montevideo_time(9, 20))

    response = client.get("/api/recesses/today", headers=student_headers)

    assert response.status_code == 200
    recesses = {recess["id"]: recess for recess in response.json()}
    assert recesses[FIRST_RECESS_ID]["is_accepting_orders"] is False
    assert recesses[SECOND_RECESS_ID]["is_accepting_orders"] is True
    assert recesses[FIRST_RECESS_ID]["ordering_closes_at"] == "2026-10-20T09:15:00-03:00"


# ---------------------------------------------------------------------------
# Validaciones
# ---------------------------------------------------------------------------

def test_repeated_products_are_merged_into_one_line(client, student_headers):
    items = [{"product_id": MEDIALUNA_ID, "quantity": 1}, {"product_id": MEDIALUNA_ID, "quantity": 2}]

    response = place_order(client, student_headers, items=items)

    assert response.status_code == 201
    assert response.json()["items"] == [
        {"product_id": MEDIALUNA_ID, "product_name": "Medialuna", "quantity": 3, "unit_price": 35, "subtotal": 105}
    ]


def test_sold_out_products_cannot_be_ordered(client, student_headers, cafeteria_headers):
    client.patch(f"/api/products/{CAFE_ID}", json={"is_sold_out": True}, headers=cafeteria_headers)

    response = place_order(client, student_headers)

    assert response.status_code == 409
    assert response.json()["code"] == "PRODUCT_SOLD_OUT"


def test_unknown_product_is_rejected(client, student_headers):
    response = place_order(client, student_headers, items=[{"product_id": 999, "quantity": 1}])

    assert response.status_code == 404


def test_order_price_does_not_change_if_the_product_price_changes(client, student_headers, cafeteria_headers):
    order_id = place_order(client, student_headers).json()["id"]

    client.patch(f"/api/products/{MEDIALUNA_ID}", json={"price": 999}, headers=cafeteria_headers)

    order = client.get(f"/api/orders/{order_id}", headers=student_headers).json()
    assert order["total"] == 2 * 35 + 60


# ---------------------------------------------------------------------------
# Permisos
# ---------------------------------------------------------------------------

def test_cafeteria_cannot_place_orders(client, cafeteria_headers):
    response = place_order(client, cafeteria_headers)

    assert response.status_code == 403


def test_students_only_see_their_own_orders(client, student_headers, other_student_headers):
    order_id = place_order(client, student_headers).json()["id"]

    my_orders = client.get("/api/orders/mine", headers=student_headers).json()
    others_orders = client.get("/api/orders/mine", headers=other_student_headers).json()

    assert [order["id"] for order in my_orders] == [order_id]
    assert others_orders == []

    response = client.get(f"/api/orders/{order_id}", headers=other_student_headers)
    assert response.status_code == 403
