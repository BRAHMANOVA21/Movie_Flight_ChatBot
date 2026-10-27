// Shared types. Shapes mirror TMDB (movies) and a generic flight-offer API,
// so swapping mock -> real providers only touches src/lib/providers/*.

export type Passport = "TR" | "AZ";
export type VisaStatus =
  | "domestic" | "visa_free" | "visa_on_arrival_free"
  | "visa_on_arrival" | "eta" | "e_visa" | "visa_required";
export type VisaTier = "no_visa" | "easy" | "hard";

export interface VisaInfo { status: VisaStatus; max_stay_days: number | null; note: string | null }

export interface Destination {
  id: string; city: string; country: string; country_code: string;
  airport_iata: string; lat: number; lon: number; region: string;
  climate_avg_high_c: number[];          // Jan..Dec
  tags: string[]; budget_level: 1 | 2 | 3; est_daily_cost_usd: number;
  rainy_months: number[]; best_months: number[]; blurb: string;
  visa: Record<Passport, VisaInfo>; direct_from: string[]; image_query: string;
}

export interface FlightOffer {
  id: string; origin: string; destination: string; destination_id: string;
  depart_date: string; return_date?: string; carrier: string;
  stops: 0 | 1; duration_min: number; price_usd: number; cabin: "economy" | "business";
  mock: true;
}

export interface Movie {
  id: string; tmdb_id: number | null; title: string; original_language: string;
  release_date: string | null; year: number;
  genres: { id: number; name: string }[]; runtime_min: number;
  vote_average: number; age_rating: string; overview: string;
  mood_tags: string[]; director: string | null; cast: string[];
  status: "in_theaters" | "streaming" | "classic" | "coming_soon";
  watch_providers_mock: string[]; box_office_worldwide_usd: number | null;
  popularity: number; poster_path: string | null; backdrop_path: string | null;
  trailer_query: string;
}

// ---- What the chat backend returns: text + rich blocks (Rufus-style) ----
export type ChatBlock =
  | { type: "text"; text: string }
  | { type: "movie_carousel"; title: string; items: Movie[]; reason_by_id?: Record<string, string> }
  | { type: "destination_carousel"; title: string; items: (Destination & { match_reasons: string[]; from_price_usd?: number })[] }
  | { type: "flight_list"; title: string; items: FlightOffer[] }
  | { type: "quick_replies"; options: string[] };   // follow-up chips

export interface ChatResponse { intent: "travel" | "movies" | "unclear" | "smalltalk"; blocks: ChatBlock[] }
