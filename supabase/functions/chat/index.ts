// Supabase Edge Function: the chat brain.
// 1) LLM reads the conversation + user profile (passport, home airport)
// 2) LLM calls tools (search_destinations / search_flights / search_movies)
// 3) We return { intent, blocks[] } -> the frontend renders text + cards.
// API key lives in Supabase secrets, never in the browser.
// NOTE: copy src/lib + src/data into supabase/functions/_shared (or symlink) for deployment.
import { searchDestinations } from "../_shared/lib/providers/destinations.mock.ts";
import { searchFlights } from "../_shared/lib/providers/flights.mock.ts";
import { searchMovies } from "../_shared/lib/providers/movies.mock.ts";

const MODEL = Deno.env.get("LLM_MODEL") ?? "claude-sonnet-5-5";
const today = () => new Date().toISOString().slice(0, 10);

const SYSTEM = (profile: any) => `You are a travel & movie assistant inside a shopping-style chat.
Today is ${today()}. User profile: passport=${profile.passport ?? "unknown"}, home_airport=${profile.home_airport ?? "unknown"}.
Decide the intent: travel, movies, or unclear. If unclear, ask ONE short question and offer quick replies.
Travel: convert vague wishes to filters. "warm in winter" -> months [12,1,2], min_avg_high_c 24 (beach: 27).
"no visa" -> visa_pref "strict_no_visa"; "visa on arrival is ok" -> "allow_easy". If passport unknown and user cares about visas, ask for it.
Movies: map moods ("something light", "date night", "with kids") to mood tags / family_safe.
Always call a tool before recommending. Keep your text to 1-2 sentences; the cards carry the details.
Never invent prices or visa rules - only use tool results. Visa info is demo data; remind users to verify before booking.`;

const TOOLS = [
  { name: "search_destinations", description: "Find holiday destinations by climate, visa, budget and style.",
    input_schema: { type: "object", properties: {
      months: { type: "array", items: { type: "integer" } },
      passport: { type: "string", enum: ["TR", "AZ"] },
      visa_pref: { type: "string", enum: ["strict_no_visa", "allow_easy", "any"] },
      min_avg_high_c: { type: "number" }, max_avg_high_c: { type: "number" },
      tags: { type: "array", items: { type: "string", enum: ["beach","city","culture","nightlife","diving","honeymoon","family","budget","luxury","ski","nature","food","shopping","all_inclusive","halal_friendly","surf","history"] } },
      max_budget_level: { type: "integer", enum: [1, 2, 3] },
      origin: { type: "string" }, depart_date: { type: "string" }, avoid_rainy: { type: "boolean" },
    }, required: ["months"] } },
  { name: "search_flights", description: "Flight offers for one route and date.",
    input_schema: { type: "object", properties: {
      origin: { type: "string" }, destination: { type: "string" }, depart_date: { type: "string" },
      return_date: { type: "string" }, adults: { type: "integer" }, direct_only: { type: "boolean" },
      cabin: { type: "string", enum: ["economy", "business"] }, max_price_usd: { type: "number" },
    }, required: ["origin", "destination", "depart_date"] } },
  { name: "search_movies", description: "Recommend movies by genre, mood, recency, language.",
    input_schema: { type: "object", properties: {
      genres: { type: "array", items: { type: "string" } }, moods: { type: "array", items: { type: "string" } },
      status: { type: "array", items: { type: "string", enum: ["in_theaters","streaming","classic","coming_soon"] } },
      min_year: { type: "integer" }, max_runtime_min: { type: "integer" },
      languages: { type: "array", items: { type: "string" } }, family_safe: { type: "boolean" }, similar_to: { type: "string" },
    } } },
  { name: "ask_user", description: "Ask a clarifying question with quick-reply chips.",
    input_schema: { type: "object", properties: { question: { type: "string" }, options: { type: "array", items: { type: "string" } } }, required: ["question","options"] } },
];

function runTool(name: string, input: any) {
  if (name === "search_destinations") return { type: "destination_carousel", title: "Destinations for you", items: searchDestinations(input) };
  if (name === "search_flights") return { type: "flight_list", title: "Flights", items: searchFlights(input) };
  if (name === "search_movies") {
    const r = searchMovies(input);
    return { type: "movie_carousel", title: "Picked for you", items: r.map(x => x.movie),
             reason_by_id: Object.fromEntries(r.map(x => [x.movie.id, x.why])) };
  }
  return null;
}

Deno.serve(async (req) => {
  const { messages, profile = {} } = await req.json();
  const blocks: any[] = [];
  let intent = "unclear";
  let convo = [...messages];

  for (let step = 0; step < 4; step++) {           // small tool-use loop
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "x-api-key": Deno.env.get("ANTHROPIC_API_KEY")!, "anthropic-version": "2023-06-01", "content-type": "application/json" },
      body: JSON.stringify({ model: MODEL, max_tokens: 1024, system: SYSTEM(profile), tools: TOOLS, messages: convo }),
    });
    const data = await res.json();
    const toolUses = data.content.filter((c: any) => c.type === "tool_use");
    data.content.filter((c: any) => c.type === "text").forEach((c: any) => blocks.push({ type: "text", text: c.text }));
    if (!toolUses.length) break;

    const results = toolUses.map((t: any) => {
      if (t.name === "ask_user") {
        blocks.push({ type: "text", text: t.input.question }, { type: "quick_replies", options: t.input.options });
        return { type: "tool_result", tool_use_id: t.id, content: "asked" };
      }
      intent = t.name === "search_movies" ? "movies" : "travel";
      const block = runTool(t.name, t.input);
      if (block) blocks.push(block);
      // Give the model a compact summary, not the full JSON, to save tokens.
      const summary = block ? JSON.stringify((block as any).items.slice(0, 8).map((i: any) => i.title ?? i.city ?? `${i.carrier} $${i.price_usd}`)) : "[]";
      return { type: "tool_result", tool_use_id: t.id, content: summary };
    });
    if (toolUses.some((t: any) => t.name === "ask_user")) break;
    convo = [...convo, { role: "assistant", content: data.content }, { role: "user", content: results }];
  }
  return new Response(JSON.stringify({ intent, blocks }), { headers: { "content-type": "application/json" } });
});
