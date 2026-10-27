// The "no visa required" logic layer. Data -> tier -> filter.
import visaMeta from "../data/visa_meta.json";
import type { Destination, Passport, VisaTier } from "../types/index.ts";

const TIERS = visaMeta.tiers as Record<string, VisaTier>;

export type VisaPreference = "strict_no_visa" | "allow_easy" | "any";

export function visaTier(dest: Destination, passport: Passport): VisaTier {
  return TIERS[dest.visa[passport].status] ?? "hard";
}

export function passesVisa(dest: Destination, passport: Passport, pref: VisaPreference) {
  const tier = visaTier(dest, passport);
  if (pref === "any") return true;
  if (pref === "allow_easy") return tier !== "hard";
  return tier === "no_visa";
}

// Short label for the card badge
export function visaBadge(dest: Destination, passport: Passport) {
  const v = dest.visa[passport];
  const label: Record<string, string> = {
    domestic: "Domestic", visa_free: "Visa-free", visa_on_arrival_free: "Free visa on arrival",
    visa_on_arrival: "Visa on arrival", eta: "Online authorisation", e_visa: "e-Visa", visa_required: "Visa required",
  };
  return {
    text: label[v.status] + (v.max_stay_days ? ` · ${v.max_stay_days} days` : ""),
    tier: visaTier(dest, passport),
    note: v.note,
    verified_at: visaMeta.verified_at,
  };
}
