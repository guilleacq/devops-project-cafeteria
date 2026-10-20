/**
 * Formato de horas, plata y estados.
 *
 * Las horas siempre se muestran en la zona del liceo, aunque el celular
 * esté configurado en otra. Los momentos `_at` de la API ya traen el
 * desfase (-03:00), así que `new Date(...)` los interpreta bien.
 */

export const SCHOOL_TIMEZONE = "America/Montevideo";

const clockFormatter = new Intl.DateTimeFormat("es-UY", {
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
  timeZone: SCHOOL_TIMEZONE,
});

const longDateFormatter = new Intl.DateTimeFormat("es-UY", {
  weekday: "long",
  day: "numeric",
  month: "long",
  timeZone: SCHOOL_TIMEZONE,
});

/** "2026-10-20T09:15:00-03:00" → "09:15" */
export function clockTime(isoMoment) {
  return clockFormatter.format(new Date(isoMoment));
}

/** "09:30:00" → "09:30" (hora de reloj del liceo, sin zona) */
export function wallTime(startTime) {
  return startTime.slice(0, 5);
}

/** "2026-10-20" → "martes 20 de octubre" */
export function longDate(serviceDate) {
  return longDateFormatter.format(new Date(`${serviceDate}T12:00:00-03:00`));
}

export function todayLongDate() {
  return longDateFormatter.format(new Date());
}

/** 1250 → "$ 1.250" */
export function pesos(amount) {
  return `$ ${amount.toLocaleString("es-UY")}`;
}

/** Milisegundos que faltan → "en 12 min", "en 1 h 05 min", "en menos de un minuto" */
export function timeLeft(milliseconds) {
  const totalMinutes = Math.floor(milliseconds / 60000);

  if (totalMinutes < 1) return "en menos de un minuto";
  if (totalMinutes < 60) return `en ${totalMinutes} min`;

  const hours = Math.floor(totalMinutes / 60);
  const minutes = String(totalMinutes % 60).padStart(2, "0");
  return `en ${hours} h ${minutes} min`;
}

/** Número de pedido de tres cifras, como en un ticket: 7 → "007" */
export function ticketNumber(orderId) {
  return String(orderId).padStart(3, "0");
}

export const STATUS_LABELS = {
  pending: "En preparación",
  ready: "Listo para retirar",
  delivered: "Entregado",
};

export function unitsLabel(count) {
  return count === 1 ? "1 producto" : `${count} productos`;
}

export function capitalize(text) {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/** Fecha de hoy en el liceo, como la espera la API: "2026-10-20" */
export function todayServiceDate() {
  return new Intl.DateTimeFormat("en-CA", { timeZone: SCHOOL_TIMEZONE }).format(new Date());
}
