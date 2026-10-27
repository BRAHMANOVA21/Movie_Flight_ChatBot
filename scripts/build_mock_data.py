
import json, math, os

OUT = os.path.join(os.path.dirname(__file__), "..", "src", "data")
os.makedirs(OUT, exist_ok=True)
VERIFIED_AT = "2026-10-27"

# ---------------------------------------------------------------------------
# ORIGIN AIRPORTS (where our users fly from)
# ---------------------------------------------------------------------------
ORIGINS = [
    {"iata": "IST", "city": "Istanbul", "country": "TR", "lat": 41.26, "lon": 28.74},
    {"iata": "SAW", "city": "Istanbul (Sabiha Gokcen)", "country": "TR", "lat": 40.90, "lon": 29.31},
    {"iata": "ESB", "city": "Ankara", "country": "TR", "lat": 40.13, "lon": 32.99},
    {"iata": "GYD", "city": "Baku", "country": "AZ", "lat": 40.47, "lon": 50.05},
]

# ---------------------------------------------------------------------------
# VISA STATUS VOCABULARY  (the "logic layer" keys off these)
# ---------------------------------------------------------------------------
# no_visa tier  -> what "no visa required" means by default
#   domestic, visa_free, visa_on_arrival_free
# easy tier     -> shown with a badge, included if user allows "easy visa"
#   visa_on_arrival (paid), e_visa, eta (electronic travel authorisation)
# hard tier     -> visa_required (embassy / consulate)
VISA_TIERS = {
    "domestic": "no_visa",
    "visa_free": "no_visa",
    "visa_on_arrival_free": "no_visa",
    "visa_on_arrival": "easy",
    "eta": "easy",
    "e_visa": "easy",
    "visa_required": "hard",
}

# ---------------------------------------------------------------------------
# DESTINATIONS
# climate = avg daily high deg C, Jan..Dec
# visa = {passport: (status, max_stay_days|None, note|None)}
# ---------------------------------------------------------------------------
def d(id, city, country, cc, iata, lat, lon, region, climate, tags, budget,
      daily, rainy, best, blurb, tr, az, direct_from):
    return dict(id=id, city=city, country=country, country_code=cc,
                airport_iata=iata, lat=lat, lon=lon, region=region,
                climate_avg_high_c=climate, tags=tags, budget_level=budget,
                est_daily_cost_usd=daily, rainy_months=rainy, best_months=best,
                blurb=blurb, visa={"TR": tr, "AZ": az}, direct_from=direct_from,
                image_query=f"{city} {country} travel")

V = lambda s, days=None, note=None: {"status": s, "max_stay_days": days, "note": note}

