import { useEffect, useState } from "react";
import { moviesApi } from "../../api/moviesApi";

export default function BrowsePage({ onMovieClick }) {
  const [rows, setRows] = useState([
    { key: "popular", title: "Популярное", params: { ordering: "-views" }, items: [], loading: true },
    { key: "new", title: "Новинки", params: { ordering: "-year" }, items: [], loading: true },
    { key: "all", title: "Все фильмы", params: {}, items: [], loading: true },
  ]);

  useEffect(() => {
    rows.forEach(async (row, idx) => {
      try {
        const data = await moviesApi.getMovies(row.params);
        setRows((old) => old.map((r, i) => i === idx ? ({ ...r, items: data.results || data, loading: false }) : r));
      } catch {
        setRows((old) => old.map((r, i) => i === idx ? ({ ...r, items: [], loading: false }) : r));
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <main className="px-4 py-6 space-y-8 max-w-7xl mx-auto">
      {rows.map(row => (
        <section key={row.key} className="space-y-3">
          <h2 className="text-xl font-bold">{row.title}</h2>
          {row.loading ? (
            <p>Загрузка...</p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-6 gap-3">
              {row.items.map(m => (
                <button
                  key={m.id}
                  onClick={() => onMovieClick?.(m.slug)}
                  className="text-left group"
                  title={m.title}
                >
                  <div className="aspect-[2/3] w-full overflow-hidden rounded-xl border">
                    {m.poster ? (
                      <img src={m.poster} alt={m.title} className="w-full h-full object-cover group-hover:scale-105 transition"/>
                    ) : (
                      <div className="w-full h-full grid place-items-center text-sm opacity-60">Нет постера</div>
                    )}
                  </div>
                  <div className="mt-2 text-sm line-clamp-1">{m.title}</div>
                </button>
              ))}
            </div>
          )}
        </section>
      ))}
    </main>
  );
}
