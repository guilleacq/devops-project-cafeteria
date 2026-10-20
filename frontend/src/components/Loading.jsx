export default function Loading({ children = "Cargando…" }) {
  return <p className="loading">{children}</p>;
}