DESTINATIONS = [
    # ---------------- WARM IN WINTER: beach ----------------
    d("phuket", "Phuket", "Thailand", "TH", "HKT", 7.9, 98.3, "Southeast Asia",
      [32,33,34,34,32,31,31,31,30,31,31,31], ["beach","nightlife","diving","honeymoon"], 2, 70,
      [5,6,7,8,9,10], [12,1,2,3], "Andaman Sea beaches, island hopping to Phi Phi, lively nightlife.",
      V("visa_free", 30, "Thailand revised exemption rules in 2026; re-check stay length."),
      V("e_visa", 60), ["IST"]),
    d("bangkok", "Bangkok", "Thailand", "TH", "BKK", 13.7, 100.5, "Southeast Asia",
      [32,33,34,35,34,33,32,32,32,32,32,31], ["city","food","culture","nightlife","budget"], 1, 55,
      [5,6,7,8,9,10], [11,12,1,2], "Street food capital, temples, rooftop bars, cheap and energetic.",
      V("visa_free", 30, "Re-check 2026 Thai exemption rules."), V("e_visa", 60), ["IST"]),
    d("langkawi", "Langkawi", "Malaysia", "MY", "LGK", 6.3, 99.8, "Southeast Asia",
      [32,33,33,33,32,32,31,31,31,31,31,31], ["beach","nature","family","budget"], 1, 50,
      [9,10,11], [12,1,2,3], "Duty-free island with rainforest, cable car and calm beaches.",
      V("visa_free", 90), V("visa_free", 30), []),
    d("kuala_lumpur", "Kuala Lumpur", "Malaysia", "MY", "KUL", 3.1, 101.7, "Southeast Asia",
      [32,33,33,33,33,33,32,32,32,32,32,32], ["city","food","shopping","family","halal_friendly"], 1, 55,
      [4,10,11], [12,1,2,6,7], "Petronas Towers, malls, halal food everywhere, easy hub for islands.",
      V("visa_free", 90), V("visa_free", 30), ["IST"]),
    d("male", "Maldives", "Maldives", "MV", "MLE", 4.2, 73.5, "Indian Ocean",
      [30,31,31,32,31,31,30,30,30,30,30,30], ["beach","luxury","honeymoon","diving"], 3, 350,
      [5,6,7,8,9,10], [12,1,2,3,4], "Overwater villas and reef snorkelling. Guesthouse islands for lower budgets.",
      V("visa_on_arrival_free", 30, "Free 30-day permit on arrival for all nationalities."),
      V("visa_on_arrival_free", 30, "Free 30-day permit on arrival for all nationalities."),
      ["IST","GYD"]),
    d("sharm", "Sharm El Sheikh", "Egypt", "EG", "SSH", 27.9, 34.3, "Red Sea",
      [22,23,25,29,33,36,37,37,35,31,27,23], ["beach","diving","family","budget","all_inclusive"], 1, 60,
      [], [10,11,3,4], "Red Sea reefs and all-inclusive resorts; mild-warm in Dec-Feb, sea ~22C.",
      V("visa_on_arrival", 30, "Paid VOA; Sinai-only stamp may be free - verify."),
      V("visa_on_arrival", 30), ["IST"]),
    d("hurghada", "Hurghada", "Egypt", "EG", "HRG", 27.2, 33.8, "Red Sea",
      [21,22,24,28,31,33,34,35,33,30,26,23], ["beach","diving","family","budget","all_inclusive"], 1, 55,
      [], [10,11,3,4], "Budget all-inclusive beach holidays and snorkelling trips.",
      V("visa_on_arrival", 30), V("visa_on_arrival", 30), ["IST","SAW"]),
    d("colombo", "Colombo & South Coast", "Sri Lanka", "LK", "CMB", 6.9, 79.9, "South Asia",
      [31,31,32,32,31,30,30,30,30,30,30,30], ["beach","culture","nature","surf","budget"], 1, 45,
      [5,6,10,11], [12,1,2,3], "Tea hills, safaris and the Galle/Mirissa coast - best in winter.",
      V("eta", 30), V("eta", 30), ["IST"]),
    d("bali", "Bali", "Indonesia", "ID", "DPS", -8.7, 115.2, "Southeast Asia",
      [31,31,31,32,31,30,29,30,30,31,32,31], ["beach","culture","surf","honeymoon","nature"], 2, 65,
      [12,1,2,3], [5,6,7,8,9], "Rice terraces, temples and surf. Note: Dec-Mar is rainy season.",
      V("visa_on_arrival", 30, "Plus Bali tourist levy."), V("visa_on_arrival", 30, "Plus Bali tourist levy."), ["IST"]),
    d("phu_quoc", "Phu Quoc", "Vietnam", "VN", "PQC", 10.2, 103.97, "Southeast Asia",
      [30,31,32,33,32,31,30,30,30,30,30,30], ["beach","budget","family"], 1, 50,
      [6,7,8,9,10], [11,12,1,2,3], "Quiet white-sand beaches and sunsets; dry season matches European winter.",
      V("e_visa", 90), V("e_visa", 90), []),
    d("mauritius", "Mauritius", "Mauritius", "MU", "MRU", -20.4, 57.7, "Indian Ocean",
      [30,30,30,29,27,26,25,25,26,27,28,29], ["beach","honeymoon","luxury","nature"], 3, 180,
      [1,2,3], [10,11,12,4,5], "Lagoons, mountains and resorts; southern-hemisphere summer in Dec-Feb.",
      V("visa_free", 90), V("visa_on_arrival_free", 60), []),
    d("seychelles", "Mahe", "Seychelles", "SC", "SEZ", -4.7, 55.5, "Indian Ocean",
      [30,30,31,31,30,29,28,28,29,29,30,30], ["beach","luxury","honeymoon","nature"], 3, 250,
      [12,1], [4,5,10,11], "Granite-boulder beaches. Online Travel Authorisation required for everyone.",
      V("visa_free", 90, "Visitor permit on arrival; online Travel Authorisation required."),
      V("visa_free", 90, "Visitor permit on arrival; online Travel Authorisation required."), ["IST"]),
    d("zanzibar", "Zanzibar", "Tanzania", "TZ", "ZNZ", -6.2, 39.2, "East Africa",
      [32,32,32,30,29,28,28,28,29,30,31,32], ["beach","culture","diving","budget"], 2, 70,
      [4,5,11], [12,1,2,6,7,8], "Spice-island old town (Stone Town) and turquoise east-coast beaches.",
      V("e_visa", 90), V("e_visa", 90), ["IST"]),
    d("punta_cana", "Punta Cana", "Dominican Republic", "DO", "PUJ", 18.6, -68.4, "Caribbean",
      [28,28,29,29,30,31,31,31,31,31,30,29], ["beach","all_inclusive","family","honeymoon"], 2, 120,
      [9,10], [12,1,2,3,4], "Caribbean all-inclusive resorts; long-haul with a connection.",
      V("visa_free", 30),
      V("visa_required", None, "Waiver agreement signed Sep 2026, not yet in force."), []),
    d("cancun", "Cancun", "Mexico", "MX", "CUN", 21.2, -86.8, "Caribbean",
      [28,29,30,31,32,33,33,33,32,31,29,28], ["beach","nightlife","culture","diving"], 2, 110,
      [9,10], [12,1,2,3,4], "Caribbean beaches plus Mayan ruins and cenotes.",
      V("eta", 180, "Electronic authorisation (SAE) route; otherwise visa - verify."),
      V("visa_required"), ["IST"]),
    d("havana", "Havana & Varadero", "Cuba", "CU", "HAV", 23.1, -82.4, "Caribbean",
      [26,27,28,29,30,31,32,32,31,29,28,26], ["beach","culture","music"], 2, 80,
      [6,9,10], [12,1,2,3], "Vintage cars, salsa and Varadero beach. Tourist card needed by all.",
      V("e_visa", 30, "Tourist card / e-visa - verify."), V("e_visa", 30), []),
    d("rio", "Rio de Janeiro", "Brazil", "BR", "GIG", -22.9, -43.2, "South America",
      [30,31,30,28,26,25,25,26,25,26,28,29], ["beach","city","nightlife","culture"], 2, 90,
      [12,1,2,3], [12,1,2,3], "Copacabana, Sugarloaf and Carnival (Feb) - peak summer in winter months.",
      V("visa_free", 90), V("visa_required"), ["IST"]),
    d("cartagena", "Cartagena", "Colombia", "CO", "CTG", 10.4, -75.5, "South America",
      [31,31,31,32,32,32,32,32,32,31,31,31], ["beach","culture","city","nightlife"], 2, 75,
      [5,9,10,11], [12,1,2,3], "Colourful walled old town and Rosario islands.",
      V("visa_free", 90), V("visa_free", 90), []),
    d("boracay", "Boracay", "Philippines", "PH", "MPH", 11.9, 121.9, "Southeast Asia",
      [29,30,31,32,32,31,30,30,30,30,30,29], ["beach","nightlife","diving"], 2, 65,
      [6,7,8,9,10], [12,1,2,3,4,5], "White Beach and island-hopping; dry season Dec-May.",
      V("visa_free", 30), V("visa_required"), []),
    d("goa", "Goa", "India", "IN", "GOX", 15.4, 73.8, "South Asia",
      [32,32,32,33,33,30,29,29,30,32,33,33], ["beach","nightlife","budget","culture"], 1, 40,
      [6,7,8,9], [11,12,1,2], "Beach shacks, Portuguese churches and parties; dry and sunny in winter.",
      V("e_visa", 30), V("e_visa", 30), []),
    d("cape_town", "Cape Town", "South Africa", "ZA", "CPT", -33.9, 18.4, "Southern Africa",
      [26,27,25,23,20,18,18,18,19,21,23,25], ["city","nature","beach","wine","food"], 2, 85,
      [6,7,8], [12,1,2,3], "Table Mountain, wine country and penguins - summer in Dec-Feb.",
      V("visa_free", 30), V("visa_required"), ["IST"]),
    d("mombasa", "Mombasa & Diani", "Kenya", "KE", "MBA", -4.0, 39.6, "East Africa",
      [32,33,33,32,30,29,28,28,29,30,31,32], ["beach","safari","nature"], 2, 80,
      [4,5,11], [12,1,2,7,8], "Indian Ocean beaches easily combined with a safari.",
      V("eta", 90, "Kenya eTA required for all visitors."), V("eta", 90, "Kenya eTA required for all visitors."), []),
    # ---------------- WARM IN WINTER: Gulf / city sun ----------------
    d("dubai", "Dubai", "United Arab Emirates", "AE", "DXB", 25.2, 55.3, "Middle East",
      [24,25,28,33,37,39,41,41,39,35,30,26], ["city","beach","shopping","luxury","family","halal_friendly"], 3, 160,
      [], [11,12,1,2,3], "Winter is peak season: 24-28C, beaches, desert safari, malls.",
      V("e_visa", 30, "Visa on arrival possible if holding valid US/UK/Schengen visa."),
      V("visa_free", 90), ["IST","SAW","GYD"]),
    d("doha", "Doha", "Qatar", "QA", "DOH", 25.3, 51.5, "Middle East",
      [22,23,27,32,38,41,42,41,39,35,29,24], ["city","culture","family","halal_friendly"], 3, 130,
      [], [11,12,1,2,3], "Museums, souqs and desert trips; pleasant 22-27C in winter.",
      V("visa_free", 30), V("visa_free", 30), ["IST","GYD"]),
    d("muscat", "Muscat", "Oman", "OM", "MCT", 23.6, 58.4, "Middle East",
      [25,26,29,34,39,40,38,36,35,34,30,27], ["culture","nature","beach","halal_friendly"], 2, 100,
      [], [11,12,1,2,3], "Wadis, forts and quiet beaches; authentic Arabia without crowds.",
      V("visa_free", 14), V("visa_free", 14), ["IST"]),
    d("jeddah", "Jeddah & Red Sea", "Saudi Arabia", "SA", "JED", 21.5, 39.2, "Middle East",
      [29,30,31,34,36,38,38,38,37,35,32,30], ["culture","beach","halal_friendly","religious"], 2, 110,
      [], [11,12,1,2], "Historic Al-Balad and Red Sea coast; gateway for Umrah.",
      V("e_visa", 90), V("e_visa", 90), ["IST","SAW","GYD"]),
    d("aqaba", "Aqaba & Petra", "Jordan", "JO", "AQJ", 29.5, 35.0, "Middle East",
      [21,23,27,31,35,38,39,39,37,33,27,22], ["beach","culture","diving","history"], 2, 80,
      [], [10,11,3,4], "Red Sea diving plus a day trip to Petra and Wadi Rum.",
      V("visa_free", 30), V("visa_on_arrival", 30), ["IST"]),
    d("marrakech", "Marrakech", "Morocco", "MA", "RAK", 31.6, -8.0, "North Africa",
      [18,20,23,25,29,33,37,37,32,27,22,19], ["culture","city","food","shopping"], 1, 60,
      [], [3,4,10,11], "Medina, riads and souks; sunny but only mild (18-20C) in winter.",
      V("visa_free", 90), V("visa_free", 90), []),
    d("agadir", "Agadir", "Morocco", "MA", "AGA", 30.4, -9.6, "North Africa",
      [21,22,23,23,24,25,26,27,27,26,24,22], ["beach","surf","budget","family"], 1, 55,
      [], [10,11,3,4,5], "Atlantic surf town with near-constant sunshine and mild winters.",
      V("visa_free", 90), V("visa_free", 90), []),
    d("singapore", "Singapore", "Singapore", "SG", "SIN", 1.35, 103.99, "Southeast Asia",
      [30,31,32,32,32,31,31,31,31,31,31,30], ["city","food","family","shopping"], 3, 150,
      [11,12,1], [2,3,4,7,8], "Gardens by the Bay, hawker food, Sentosa beaches; great family stopover.",
      V("visa_free", 30), V("visa_required"), ["IST"]),
    d("antalya", "Antalya", "Turkiye", "TR", "AYT", 36.9, 30.7, "Mediterranean",
      [15,16,18,21,26,31,34,34,31,26,21,16], ["beach","history","family","all_inclusive","budget"], 1, 60,
      [12,1,2], [5,6,9,10], "Riviera resorts; in winter it's mild (15-16C) - good for city/history, not swimming.",
      V("domestic"), V("visa_free", 90), ["GYD"]),
    # ---------------- NOT WARM: for contrast / other intents ----------------
    d("tbilisi", "Tbilisi", "Georgia", "GE", "TBS", 41.7, 44.8, "Caucasus",
      [7,9,14,19,24,29,32,32,27,20,13,8], ["city","food","wine","culture","budget"], 1, 50,
      [], [5,6,9,10], "Sulphur baths, wine bars and old-town balconies.",
      V("visa_free", 365), V("visa_free", 365), ["IST","SAW","GYD"]),
    d("gudauri", "Gudauri", "Georgia", "GE", "TBS", 42.48, 44.48, "Caucasus",
      [-4,-3,1,5,10,14,17,17,13,8,2,-2], ["ski","nature","winter_sports","budget"], 1, 70,
      [], [12,1,2,3], "Affordable freeride and ski resort ~2h from Tbilisi.",
      V("visa_free", 365), V("visa_free", 365), ["IST","SAW","GYD"]),
    d("shahdag", "Shahdag", "Azerbaijan", "AZ", "GYD", 41.3, 48.1, "Caucasus",
      [-3,-2,2,8,13,17,20,20,16,10,4,-1], ["ski","family","winter_sports"], 2, 90,
      [], [12,1,2,3], "Modern ski resort in the Greater Caucasus, ~3.5h from Baku.",
      V("visa_free", 90), V("domestic"), ["IST","SAW"]),
    d("palandoken", "Erzurum (Palandoken)", "Turkiye", "TR", "ERZ", 39.9, 41.3, "Eastern Anatolia",
      [-5,-3,2,11,17,22,27,28,23,15,6,-2], ["ski","winter_sports","budget"], 1, 55,
      [], [12,1,2,3], "Long ski season and cheap lift passes in eastern Turkiye.",
      V("domestic"), V("visa_free", 90), ["IST","SAW","ESB"]),
    d("tokyo", "Tokyo", "Japan", "JP", "HND", 35.6, 139.7, "East Asia",
      [10,10,14,19,23,26,30,31,27,22,17,12], ["city","food","culture","shopping"], 3, 150,
      [6,9], [3,4,10,11], "Neon, sushi and cherry blossoms in spring. Cold but dry in winter.",
      V("visa_free", 90), V("visa_required"), ["IST"]),
    d("belgrade", "Belgrade", "Serbia", "RS", "BEG", 44.8, 20.3, "Balkans",
      [4,7,12,18,23,27,29,30,24,18,11,5], ["city","nightlife","budget","food"], 1, 50,
      [], [5,6,9], "River-barge nightlife and big portions; cheap European city break.",
      V("visa_free", 90), V("visa_free", 30), ["IST","SAW","GYD"]),
    d("samarkand", "Samarkand", "Uzbekistan", "UZ", "SKD", 39.6, 66.9, "Central Asia",
      [7,9,15,21,27,32,34,33,28,21,14,9], ["culture","history","budget","halal_friendly"], 1, 45,
      [], [4,5,9,10], "Registan and Silk Road architecture.",
      V("visa_free", 30), V("visa_free", 60), ["IST"]),
    d("istanbul", "Istanbul", "Turkiye", "TR", "IST", 41.0, 28.98, "Mediterranean",
      [9,9,12,16,21,26,28,29,25,20,15,11], ["city","food","history","shopping"], 2, 90,
      [12,1], [4,5,9,10], "Bosphorus, bazaars and two continents in one city.",
      V("domestic"), V("visa_free", 90), ["GYD"]),
    d("baku", "Baku", "Azerbaijan", "AZ", "GYD", 40.4, 49.9, "Caucasus",
      [7,7,10,16,22,27,30,30,26,20,13,9], ["city","food","history"], 2, 70,
      [], [5,6,9,10], "Old City, Flame Towers and the Caspian boulevard.",
      V("visa_free", 90), V("domestic"), ["IST","SAW","ESB"]),
]

