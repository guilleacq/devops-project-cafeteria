import { useEffect, useState } from "react";

import { api } from "../../api.js";
import Loading from "../../components/Loading.jsx";
import Notice from "../../components/Notice.jsx";
import { wallTime } from "../../format.js";
import { useApiData } from "../../hooks.js";

/** Ajustes de la cafetería: el margen para pedir (X), los productos y los recreos. */
export default function SettingsPage() {
  return (
    <div className="settings">
      <CutoffSettings />
      <ProductSettings />
      <RecessSettings />
    </div>
  );
}

// ---------------------------------------------------------------------------
// X: minutos antes del recreo en que se cierran los pedidos
// ---------------------------------------------------------------------------

function CutoffSettings() {
  const configuration = useApiData(api.configuration);
  const recesses = useApiData(api.recesses);
  const [minutes, setMinutes] = useState("");
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    if (configuration.data) setMinutes(String(configuration.data.order_cutoff_minutes));
  }, [configuration.data]);

  async function save(event) {
    event.preventDefault();
    try {
      const saved = await api.updateOrderCutoff(Number(minutes));
      await configuration.reload();
      setFeedback({ tone: "ok", text: `Listo. Desde ahora los pedidos cierran ${saved.order_cutoff_minutes} minutos antes de cada recreo.` });
    } catch (error) {
      setFeedback({ tone: "error", text: error.detail });
    }
  }

  if (configuration.isLoading) return <Loading />;

  const firstRecess = recesses.data?.[0];
  const minutesNumber = Number(minutes);
  const isValidNumber = minutes !== "" && Number.isInteger(minutesNumber) && minutesNumber >= 0 && minutesNumber <= 240;

  return (
    <section className="sheet" aria-labelledby="cutoff-title">
      <h2 id="cutoff-title" className="sheet__title">
        Hasta cuándo se puede pedir
      </h2>
      <p className="muted">
        Los alumnos pueden pedir hasta esta cantidad de minutos antes de cada recreo. El cambio vale desde el próximo pedido.
      </p>

      <form className="cutoff" onSubmit={save}>
        <label className="field field--inline">
          <span className="field__label">Minutos antes</span>
          <input
            type="number"
            min="0"
            max="240"
            inputMode="numeric"
            className="cutoff__input"
            value={minutes}
            onChange={(event) => {
              setMinutes(event.target.value);
              setFeedback(null);
            }}
          />
        </label>
        <button type="submit" className="button button--ink" disabled={!isValidNumber}>
          Guardar
        </button>
      </form>

      {firstRecess && isValidNumber && (
        <p className="example">
          Por ejemplo: el {firstRecess.name.toLowerCase()} es a las {wallTime(firstRecess.start_time)}, así que se podría
          pedir hasta las <mark>{subtractMinutes(firstRecess.start_time, minutesNumber)}</mark>.
        </p>
      )}

      {feedback && <Notice tone={feedback.tone}>{feedback.text}</Notice>}
    </section>
  );
}

