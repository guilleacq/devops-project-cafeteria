"""
Pruebas de las vistas de la cafetería y de los cambios de estado.
"""

from tests.conftest import FIRST_RECESS_ID, SECOND_RECESS_ID, montevideo_time, place_order


def test_next_recess_board_shows_pending_orders_and_what_to_prepare(
    client, student_headers, other_student_headers, cafeteria_headers
):
    place_order(client, student_headers)
    place_order(client, other_student_headers)
    place_order(client, other_student_headers, recess_id=SECOND_RECESS_ID)

    board = client.get("/api/cafeteria/next-recess", headers=cafeteria_headers).json()

    assert board["recess"]["id"] == FIRST_RECESS_ID
    assert len(board["orders"]) == 2
    assert {order["student_name"] for order in board["orders"]} == {"Lucía Fernández", "Martín Rodríguez"}
    assert board["products_to_prepare"] == [
        {"product_name": "Medialuna", "quantity": 4},
        {"product_name": "Café", "quantity": 2},
    ]


def test_board_keeps_showing_the_recess_while_it_is_running(client, student_headers, cafeteria_headers, clock):
    place_order(client, student_headers)
    clock.move_to(montevideo_time(9, 40))

    board = client.get("/api/cafeteria/next-recess", headers=cafeteria_headers).json()

    assert board["recess"]["id"] == FIRST_RECESS_ID
    assert len(board["orders"]) == 1


def test_board_says_when_there_are_no_more_recesses(client, cafeteria_headers, clock):
    clock.move_to(montevideo_time(18, 0))

    board = client.get("/api/cafeteria/next-recess", headers=cafeteria_headers).json()

    assert board["recess"] is None
    assert board["message"] == "No quedan recreos por hoy."


def test_order_goes_from_pending_to_ready_to_delivered(client, student_headers, cafeteria_headers):
    order_id = place_order(client, student_headers).json()["id"]

    ready = client.patch(f"/api/orders/{order_id}/status", json={"status": "ready"}, headers=cafeteria_headers)
    delivered = client.patch(f"/api/orders/{order_id}/status", json={"status": "delivered"}, headers=cafeteria_headers)

    assert ready.json()["status"] == "ready"
    assert delivered.json()["status"] == "delivered"

    student_view = client.get(f"/api/orders/{order_id}", headers=student_headers).json()
    assert student_view["status"] == "delivered"


def test_order_status_cannot_go_back(client, student_headers, cafeteria_headers):
    order_id = place_order(client, student_headers).json()["id"]
    client.patch(f"/api/orders/{order_id}/status", json={"status": "delivered"}, headers=cafeteria_headers)

    response = client.patch(f"/api/orders/{order_id}/status", json={"status": "pending"}, headers=cafeteria_headers)

    assert response.status_code == 409
    assert response.json()["code"] == "INVALID_STATUS_CHANGE"


def test_delivered_orders_leave_the_board(client, student_headers, cafeteria_headers):
    order_id = place_order(client, student_headers).json()["id"]
    client.patch(f"/api/orders/{order_id}/status", json={"status": "delivered"}, headers=cafeteria_headers)

    board = client.get("/api/cafeteria/next-recess", headers=cafeteria_headers).json()

    assert board["orders"] == []


def test_orders_today_are_grouped_by_recess(client, student_headers, cafeteria_headers):
    place_order(client, student_headers)
    place_order(client, student_headers, recess_id=SECOND_RECESS_ID)

    groups = client.get("/api/cafeteria/orders-today", headers=cafeteria_headers).json()

    orders_count_by_recess = {group["recess"]["id"]: len(group["orders"]) for group in groups}
    assert orders_count_by_recess[FIRST_RECESS_ID] == 1
    assert orders_count_by_recess[SECOND_RECESS_ID] == 1


def test_daily_sales_summary(client, student_headers, other_student_headers, cafeteria_headers):
    place_order(client, student_headers)
    place_order(client, other_student_headers)

    summary = client.get("/api/cafeteria/sales-summary", headers=cafeteria_headers).json()

    assert summary["service_date"] == "2026-10-20"
    assert summary["total_orders"] == 2
    assert summary["total_revenue"] == 2 * (2 * 35 + 60)
    assert summary["products"][0] == {"product_name": "Medialuna", "units_sold": 4, "revenue": 140}


def test_invalid_cutoff_value_is_rejected(client, cafeteria_headers):
    response = client.put("/api/configuration/order-cutoff", json={"order_cutoff_minutes": -5}, headers=cafeteria_headers)

    assert response.status_code == 422
