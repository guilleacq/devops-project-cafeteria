import { Link } from "react-router-dom";

import { api } from "../../api.js";
import Loading from "../../components/Loading.jsx";
import Notice from "../../components/Notice.jsx";
import OrderTicket from "../../components/OrderTicket.jsx";
import { capitalize, longDate } from "../../format.js";
import { useApiData } from "../../hooks.js";

/**
 * Los pedidos del alumno. Se refresca solo para que vea cuando la
 * cafetería lo marca como listo, sin tener que recargar.
 */
export default function MyOrdersPage() {
  const orders = useApiData(api.myOrders, { refreshEverySeconds: 15 });

  if (orders.isLoading) return <Loading />;
  if (orders.error) return <Notice tone="error">{orders.error.detail}</Notice>;

  if (orders.data.length === 0) {
    return (
      <div className="empty-state">
        <p className="empty-state__title">Todavía no hiciste ningún pedido.</p>
        <Link to="/pedir" className="button button--ink">
          Hacer mi primer pedido
        </Link>
      </div>
    );
  }

  const ordersByDate = groupBy(orders.data, (order) => order.service_date);

  return (
    <div className="my-orders">
      {Object.entries(ordersByDate).map(([serviceDate, ordersOfDay]) => (
        <section key={serviceDate} aria-label={longDate(serviceDate)}>
          <div className="section-head">
            <h2 className="section-title">{capitalize(longDate(serviceDate))}</h2>
          </div>
          <div className="ticket-grid">
            {ordersOfDay.map((order) => (
              <OrderTicket key={order.id} order={order} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

function groupBy(list, keyOf) {
  return list.reduce((groups, element) => {
    (groups[keyOf(element)] ??= []).push(element);
    return groups;
  }, {});
}
