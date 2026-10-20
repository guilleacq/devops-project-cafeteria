export const MAX_QUANTITY_PER_PRODUCT = 20;

/** Botones − y + para elegir cuántas unidades de un producto. */
export default function Stepper({ value, onChange, label, disabled = false }) {
  return (
    <div className={`stepper ${value > 0 ? "stepper--active" : ""}`}>
      {value > 0 && (
        <>
          <button
            type="button"
            className="stepper__button"
            onClick={() => onChange(value - 1)}
            aria-label={`Sacar un ${label}`}
          >
            −
          </button>
          <span className="stepper__value" aria-live="polite">
            {value}
          </span>
        </>
      )}
      <button
        type="button"
        className="stepper__button"
        onClick={() => onChange(value + 1)}
        disabled={disabled || value >= MAX_QUANTITY_PER_PRODUCT}
        aria-label={`Agregar un ${label}`}
      >
        +
      </button>
    </div>
  );
}
