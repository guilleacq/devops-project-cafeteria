import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../../api.js";
import Loading from "../../components/Loading.jsx";
import Notice from "../../components/Notice.jsx";
import OrderTicket from "../../components/OrderTicket.jsx";
import Stepper from "../../components/Stepper.jsx";
import { clockTime, pesos, timeLeft, todayLongDate, unitsLabel, wallTime } from "../../format.js";
import { useApiData, useNow } from "../../hooks.js";

/**
 * Pantalla principal del alumno: elegir recreo, elegir productos y confirmar.
 *
 * La pantalla deshabilita los recreos cerrados para ayudar, pero quien
 * decide es el backend: si responde ORDERING_CLOSED, se muestra su mensaje.
 */
export default function OrderPage() {
  const now = useNow(10);
  const recesses = useApiData(api.recessesToday, { refreshEverySeconds: 30 });
  const products = useApiData(api.products, { refreshEverySeconds: 60 });

  const [chosenRecessId, setChosenRecessId] = useState(null);
  const [quantities, setQuantities] = useState({});
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState(null);
  const [confirmedOrder, setConfirmedOrder] = useState(null);

  const todaysRecesses = recesses.data ?? [];
  const isOpen = (recess) => recess.is_accepting_orders && now < Date.parse(recess.ordering_closes_at);
  const openRecesses = todaysRecesses.filter(isOpen);

  // Si el alumno no eligió, o lo que eligió ya cerró, se sugiere el primero abierto.
  const chosenRecess =
    openRecesses.find((recess) => recess.id === chosenRecessId) ?? openRecesses[0] ?? null;

  const productsById = useMemo(
    () => Object.fromEntries((products.data ?? []).map((product) => [product.id, product])),
    [products.data],
  );

  const cartLines = Object.entries(quantities)
    .filter(([, quantity]) => quantity > 0)
    .map(([productId, quantity]) => ({ product: productsById[productId], quantity }))
    .filter((line) => line.product);

  const cartUnits = cartLines.reduce((sum, line) => sum + line.quantity, 0);
  const cartTotal = cartLines.reduce((sum, line) => sum + line.quantity * line.product.price, 0);

  function setQuantity(productId, quantity) {
    setQuantities((current) => ({ ...current, [productId]: quantity }));
  }

  async function confirmOrder() {
    setIsSending(true);
    setError(null);

    try {
      const items = cartLines.map((line) => ({ product_id: line.product.id, quantity: line.quantity }));
      const order = await api.placeOrder(chosenRecess.id, items);
      setConfirmedOrder(order);
      setQuantities({});
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (orderError) {
      setError(orderError);
      if (orderError.code === "ORDERING_CLOSED") recesses.reload();
      if (orderError.code === "PRODUCT_SOLD_OUT") products.reload();
    } finally {
      setIsSending(false);
    }
  }

  if (recesses.isLoading || products.isLoading) return <Loading />;

  const loadError = recesses.error ?? products.error;
  if (loadError) return <Notice tone="error">{loadError.detail}</Notice>;

  return (
    <div className="order-page">
      {confirmedOrder && (
        <section className="confirmation" aria-labelledby="confirmation-title">
          <h2 id="confirmation-title" className="section-title">
            Pedido confirmado
          </h2>
          <p className="muted">
            Pasalo a buscar en el {confirmedOrder.recess_name.toLowerCase()}. Te avisamos acá cuando esté listo.
          </p>
          <OrderTicket order={confirmedOrder} />
          <div className="confirmation__actions">
            <Link to="/mis-pedidos" className="button button--ghost">
              Ver mis pedidos
            </Link>
            <button type="button" className="link-button" onClick={() => setConfirmedOrder(null)}>
              Hacer otro pedido
            </button>
          </div>
        </section>
      )}

      <section aria-labelledby="recess-title">
        <div className="section-head">
          <h2 id="recess-title" className="section-title">
            ¿Para qué recreo?
          </h2>
          <p className="section-meta">{todayLongDate()}</p>
        </div>

        {todaysRecesses.length === 0 ? (
          <p className="empty">Hoy no hay recreos cargados.</p>
        ) : (
          <ol className="timetable">
            {todaysRecesses.map((recess) => {
              const open = isOpen(recess);
              const selected = open && chosenRecess?.id === recess.id;
              const closesAt = Date.parse(recess.ordering_closes_at);

              return (
                <li key={recess.id}>
                  <label className={`period ${open ? "" : "period--closed"} ${selected ? "period--selected" : ""}`}>
                    <input
                      type="radio"
                      name="recess"
                      className="visually-hidden"
                      disabled={!open}
                      checked={selected}
                      onChange={() => setChosenRecessId(recess.id)}
                    />
                    <span className="period__time">{wallTime(recess.start_time)}</span>
                    <span className="period__body">
                      <span className="period__name">{recess.name}</span>
                      {open ? (
                        <span className="period__status">
                          Pedís hasta las <mark>{clockTime(recess.ordering_closes_at)}</mark>
                          <span className="period__countdown"> · cierra {timeLeft(closesAt - now)}</span>
                        </span>
                      ) : (
                        <span className="period__status">Cerró a las {clockTime(recess.ordering_closes_at)}</span>
                      )}
                    </span>
                    <span className="period__check" aria-hidden="true" />
                  </label>
                </li>
              );
            })}
          </ol>
        )}

        {todaysRecesses.length > 0 && openRecesses.length === 0 && (
          <Notice title="Por hoy ya no se puede pedir">
            Cerraron los pedidos de todos los recreos. Mañana a primera hora se abren de nuevo.
          </Notice>
        )}
      </section>

      {chosenRecess && (
        <section aria-labelledby="menu-title">
          <div className="section-head">
            <h2 id="menu-title" className="section-title">
              ¿Qué vas a querer?
            </h2>
            <p className="section-meta">hasta 20 de cada uno</p>
          </div>

          <ul className="menu">
            {products.data.map((product) => (
              <li key={product.id} className={`menu__item ${product.is_sold_out ? "menu__item--sold-out" : ""}`}>
                <span className="menu__name">{product.name}</span>
                <span className="menu__leader" aria-hidden="true" />
                <span className="menu__price">{pesos(product.price)}</span>
                {product.is_sold_out ? (
                  <span className="menu__sold-out">Agotado</span>
                ) : (
                  <Stepper
                    label={product.name.toLowerCase()}
                    value={quantities[product.id] ?? 0}
                    onChange={(quantity) => setQuantity(product.id, quantity)}
                  />
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {error && (
        <Notice
          tone="error"
          title={error.code === "ORDERING_CLOSED" ? "Ya cerraron los pedidos" : "No se pudo hacer el pedido"}
          onClose={() => setError(null)}
        >
          {error.detail}
        </Notice>
      )}

      {chosenRecess && cartUnits > 0 && (
        <div className="cart-bar">
          <div className="cart-bar__summary">
            <span className="cart-bar__units">
              {unitsLabel(cartUnits)} · {chosenRecess.name.toLowerCase()}
            </span>
            <span className="cart-bar__total">{pesos(cartTotal)}</span>
          </div>
          <button type="button" className="button button--highlight" onClick={confirmOrder} disabled={isSending}>
            {isSending ? "Enviando…" : "Confirmar pedido"}
          </button>
        </div>
      )}
    </div>
  );
}
