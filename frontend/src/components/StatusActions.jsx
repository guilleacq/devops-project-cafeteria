import { useState } from "react";

import { api } from "../api.js";

/**
 * Botones de la cafetería para avanzar un pedido. Los estados solo van
 * hacia adelante: pendiente → listo → entregado (o directo a entregado).
 */
export default function StatusActions({ order, onChanged, onError }) {
  const [isSending, setIsSending] = useState(false);

  async function changeStatus(status) {
    setIsSending(true);
    try {
      await api.changeOrderStatus(order.id, status);
      await onChanged();
    } catch (error) {
      onError(error);
    } finally {
      setIsSending(false);
    }
  }

  if (order.status === "delivered") return null;

  return (
    <>
      {order.status === "pending" && (
        <button type="button" className="button button--ink button--small" disabled={isSending} onClick={() => changeStatus("ready")}>
          Marcar listo
        </button>
      )}
      <button type="button" className="button button--ghost button--small" disabled={isSending} onClick={() => changeStatus("delivered")}>
        Entregado
      </button>
    </>
  );
}
