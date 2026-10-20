import { useState } from "react";

import { api } from "../../api.js";
import Loading from "../../components/Loading.jsx";
import Notice from "../../components/Notice.jsx";
import { capitalize, longDate, pesos, todayServiceDate } from "../../format.js";
import { useApiData } from "../../hooks.js";

/** Resumen de ventas de un día: cuántos pedidos, cuánta plata y qué se vendió. */
export default function SalesPage() {
  const [serviceDate, setServiceDate] = useState(todayServiceDate);
  const summary = useApiData(() => api.salesSummary(serviceDate), { dependsOn: [serviceDate] });

  return (
    <div className="sales">
      <div className="section-head">
        <h2 className="section-title">Ventas del {longDate(serviceDate)}</h2>
        <label className="field field--inline">
          <span className="field__label">Día</span>
          <input
            type="date"
            value={serviceDate}
            max={todayServiceDate()}
            onChange={(event) => event.target.value && setServiceDate(event.target.value)}
          />
        </label>
      </div>

      {summary.isLoading && <Loading />}
      {summary.error && <Notice tone="error">{summary.error.detail}</Notice>}

      {summary.data && (
        <>
          <dl className="tally">
            <div>
              <dt>Recaudado</dt>
              <dd className="tally__money">{pesos(summary.data.total_revenue)}</dd>
            </div>
            <div>
              <dt>Pedidos</dt>
              <dd>{summary.data.total_orders}</dd>
            </div>
            <div>
              <dt>Entregados</dt>
              <dd>{summary.data.delivered_orders}</dd>
            </div>
          </dl>

          {summary.data.products.length === 0 ? (
            <p className="empty">{capitalize(longDate(serviceDate))} no hubo ventas.</p>
          ) : (
            <table className="ledger">
              <thead>
                <tr>
                  <th scope="col">Producto</th>
                  <th scope="col" className="num">Unidades</th>
                  <th scope="col" className="num">Recaudado</th>
                </tr>
              </thead>
              <tbody>
                {summary.data.products.map((product) => (
                  <tr key={product.product_name}>
                    <td>{product.product_name}</td>
                    <td className="num">{product.units_sold}</td>
                    <td className="num">{pesos(product.revenue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </div>
  );
}
