# Travel & Movie Chatbot — MVP (mock data)

A chat assistant that detects whether the user wants a **trip** or a **movie**, turns vague wishes
("somewhere warm in winter, no visa") into structured filters, and answers with **Rufus-style cards**
(carousels, badges, quick-reply chips) instead of plain text.

> All data here is **mock/demo**. Visa statuses were compiled from public sources on 2026-10-27 and must be
> verified against official sources before real users rely on them.

## How it works

```
User message
   │
   ▼
Frontend (React, Lovable) ──POST {messages, profile}──▶ Edge Function /chat
                                                          │
                                         LLM + tools ◀────┤ system prompt: intent + filter rules
                                                          │
                     ┌──────────────────┬─────────────────┼───────────────────┐
                     ▼                  ▼                 ▼                   ▼
          search_destinations     search_flights     search_movies        ask_user
          (climate+visa+budget)   (mock prices,      (genre+mood+         (clarify, chips)
                │                  any date)          recency)
                ▼
          visa logic layer (passport → tier → filter)
                                                          │
Frontend ◀──────────── { intent, blocks: [text, carousel, chips] } ◀──────┘
renders each block as a card component
```

Key idea: **the LLM never invents data.** It only picks filters and calls tools; cards are built from tool
results. The response is a list of typed *blocks*, so the frontend just maps block type → component.

## Project structure

```
travel-movie-bot/
├─ scripts/
│  └─ build_mock_data.py         # single source of truth for all mock data → src/data/*.json
├─ src/
│  ├─ data/                      # generated JSON (don't hand-edit; edit the script)
│  │  ├─ destinations.json       # 40 destinations: monthly climate, tags, budget, visa per passport
│  │  ├─ routes.json             # origin×destination: distance, direct?, carriers, base price
│  │  ├─ origins.json            # IST, SAW, ESB, GYD
│  │  ├─ movies.json             # 42 movies, TMDB-shaped (2026 hits, recent, classics, Turkish)
│  │  └─ visa_meta.json          # tiers, supported passports, verified_at, disclaimer
│  ├─ types/index.ts             # Destination, Movie, FlightOffer, ChatBlock, ChatResponse
│  ├─ lib/
│  │  ├─ visa.ts                 # "no visa required" logic layer
│  │  └─ providers/              # ← the ONLY place that changes when going mock → real
│  │     ├─ destinations.mock.ts # climate/visa/budget/tag filter + ranking + "why" reasons
│  │     ├─ flights.mock.ts      # deterministic price generator for any date
│  │     └─ movies.mock.ts       # genre/mood/similar-to search
│  ├─ components/                # (build in Lovable)
│  │  ├─ chat/  ChatWindow, MessageList, Composer, QuickReplies, TypingIndicator
│  │  └─ cards/ MovieCard, MovieCarousel, DestinationCard, DestinationCarousel,
│  │            FlightCard, VisaBadge, PriceTag, CardSkeleton
│  └─ pages/ Index.tsx           # chat page + small profile bar (passport, home airport)
└─ supabase/functions/
   ├─ chat/index.ts              # LLM orchestration + tool loop (API key in secrets)
   └─ _shared/                   # copy of src/lib + src/data for the function runtime
```

Regenerate data: `python scripts/build_mock_data.py`

## The visa logic layer

Each destination stores a status **per passport** (`TR`, `AZ`). Statuses map to three tiers:

| Tier      | Statuses                                              | Shown when user says…            |
|-----------|-------------------------------------------------------|----------------------------------|
| `no_visa` | `domestic`, `visa_free`, `visa_on_arrival_free`       | "no visa" (default strict mode)  |
| `easy`    | `visa_on_arrival`, `e_visa`, `eta`                    | "visa on arrival / online is ok" |
| `hard`    | `visa_required`                                       | never, unless user asks for any  |

Passport is asked once and stored in the profile, never guessed. Adding a passport = adding one key per
destination. For production, replace the static table with a visa API (e.g. Sherpa, IATA Timatic) and keep the
same `visaTier()` interface.

## Translating vague requests into filters (examples for the system prompt)

| User says                        | Filters                                                        |
|----------------------------------|----------------------------------------------------------------|
| "warm place in winter"           | `months:[12,1,2], min_avg_high_c:24`                           |
| "beach holiday, swimming"        | `min_avg_high_c:27, tags:[beach]`                              |
| "New Year trip, no visa, Turkish passport" | `months:[12,1], passport:TR, visa_pref:strict_no_visa` |
| "cheap"                          | `max_budget_level:1`                                           |
| "honeymoon"                      | `tags:[honeymoon]`                                             |
| "skiing"                         | `max_avg_high_c:5, tags:[ski]`                                 |
| "movie with kids"                | `family_safe:true, moods:[family]`                             |
| "something like Interstellar"    | `similar_to:"Interstellar"`                                    |
| "what's new in cinema"           | `status:[in_theaters]`                                         |

## Mock → real migration

| Mock provider            | Real replacement                                   | Notes |
|--------------------------|----------------------------------------------------|-------|
| `movies.mock.ts`         | TMDB `/discover/movie`, `/movie/{id}/watch/providers` | fill `tmdb_id`, `poster_path` |
| `flights.mock.ts`        | a self-serve flight API (Amadeus Self-Service closed July 2026) | evaluate options |
| `destinations.mock.ts`   | keep curated list + real climate API if needed     | curation is a feature |
| `visa.ts` table          | visa data API                                      | same tier interface |

## Building in Lovable (suggested order)

1. Create the project, paste `src/types`, `src/data`, `src/lib` into it.
2. Prompt Lovable to build the chat page and card components from the `ChatBlock` type.
3. Enable Supabase, add `chat` edge function, set `ANTHROPIC_API_KEY` (or your LLM key) as a secret.
4. Test the demo scripts below, then share the hosted link with the client.

## Demo scripts for the client meeting

- "I want to go somewhere warm for New Year, I have a Turkish passport and don't want to deal with visas."
- "Same, but I'm from Azerbaijan, flying from Baku, budget is limited."
- "Show flights to Dubai on Dec 27, back Jan 3."
- "Recommend a movie for tonight, something like Interstellar."
- "What can I watch with my kids this weekend?"
- "Something for the weekend" → bot should ask: trip or movie?