# ---------------------------------------------------------------------------
# ROUTES: origin x destination with distance and directness, used by the mock
# flight provider to generate deterministic prices for ANY date.
# ---------------------------------------------------------------------------
def haversine(a, b):
    R = 6371
    la1, lo1, la2, lo2 = map(math.radians, [a["lat"], a["lon"], b["lat"], b["lon"]])
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return round(2*R*math.asin(math.sqrt(h)))

AIRLINES = {
    "TR_direct": ["Turkish Airlines", "Pegasus", "AJet"],
    "AZ_direct": ["AZAL", "Turkish Airlines"],
    "via_gulf": ["Emirates (via DXB)", "Qatar Airways (via DOH)", "flydubai (via DXB)"],
    "via_ist": ["Turkish Airlines (via IST)"],
}

routes = []
for o in ORIGINS:
    for dest in DESTINATIONS:
        if dest["airport_iata"] == o["iata"] or dest["country_code"] == o["country"] and dest["airport_iata"] in ("GYD",):
            continue
        dist = haversine(o, dest)
        if dist < 150:
            continue
        direct = o["iata"] in dest["direct_from"]
        if direct:
            carriers = AIRLINES["TR_direct"] if o["country"] == "TR" else AIRLINES["AZ_direct"]
            if dist > 3000 and o["country"] == "TR":
                carriers = ["Turkish Airlines"]
        else:
            carriers = AIRLINES["via_ist"] + AIRLINES["via_gulf"] if o["country"] == "AZ" else AIRLINES["via_gulf"] + ["Turkish Airlines (via IST)"]
        routes.append({
            "origin": o["iata"], "destination": dest["airport_iata"], "destination_id": dest["id"],
            "distance_km": dist, "direct_available": direct, "carriers": carriers,
            "base_price_usd": round(50 + dist * 0.085 * (1.15 if direct else 1.0)),
            "base_duration_min": round(dist / 780 * 60 + 35 + (0 if direct else 150)),
        })

