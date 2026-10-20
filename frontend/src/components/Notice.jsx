/**
 * Un aviso dentro de la página. `tone="error"` para lo que salió mal
 * (con la explicación del backend), `tone="ok"` para confirmar una acción.
 */
export default function Notice({ tone = "info", title, children, onClose }) {
  return (
    <div className={`notice notice--${tone}`} role={tone === "error" ? "alert" : "status"}>
      <div>
        {title && <p className="notice__title">{title}</p>}
        <p className="notice__body">{children}</p>
      </div>
      {onClose && (
        <button type="button" className="notice__close" onClick={onClose} aria-label="Cerrar aviso">
          ×
        </button>
      )}
    </div>
  );
}
