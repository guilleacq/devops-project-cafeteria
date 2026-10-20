import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Carga datos de la API y, si se indica, los vuelve a pedir cada tantos
 * segundos. Devuelve también `reload` para refrescar después de una acción.
 *
 * `dependsOn` funciona como las dependencias de useEffect: si cambia algún
 * valor (por ejemplo, la fecha elegida), se vuelve a cargar.
 */
export function useApiData(loader, { refreshEverySeconds, dependsOn = [] } = {}) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null);

  const loaderRef = useRef(loader);
  loaderRef.current = loader;

  const reload = useCallback(async () => {
    try {
      const result = await loaderRef.current();
      setData(result);
      setError(null);
      setLastUpdatedAt(Date.now());
    } catch (loadError) {
      setError(loadError);
    }
  }, []);

  useEffect(() => {
    reload();

    if (!refreshEverySeconds) return;

    const interval = setInterval(reload, refreshEverySeconds * 1000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reload, refreshEverySeconds, ...dependsOn]);

  return { data, error, reload, lastUpdatedAt, isLoading: data === null && error === null };
}

/** La hora actual, actualizada cada tantos segundos. Para las cuentas regresivas. */
export function useNow(everySeconds = 15) {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const interval = setInterval(() => setNow(Date.now()), everySeconds * 1000);
    return () => clearInterval(interval);
  }, [everySeconds]);

  return now;
}
