// Destination search: climate + visa + budget + tags -> ranked results with reasons.
import destinations from "../../data/destinations.json";
import type { Destination, Passport } from "../../types";
import { passesVisa, visaTier, type VisaPreference } from "../visa";
import { cheapestFrom } from "./flights.mock";

export interface DestinationQuery {
  months: number[];                // travel months, e.g. [12,1]
  passport?: Passport;
  visa_pref?: VisaPreference;      // default strict when passport known
  min_avg_high_c?: number;         // "warm" ~ 24, "hot/beach" ~ 27
  max_avg_high_c?: number;         // "not too hot", or ski (<5)
  tags?: string[];                 // beach, ski, city, family, honeymoon...
  max_budget_level?: 1 | 2 | 3;
  origin?: string;                 // IST / SAW / ESB / GYD -> adds from-price
  depart_date?: string;
  avoid_rainy?: boolean;
  limit?: number;
}

const DATA = destinations as unknown as Destination[];
const avgHigh = (d: Destination, months: number[]) =>
  months.reduce((s, m) => s + d.climate_avg_high_c[m - 1], 0) / months.length;

export function searchDestinations(q: DestinationQuery) {
  const pref = q.visa_pref ?? (q.passport ? "strict_no_visa" : "any");
  return DATA
    .filter(d => !q.passport || passesVisa(d, q.passport, pref))
    .filter(d => !q.passport || d.visa[q.passport].status !== "domestic" || q.tags?.length) // don't suggest home city by default
    .filter(d => q.min_avg_high_c == null || avgHigh(d, q.months) >= q.min_avg_high_c)
    .filter(d => q.max_avg_high_c == null || avgHigh(d, q.months) <= q.max_avg_high_c)
    .filter(d => !q.max_budget_level || d.budget_level <= q.max_budget_level)
    .filter(d => !q.avoid_rainy || !q.months.some(m => d.rainy_months.includes(m)))
    .map(d => {
      const t = Math.round(avgHigh(d, q.months));
      const tagHits = (q.tags ?? []).filter(t => d.tags.includes(t));
      const inBest = q.months.filter(m => d.best_months.includes(m)).length / q.months.length;
      const rainy = q.months.some(m => d.rainy_months.includes(m));
      const reasons = [`~${t}°C average highs`];
      if (q.passport) reasons.push(visaTier(d, q.passport) === "no_visa" ? "No visa needed" : "Easy online/arrival visa");
      if (inBest >= 0.5) reasons.push("Best season to visit");
      if (tagHits.length) reasons.push(tagHits.join(", "));
      if (rainy) reasons.push("Rainy season - expect showers");
      const score = tagHits.length * 3 + inBest * 4 - (rainy ? 3 : 0) + (q.origin && d.direct_from.includes(q.origin) ? 1.5 : 0);
      const from_price_usd = q.origin && q.depart_date ? cheapestFrom(q.origin, d.airport_iata, q.depart_date) : undefined;
      return { ...d, match_reasons: reasons, score, from_price_usd };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, q.limit ?? 8);
}