# ---------------------------------------------------------------------------
# MOVIES  (TMDB-shaped; tmdb_id left null -> fill with a sync script later)
# ---------------------------------------------------------------------------
G = {  # TMDB genre ids
    "Action": 28, "Adventure": 12, "Animation": 16, "Comedy": 35, "Crime": 80,
    "Documentary": 99, "Drama": 18, "Family": 10751, "Fantasy": 14, "History": 36,
    "Horror": 27, "Music": 10402, "Mystery": 9648, "Romance": 10749,
    "Science Fiction": 878, "Thriller": 53, "War": 10752,
}

def m(slug, title, year, date, genres, runtime, rating, overview, moods, status,
      providers=None, director=None, cast=None, box_office=None, lang="en", age="PG-13",
      popularity=50):
    return {
        "id": slug, "tmdb_id": None, "title": title, "original_language": lang,
        "release_date": date, "year": year,
        "genres": [{"id": G[g], "name": g} for g in genres],
        "runtime_min": runtime, "vote_average": rating, "age_rating": age,
        "overview": overview, "mood_tags": moods, "director": director, "cast": cast or [],
        "status": status,  # in_theaters | streaming | classic | coming_soon
        "watch_providers_mock": providers or [],
        "box_office_worldwide_usd": box_office, "popularity": popularity,
        "poster_path": None, "backdrop_path": None,
        "trailer_query": f"{title} {year} official trailer",
    }

