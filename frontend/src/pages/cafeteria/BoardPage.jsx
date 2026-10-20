import { useState } from "react";

import { api } from "../../api.js";
import Loading from "../../components/Loading.jsx";
import Notice from "../../components/Notice.jsx";
import OrderTicket from "../../components/OrderTicket.jsx";
import StatusActions from "../../components/StatusActions.jsx";
import { clockTime, timeLeft, wallTime } from "../../format.js";
import { useApiData, useNow } from "../../hooks.js";

const REFRESH_EVERY_SECONDS = 5;

/**
 * La pantalla que la cafetería deja abierta: qué preparar y a quién
 * entregarle en el próximo recreo. Se actualiza sola cada pocos segundos.
 */
export default function BoardPage() {
  const now = useNow(1);
  const board = useApiData(api.nextRecessBoard, { refreshEverySeconds: REFRESH_EVERY_SECONDS });
  const [actionError, setActionError] = useState(null);

  if (board.isLoading) return <Loading />;
  if (board.error && !board.data) return <Notice tone="error">{board.error.detail}</Notice>;

  const { recess, orders, products_to_prepare: productsToPrepare, message } = board.data;

  if (!recess) {
    return (
      <div className="empty-state">
        <p className="empty-state__title">{message}</p>
        <p className="muted">Mañana los pedidos aparecen acá apenas los hagan los alumnos.</p>
      </div>
    );
  }

  const pendingOrders = orders.filter((order) => order.status === "pending");
  const readyOrders = orders.filter((order) => order.status === "ready");
  const secondsSinceUpdate = Math.max(0, Math.round((now - board.lastUpdatedAt) / 1000));

  return (
    <div className="board">
      <header className="board__head">
        <div>
          <p className="eyebrow">Próximo recreo</p>
          <h1 className="board__title">
            {recess.name} <span className="board__time">{wallTime(recess.start_time)}</span>
          </h1>
        </div>
        <dl className="board__facts">
          <div>
            <dt>Empieza</dt>
            <dd>{now < Date.parse(recess.starts_at) ? timeLeft(Date.parse(recess.starts_at) - now) : "ahora, en curso"}</dd>
          </div>
          <div>
            <dt>Pedidos</dt>
            <dd>
              {recess.is_accepting_orders
                ? `abiertos hasta las ${clockTime(recess.ordering_closes_at)}`
                : `cerrados desde las ${clockTime(recess.ordering_closes_at)}`}
            </dd>
          </div>
          <div>
            <dt>Actualizado</dt>
            <dd className={board.error ? "text-error" : ""}>
              {board.error ? "sin conexión" : secondsSinceUpdate < 2 ? "recién" : `hace ${secondsSinceUpdate} s`}
            </dd>
          </div>
        </dl>
      </header>

      {actionError && (
        <Notice tone="error" onClose={() => setActionError(null)}>
          {actionError.detail}
        </Notice>
      )}

      <div className="board__columns">
        <section className="prep" aria-labelledby="prep-title">
          <h2 id="prep-title" className="section-title">
            A preparar
          </h2>
          {productsToPrepare.length === 0 ? (
            <p className="empty">Nada pendiente por ahora.</p>
          ) : (
            <ul className="prep__list">
              {productsToPrepare.map((product) => (
                <li key={product.product_name}>
                  <span className="prep__count">{product.quantity}</span>
                  <span className="prep__name">{product.product_name}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="rail" aria-labelledby="rail-title">
          <div className="section-head">
            <h2 id="rail-title" className="section-title">
              Pedidos
            </h2>
            <p className="section-meta">
              {pendingOrders.length} por preparar · {readyOrders.length} listos
            </p>
          </div>

          {orders.length === 0 ? (
            <p className="empty">Todavía no hay pedidos para este recreo.</p>
          ) : (
            <div className="ticket-grid">
              {[...pendingOrders, ...readyOrders].map((order) => (
                <OrderTicket
                  key={order.id}
                  order={order}
                  showStudent
                  compact
                  actions={<StatusActions order={order} onChanged={board.reload} onError={setActionError} />}
                />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
