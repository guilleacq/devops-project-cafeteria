import { useState } from "react";

import { api } from "../../api.js";
import Loading from "../../components/Loading.jsx";
import Notice from "../../components/Notice.jsx";
import OrderTicket from "../../components/OrderTicket.jsx";
import StatusActions from "../../components/StatusActions.jsx";
import { clockTime, wallTime } from "../../format.js";
import { useApiData } from "../../hooks.js";

/** Todos los pedidos del día, en cualquier estado, agrupados por recreo. */
export default function TodayPage() {
  const groups = useApiData(api.ordersToday, { refreshEverySeconds: 15 });
  const [actionError, setActionError] = useState(null);

  if (groups.isLoading) return <Loading />;
  if (groups.error) return <Notice tone="error">{groups.error.detail}</Notice>;

  return (
    <div className="today">
      {actionError && (
        <Notice tone="error" onClose={() => setActionError(null)}>
          {actionError.detail}
        </Notice>
      )}

      {groups.data.map(({ recess, orders }) => {
        const delivered = orders.filter((order) => order.status === "delivered").length;

        return (
          <section key={recess.id} className="today__group" aria-labelledby={`recess-${recess.id}`}>
            <div className="section-head">
              <h2 id={`recess-${recess.id}`} className="section-title">
                <span className="mono">{wallTime(recess.start_time)}</span> {recess.name}
              </h2>
              <p className="section-meta">
                {orders.length === 0
                  ? "sin pedidos"
                  : `${orders.length} pedidos · ${delivered} entregados · cierre ${clockTime(recess.ordering_closes_at)}`}
              </p>
            </div>

            {orders.length > 0 && (
              <div className="ticket-grid">
                {orders.map((order) => (
                  <OrderTicket
                    key={order.id}
                    order={order}
                    showStudent
                    compact
                    actions={<StatusActions order={order} onChanged={groups.reload} onError={setActionError} />}
                  />
                ))}
              </div>
            )}
          </section>
        );
      })}
    </div>
  );
}