MOVIES = [
    # ---- 2026 big releases (box office from public reporting, Oct 2026) ----
    m("spiderman-bnd", "Spider-Man: Brand New Day", 2026, "2026-07-31", ["Action","Adventure","Science Fiction"], 135, 8.1,
      "A Peter Parker the world has forgotten tries to rebuild a life in New York while a new threat rises.",
      ["exciting","fun","friends"], "in_theaters", [], None, ["Tom Holland","Zendaya"], 2506881993, popularity=99),
    m("the-odyssey", "The Odyssey", 2026, "2026-07-17", ["Adventure","Fantasy","Drama"], 165, 8.4,
      "Christopher Nolan's epic of Odysseus' long, perilous voyage home after the Trojan War.",
      ["epic","thoughtful","visually_stunning"], "in_theaters", [], "Christopher Nolan", ["Matt Damon"], 1770810884, popularity=97),
    m("toy-story-5", "Toy Story 5", 2026, "2026-06-19", ["Animation","Family","Comedy","Adventure"], 100, 7.8,
      "Woody, Buzz and the gang face a new rival for a kid's attention: a shiny tablet.",
      ["family","feel_good","funny"], "streaming", ["Disney+"], None, None, 1148032149, "en", "G", 92),
    m("michael", "Michael", 2026, "2026-04-24", ["Music","Drama","History"], 130, 7.4,
      "Biopic tracing Michael Jackson's rise from the Jackson 5 to global superstardom.",
      ["music","inspiring","nostalgic"], "streaming", ["Prime Video"], "Antoine Fuqua", ["Jaafar Jackson"], None, popularity=90),
    m("mario-galaxy", "The Super Mario Galaxy Movie", 2026, "2026-04-03", ["Animation","Family","Adventure","Comedy"], 98, 7.1,
      "Mario and friends blast off on a cosmic adventure across planets and galaxies.",
      ["family","fun","colorful"], "streaming", ["Netflix"], None, None, None, "en", "PG", 88),
    m("project-hail-mary", "Project Hail Mary", 2026, "2026-03-20", ["Science Fiction","Adventure","Drama"], 156, 8.3,
      "An astronaut wakes with no memory aboard a ship on a mission to save the Sun - and finds an unexpected ally.",
      ["thoughtful","feel_good","space"], "streaming", ["Prime Video"], "Phil Lord & Chris Miller", ["Ryan Gosling","Sandra Hüller"], None, popularity=91),
    m("devil-wears-prada-2", "The Devil Wears Prada 2", 2026, "2026-05-01", ["Comedy","Drama"], 115, 6.9,
      "Miranda Priestly and Andy Sachs cross paths again as the magazine world fights to survive.",
      ["funny","stylish","date_night"], "streaming", ["Disney+"], "David Frankel", ["Meryl Streep","Anne Hathaway","Emily Blunt"], 664100000, popularity=84),
    m("minions-monsters", "Minions & Monsters", 2026, "2026-07-01", ["Animation","Family","Comedy"], 92, 6.8,
      "The Minions stumble into the world of classic monster movies.",
      ["family","funny","silly"], "in_theaters", [], None, None, None, "en", "PG", 80),
    m("hoppers", "Hoppers", 2026, "2026-03-06", ["Animation","Family","Science Fiction","Comedy"], 104, 7.6,
      "A girl transfers her mind into a robotic beaver to get close to the animals she wants to protect.",
      ["family","feel_good","funny"], "streaming", ["Disney+"], None, None, 388400000, "en", "PG", 78),
    m("wuthering-heights-2026", "Wuthering Heights", 2026, "2026-02-13", ["Romance","Drama"], 135, 6.6,
      "A lush, intense new take on Emily Brontë's tale of obsessive love on the Yorkshire moors.",
      ["romantic","dark","date_night"], "streaming", ["HBO Max"], "Emerald Fennell", ["Margot Robbie","Jacob Elordi"], 241600000, "en", "R", 76),
    m("obsession-2026", "Obsession", 2026, None, ["Horror","Thriller"], 95, 7.2,
      "A micro-budget horror hit that became one of the year's biggest surprises.",
      ["scary","tense"], "streaming", ["Netflix"], None, None, 519300000, "en", "R", 82),
    m("resident-evil-2026", "Resident Evil", 2026, "2026-09-18", ["Horror","Action"], 110, 7.5,
      "A fresh, standalone take on the survival-horror game franchise.",
      ["scary","exciting","friends"], "in_theaters", [], "Zach Cregger", None, None, "en", "R", 86),
    m("verity", "Verity", 2026, "2026-10-02", ["Thriller","Mystery","Romance"], 112, 6.8,
      "A struggling writer hired to finish a bestselling author's series uncovers a chilling manuscript.",
      ["tense","twisty","date_night"], "in_theaters", [], None, ["Anne Hathaway"], None, "en", "R", 85),
    m("practical-magic-2", "Practical Magic 2", 2026, "2026-09-18", ["Fantasy","Comedy","Romance"], 110, 7.0,
      "The Owens sisters return to face a new generation of family magic and curses.",
      ["cozy","feel_good","nostalgic"], "in_theaters", [], None, ["Sandra Bullock","Nicole Kidman"], None, popularity=79),
    m("street-fighter", "Street Fighter", 2026, "2026-10-16", ["Action","Adventure"], 112, 6.9,
      "The classic fighting-game roster collides in a world tournament.",
      ["exciting","fun","friends"], "in_theaters", [], "Kitao Sakurai", None, None, popularity=83),
    m("avatar-fire-ash", "Avatar: Fire and Ash", 2025, "2025-12-19", ["Science Fiction","Adventure","Action"], 195, 7.6,
      "Jake and Neytiri's family encounter the Ash People, a fierce new Na'vi clan on Pandora.",
      ["epic","visually_stunning","family"], "streaming", ["Disney+"], "James Cameron", ["Sam Worthington","Zoe Saldaña"], None, popularity=81),
    # ---- recent hits 2024-2025 ----
    m("sinners", "Sinners", 2025, "2025-04-18", ["Horror","Drama","Music"], 137, 7.8,
      "Twin brothers return to 1930s Mississippi to open a juke joint and meet an ancient evil.",
      ["dark","music","thoughtful"], "streaming", ["HBO Max"], "Ryan Coogler", ["Michael B. Jordan"], None, "en", "R", 75),
    m("kpop-demon-hunters", "KPop Demon Hunters", 2025, "2025-06-20", ["Animation","Fantasy","Music","Action"], 96, 7.9,
      "A K-pop girl group secretly protects fans from demons - including a rival boy band.",
      ["fun","music","family","colorful"], "streaming", ["Netflix"], None, None, None, "en", "PG", 88),
    m("weapons", "Weapons", 2025, "2025-08-08", ["Horror","Mystery"], 128, 7.5,
      "When a class of children vanishes overnight, a town searches for what happened.",
      ["scary","twisty","tense"], "streaming", ["HBO Max"], "Zach Cregger", ["Julia Garner","Josh Brolin"], None, "en", "R", 70),
    m("f1", "F1", 2025, "2025-06-27", ["Action","Drama"], 155, 7.6,
      "A veteran driver returns to Formula 1 to mentor a rookie on a struggling team.",
      ["exciting","inspiring","friends"], "streaming", ["Apple TV+"], "Joseph Kosinski", ["Brad Pitt"], None, popularity=72),
    m("dune-part-two", "Dune: Part Two", 2024, "2024-03-01", ["Science Fiction","Adventure"], 166, 8.2,
      "Paul Atreides unites with the Fremen while seeking revenge against those who destroyed his family.",
      ["epic","visually_stunning","thoughtful"], "streaming", ["HBO Max","Prime Video"], "Denis Villeneuve", ["Timothée Chalamet","Zendaya"], None, popularity=74),
    m("inside-out-2", "Inside Out 2", 2024, "2024-06-14", ["Animation","Family","Comedy"], 96, 7.6,
      "Riley becomes a teenager and new emotions, led by Anxiety, move into headquarters.",
      ["family","feel_good","thoughtful"], "streaming", ["Disney+"], None, None, None, "en", "PG", 70),
    # ---- evergreen classics (safe recommendations) ----
    m("interstellar", "Interstellar", 2014, "2014-11-07", ["Science Fiction","Adventure","Drama"], 169, 8.5,
      "Explorers travel through a wormhole to find humanity a new home.",
      ["epic","thoughtful","space","emotional"], "classic", ["Prime Video","Netflix"], "Christopher Nolan", ["Matthew McConaughey","Anne Hathaway"], popularity=85),
    m("inception", "Inception", 2010, "2010-07-16", ["Science Fiction","Action","Thriller"], 148, 8.4,
      "A thief who steals secrets through dreams is asked to plant an idea instead.",
      ["twisty","exciting","thoughtful"], "classic", ["Netflix"], "Christopher Nolan", ["Leonardo DiCaprio"], popularity=80),
    m("dark-knight", "The Dark Knight", 2008, "2008-07-18", ["Action","Crime","Drama"], 152, 8.5,
      "Batman faces the Joker, a criminal mastermind who wants to watch Gotham burn.",
      ["dark","exciting","tense"], "classic", ["HBO Max"], "Christopher Nolan", ["Christian Bale","Heath Ledger"], popularity=78),
    m("shawshank", "The Shawshank Redemption", 1994, "1994-09-23", ["Drama","Crime"], 142, 8.7,
      "Two imprisoned men bond over years, finding hope and redemption.",
      ["inspiring","emotional","thoughtful"], "classic", ["Netflix"], "Frank Darabont", ["Tim Robbins","Morgan Freeman"], age="R", popularity=75),
    m("parasite", "Parasite", 2019, "2019-05-30", ["Thriller","Comedy","Drama"], 132, 8.5,
      "A poor family schemes its way into a wealthy household - until things spiral.",
      ["twisty","dark","thoughtful"], "classic", ["Prime Video","MUBI"], "Bong Joon Ho", None, lang="ko", age="R", popularity=70),
    m("spirited-away", "Spirited Away", 2001, "2001-07-20", ["Animation","Fantasy","Family"], 125, 8.5,
      "A girl trapped in a spirit world must work in a bathhouse to free her parents.",
      ["family","magical","cozy"], "classic", ["Netflix","HBO Max"], "Hayao Miyazaki", None, lang="ja", age="PG", popularity=72),
    m("coco", "Coco", 2017, "2017-11-22", ["Animation","Family","Music","Fantasy"], 105, 8.2,
      "A boy who dreams of music journeys into the Land of the Dead.",
      ["family","emotional","music","colorful"], "classic", ["Disney+"], None, None, age="PG", popularity=70),
    m("top-gun-maverick", "Top Gun: Maverick", 2022, "2022-05-27", ["Action","Drama"], 131, 8.2,
      "Maverick trains a new generation of pilots for a near-impossible mission.",
      ["exciting","inspiring","friends"], "classic", ["Prime Video"], "Joseph Kosinski", ["Tom Cruise"], popularity=68),
    m("oppenheimer", "Oppenheimer", 2023, "2023-07-21", ["Drama","History"], 180, 8.1,
      "The story of the physicist who led the creation of the atomic bomb.",
      ["thoughtful","epic","dark"], "classic", ["Prime Video"], "Christopher Nolan", ["Cillian Murphy"], age="R", popularity=69),
    m("la-la-land", "La La Land", 2016, "2016-12-09", ["Romance","Music","Comedy","Drama"], 128, 7.9,
      "A jazz pianist and an aspiring actress fall in love while chasing dreams in LA.",
      ["romantic","music","date_night","bittersweet"], "classic", ["Netflix"], "Damien Chazelle", ["Ryan Gosling","Emma Stone"], popularity=66),
    m("grand-budapest", "The Grand Budapest Hotel", 2014, "2014-03-28", ["Comedy","Crime","Adventure"], 99, 8.0,
      "A legendary concierge and his lobby boy get swept up in a stolen-painting caper.",
      ["funny","quirky","stylish"], "classic", ["Disney+"], "Wes Anderson", ["Ralph Fiennes"], age="R", popularity=60),
    m("knives-out", "Knives Out", 2019, "2019-11-27", ["Mystery","Comedy","Crime"], 130, 7.9,
      "A detective investigates the death of a wealthy crime novelist and his scheming family.",
      ["twisty","funny","friends"], "classic", ["Prime Video"], "Rian Johnson", ["Daniel Craig","Ana de Armas"], popularity=62),
    m("get-out", "Get Out", 2017, "2017-02-24", ["Horror","Thriller","Mystery"], 104, 7.7,
      "A weekend visit to a girlfriend's family turns deeply unsettling.",
      ["scary","twisty","thoughtful"], "classic", ["Netflix"], "Jordan Peele", None, age="R", popularity=58),
    m("mad-max-fury-road", "Mad Max: Fury Road", 2015, "2015-05-15", ["Action","Adventure","Science Fiction"], 120, 8.1,
      "In a desert wasteland, Furiosa and Max flee a tyrant in a relentless chase.",
      ["exciting","visually_stunning"], "classic", ["HBO Max"], "George Miller", ["Charlize Theron","Tom Hardy"], age="R", popularity=60),
    m("everything-everywhere", "Everything Everywhere All at Once", 2022, "2022-03-25", ["Science Fiction","Comedy","Action"], 139, 7.8,
      "A laundromat owner must connect with alternate versions of herself to save the multiverse.",
      ["quirky","emotional","funny"], "classic", ["Prime Video"], "Daniels", ["Michelle Yeoh"], age="R", popularity=60),
    m("about-time", "About Time", 2013, "2013-09-04", ["Romance","Comedy","Fantasy"], 123, 7.8,
      "A young man who can travel in time learns what really matters in love and family.",
      ["romantic","feel_good","cozy","date_night"], "classic", ["Netflix"], "Richard Curtis", ["Domhnall Gleeson","Rachel McAdams"], age="R", popularity=55),
    m("paddington-2", "Paddington 2", 2017, "2017-11-10", ["Family","Comedy","Adventure"], 103, 7.8,
      "Paddington is framed for theft and must clear his name.",
      ["family","feel_good","funny","cozy"], "classic", ["Netflix"], "Paul King", None, age="PG", popularity=55),
    # ---- regional picks (Turkish / Azerbaijani audience) ----
    m("winter-sleep", "Winter Sleep (Kış Uykusu)", 2014, "2014-06-13", ["Drama"], 196, 8.0,
      "A retired actor running a hotel in Cappadocia confronts tensions with family and tenants. Palme d'Or winner.",
      ["thoughtful","slow","arthouse"], "classic", ["MUBI"], "Nuri Bilge Ceylan", None, lang="tr", age="13+", popularity=40),
    m("ayla", "Ayla: The Daughter of War", 2017, "2017-10-27", ["Drama","War","History"], 125, 8.2,
      "A Turkish soldier in the Korean War rescues an orphaned girl - based on a true story.",
      ["emotional","inspiring"], "classic", ["Netflix"], "Can Ulkay", None, lang="tr", age="13+", popularity=45),
    m("miracle-cell-7", "Miracle in Cell No. 7 (7. Koğuştaki Mucize)", 2019, "2019-10-11", ["Drama","Family"], 132, 8.2,
      "A father with an intellectual disability is wrongly imprisoned and longs for his daughter.",
      ["emotional","family"], "classic", ["Netflix"], "Mehmet Ada Öztekin", None, lang="tr", age="13+", popularity=50),
]

def dump(name, obj):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(f"wrote {name}: {len(obj) if isinstance(obj, list) else 'obj'}")

dump("origins.json", ORIGINS)
dump("destinations.json", DESTINATIONS)
dump("routes.json", routes)
dump("movies.json", MOVIES)
dump("visa_meta.json", {
    "verified_at": VERIFIED_AT,
    "supported_passports": ["TR", "AZ"],
    "tiers": VISA_TIERS,
    "disclaimer": "Demo data compiled from public sources; verify with official government sites before travel.",
})