/** "09:30:00" menos 15 → "09:15". Solo para el ejemplo; el cálculo real lo hace el backend. */
function subtractMinutes(startTime, minutes) {
  const [hours, mins] = startTime.split(":").map(Number);
  const total = (((hours * 60 + mins - minutes) % 1440) + 1440) % 1440;
  return `${String(Math.floor(total / 60)).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
}

// ---------------------------------------------------------------------------
// Productos
// ---------------------------------------------------------------------------

function ProductSettings() {
  const products = useApiData(api.products);
  const [error, setError] = useState(null);

  async function run(action) {
    try {
      await action();
      setError(null);
      await products.reload();
    } catch (actionError) {
      setError(actionError.detail);
    }
  }

  return (
    <section className="sheet" aria-labelledby="products-title">
      <h2 id="products-title" className="sheet__title">
        Productos
      </h2>
      <p className="muted">Un producto agotado sigue en la lista pero nadie lo puede pedir hasta que lo vuelvas a activar.</p>

      {products.isLoading && <Loading />}

      {products.data && (
        <ul className="editable-list">
          {products.data.map((product) => (
            <ProductRow
              key={product.id}
              product={product}
              onSave={(changes) => run(() => api.updateProduct(product.id, changes))}
            />
          ))}
        </ul>
      )}

      <NewProductForm onCreate={(product) => run(() => api.createProduct(product))} />

      {error && <Notice tone="error">{error}</Notice>}
    </section>
  );
}

function ProductRow({ product, onSave }) {
  const [name, setName] = useState(product.name);
  const [price, setPrice] = useState(String(product.price));
  const hasChanges = name.trim() !== product.name || Number(price) !== product.price;

  return (
    <li className={`editable-row ${product.is_sold_out ? "editable-row--muted" : ""}`}>
      <input aria-label="Nombre" className="editable-row__name" value={name} onChange={(event) => setName(event.target.value)} />
      <label className="money-input">
        <span aria-hidden="true">$</span>
        <input
          aria-label={`Precio de ${product.name}`}
          type="number"
          min="1"
          inputMode="numeric"
          value={price}
          onChange={(event) => setPrice(event.target.value)}
        />
      </label>
      {hasChanges ? (
        <button type="button" className="button button--ink button--small" onClick={() => onSave({ name: name.trim(), price: Number(price) })}>
          Guardar
        </button>
      ) : (
        <button
          type="button"
          className={`toggle ${product.is_sold_out ? "toggle--off" : ""}`}
          aria-pressed={product.is_sold_out}
          onClick={() => onSave({ is_sold_out: !product.is_sold_out })}
        >
          {product.is_sold_out ? "Agotado" : "Disponible"}
        </button>
      )}
    </li>
  );
}

function NewProductForm({ onCreate }) {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");

  async function submit(event) {
    event.preventDefault();
    await onCreate({ name: name.trim(), price: Number(price) });
    setName("");
    setPrice("");
  }

  return (
    <form className="editable-row editable-row--new" onSubmit={submit}>
      <input aria-label="Nombre del producto nuevo" placeholder="Producto nuevo" className="editable-row__name" required value={name} onChange={(event) => setName(event.target.value)} />
      <label className="money-input">
        <span aria-hidden="true">$</span>
        <input aria-label="Precio del producto nuevo" type="number" min="1" inputMode="numeric" required value={price} onChange={(event) => setPrice(event.target.value)} />
      </label>
      <button type="submit" className="button button--ghost button--small">
        Agregar
      </button>
    </form>
  );
}

// ---------------------------------------------------------------------------
// Recreos
// ---------------------------------------------------------------------------

function RecessSettings() {
  const recesses = useApiData(api.recesses);
  const [error, setError] = useState(null);

  async function run(action) {
    try {
      await action();
      setError(null);
      await recesses.reload();
    } catch (actionError) {
      setError(actionError.detail);
    }
  }

  return (
    <section className="sheet" aria-labelledby="recesses-title">
      <h2 id="recesses-title" className="sheet__title">
        Recreos
      </h2>
      <p className="muted">Se repiten todos los días a la misma hora. La duración define hasta cuándo se ve el recreo en el tablero.</p>

      {recesses.isLoading && <Loading />}

      {recesses.data && (
        <ul className="editable-list">
          {recesses.data.map((recess) => (
            <RecessForm
              key={recess.id}
              recess={recess}
              submitLabel="Guardar"
              onSubmit={(changes) => run(() => api.updateRecess(recess.id, changes))}
            />
          ))}
        </ul>
      )}

      <RecessForm submitLabel="Agregar" onSubmit={(recess) => run(() => api.createRecess(recess))} />

      {error && <Notice tone="error">{error}</Notice>}
    </section>
  );
}

/** Sirve para editar un recreo existente o, sin `recess`, para crear uno nuevo. */
function RecessForm({ recess = null, submitLabel, onSubmit }) {
  const initial = {
    name: recess?.name ?? "",
    startTime: recess ? wallTime(recess.start_time) : "",
    duration: String(recess?.duration_minutes ?? 15),
  };
  const [name, setName] = useState(initial.name);
  const [startTime, setStartTime] = useState(initial.startTime);
  const [duration, setDuration] = useState(initial.duration);

  const hasChanges = name !== initial.name || startTime !== initial.startTime || duration !== initial.duration;

  async function submit(event) {
    event.preventDefault();
    await onSubmit({ name: name.trim(), start_time: startTime, duration_minutes: Number(duration) });
    if (!recess) {
      setName("");
      setStartTime("");
      setDuration("15");
    }
  }

  const Wrapper = recess ? "li" : "div";

  return (
    <Wrapper className={`editable-row editable-row--recess ${recess ? "" : "editable-row--new"}`}>
      <form className="editable-row__form" onSubmit={submit}>
        <input aria-label="Hora" type="time" required className="editable-row__time" value={startTime} onChange={(event) => setStartTime(event.target.value)} />
        <input aria-label="Nombre del recreo" placeholder="Recreo nuevo" required className="editable-row__name" value={name} onChange={(event) => setName(event.target.value)} />
        <label className="minutes-input">
          <input aria-label="Duración en minutos" type="number" min="1" max="240" inputMode="numeric" required value={duration} onChange={(event) => setDuration(event.target.value)} />
          <span aria-hidden="true">min</span>
        </label>
        {(hasChanges || !recess) && (
          <button type="submit" className={`button button--small ${recess ? "button--ink" : "button--ghost"}`}>
            {submitLabel}
          </button>
        )}
      </form>
    </Wrapper>
  );
}
