export default function Wordmark({ large = false }) {
  return (
    <div className={`wordmark ${large ? "wordmark--large" : ""}`}>
      <span className="wordmark__name">Cafetería</span>
      <span className="wordmark__tagline">pedí antes del timbre</span>
    </div>
  );
}
