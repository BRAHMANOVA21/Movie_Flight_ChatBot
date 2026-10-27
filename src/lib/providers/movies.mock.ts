// Movie search over TMDB-shaped mock data. Replace with TMDB /discover later.
import movies from "../../data/movies.json";
import type { Movie } from "../../types";

export interface MovieQuery {
  genres?: string[]; moods?: string[]; status?: Movie["status"][];
  min_year?: number; max_runtime_min?: number; languages?: string[];
  family_safe?: boolean; similar_to?: string; limit?: number;
}

const DATA = movies as Movie[];
const FAMILY = new Set(["G", "PG"]);

export function searchMovies(q: MovieQuery) {
  const ref = q.similar_to ? DATA.find(m => m.title.toLowerCase().includes(q.similar_to!.toLowerCase())) : undefined;
  const wantGenres = q.genres ?? ref?.genres.map(g => g.name) ?? [];
  const wantMoods = q.moods ?? ref?.mood_tags ?? [];
  return DATA
    .filter(m => m.id !== ref?.id)
    .filter(m => !q.status?.length || q.status.includes(m.status))
    .filter(m => !q.min_year || m.year >= q.min_year)
    .filter(m => !q.max_runtime_min || m.runtime_min <= q.max_runtime_min)
    .filter(m => !q.languages?.length || q.languages.includes(m.original_language))
    .filter(m => !q.family_safe || FAMILY.has(m.age_rating))
    .map(m => {
      const g = m.genres.filter(x => wantGenres.includes(x.name)).length;
      const mo = m.mood_tags.filter(x => wantMoods.includes(x)).length;
      const score = g * 3 + mo * 2 + m.vote_average / 2 + m.popularity / 40;
      const why = [
        ...m.genres.filter(x => wantGenres.includes(x.name)).map(x => x.name),
        ...m.mood_tags.filter(x => wantMoods.includes(x)).map(x => x.replace("_", " ")),
      ].slice(0, 3);
      return { movie: m, score, why: why.length ? `Matches: ${why.join(", ")}` : "Popular right now" };
    })
    .filter(r => (wantGenres.length || wantMoods.length) ? r.score > 6 : true)
    .sort((a, b) => b.score - a.score)
    .slice(0, q.limit ?? 8);
}
