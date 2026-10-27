// Mock flight provider: deterministic prices for ANY date, no static flight list.
// Same inputs -> same results, so demos are repeatable.
import routes from "../../data/routes.json";
import type { FlightOffer } from "../../types";

function seeded(str: string) {            // tiny deterministic PRNG
  let h = 2166136261;
  for (const c of str) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
  return () => ((h = Math.imul(h ^ (h >>> 15), 2246822507) >>> 0) % 10000) / 10000;
}

function seasonMultiplier(date: string) {
  const d = new Date(date), m = d.getMonth() + 1, day = d.getDate();
  if ((m === 12 && day >= 20) || (m === 1 && day <= 5)) return 1.45;   // New Year peak
  if (m === 7 || m === 8) return 1.25;                                 // summer peak
  if (m === 11 || m === 2) return 0.9;                                 // shoulder
  return 1.0;
}

export interface FlightQuery {
  origin: string; destination: string; depart_date: string; return_date?: string;
  adults?: number; direct_only?: boolean; cabin?: "economy" | "business"; max_price_usd?: number;
}

export function searchFlights(q: FlightQuery): FlightOffer[] {
  const route = routes.find(r => r.origin === q.origin && r.destination === q.destination);
  if (!route) return [];
  const rnd = seeded(`${q.origin}-${q.destination}-${q.depart_date}`);
  const pax = q.adults ?? 1;
  const cabinMult = q.cabin === "business" ? 3.2 : 1;
  const tripMult = q.return_date ? 1.8 : 1;

  const offers: FlightOffer[] = route.carriers.map((carrier, i) => {
    const direct = route.direct_available && !carrier.includes("via");
    const base = route.base_price_usd * (direct ? 1.1 : 0.9);
    const price = base * seasonMultiplier(q.depart_date) * cabinMult * tripMult * (0.85 + rnd() * 0.4) * pax;
    return {
      id: `${q.origin}${q.destination}${q.depart_date}-${i}`,
      origin: q.origin, destination: q.destination, destination_id: route.destination_id,
      depart_date: q.depart_date, return_date: q.return_date, carrier,
      stops: direct ? 0 : 1,
      duration_min: Math.round(route.base_duration_min * (direct ? 1 : 1.05) + rnd() * 60),
      price_usd: Math.round(price), cabin: q.cabin ?? "economy", mock: true,
    };
  });

  return offers
    .filter(o => !q.direct_only || o.stops === 0)
    .filter(o => !q.max_price_usd || o.price_usd <= q.max_price_usd)
    .sort((a, b) => a.price_usd - b.price_usd);
}

export function cheapestFrom(origin: string, destinationIata: string, date: string) {
  return searchFlights({ origin, destination: destinationIata, depart_date: date })[0]?.price_usd;
}
