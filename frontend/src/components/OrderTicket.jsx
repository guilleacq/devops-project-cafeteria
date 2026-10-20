import { STATUS_LABELS, pesos, ticketNumber, wallTime } from "../format.js";

/**
 * Un pedido con forma de ticket de cantina: número grande, recreo, lo que
 * se pidió y el total. El borde de abajo es dentado, como un papel cortado.
 *
 * `actions` permite que la cafetería agregue sus botones al pie.
 */
export default function OrderTicket({ order, showStudent = false, actions = null, compact = false }) {
  return (
    // El borde dentado recorta la sombra, por eso la sombra va en el contenedor.
    <div className="ticket-shadow">
    <article className={`ticket ticket--${order.status} ${compact ? "ticket--compact" : ""}`}>
      <header className="ticket__head">
        <div>
          <p className="ticket__label">Pedido</p>
          <p className="ticket__number">#{ticketNumber(order.id)}</p>
        </div>
        <span className={`stamp stamp--${order.status}`}>{STATUS_LABELS[order.status]}</span>
      </header>

      {showStudent ? (
        <p className="ticket__student">{order.student_name}</p>
      ) : (
        <p className="ticket__recess">
          {order.recess_name} · <span className="mono">{wallTime(order.recess_start_time)}</span>
        </p>
      )}

      <ul className="ticket__items">
        {order.items.map((item) => (
          <li key={item.product_id}>
            <span className="ticket__qty">{item.quantity}×</span>
            <span className="ticket__item-name">{item.product_name}</span>
            {!compact && <span className="ticket__subtotal">{pesos(item.subtotal)}</span>}
          </li>
        ))}
      </ul>

      <footer className="ticket__foot">
        <span>Total</span>
        <span className="ticket__total">{pesos(order.total)}</span>
      </footer>

      {actions && <div className="ticket__actions">{actions}</div>}
    </article>
    </div>
  );
}
