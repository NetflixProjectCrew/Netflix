import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { moviesApi } from "../../../api/moviesApi";

export default function MovieModal({ slug, onClose, onPlay }) {
    const [movie, setMovie] = useState(null);

    useEffect(() => {
        (async () => {
          try {
            const data = await moviesApi.getMovie(slug);
            setMovie(data);
        } catch {
            onClose?.();
        }
      })();
    }, [slug, onClose]);

    useEffect(() => {
        const onEsc = (e) => { if (e.key === "Escape") onClose?.(); };
        window.addEventListener("keydown", onEsc);
        return () => window.removeEventListener("keydown", onEsc);
    }, [onClose]);

    if (!movie) return null;

    return createPortal(
      <div className="fixed inset-0 z-[100] bg-black/70 flex items-center justify-center p-4" onClick={onClose}>
          <div className="max-w-4xl w-full rounded-2xl bg-white text-black overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <div className="aspect-video bg-black">
              {/* трейлер, если есть отдельное поле trailer; если нет — постер */}
              {movie.trailer ? (
                <video src={movie.trailer} controls className="w-full h-full object-cover" />
            ) : movie.poster ? (
                <img src={movie.poster} alt={movie.title} className="w-full h-full object-cover"/>
            ) : null}
          </div>

          <div className="p-5 space-y-3">
            <h3 className="text-2xl font-bold">{movie.title} <span className="opacity-60">({movie.year})</span></h3>
            <p className="opacity-80">{movie.description}</p>

            <div className="text-sm grid md:grid-cols-2 gap-4">
              {movie.author_info && (
                <div><span className="opacity-60">Режиссёр: </span>{movie.author_info.name}</div>
              )}
              {Array.isArray(movie.genres_info) && movie.genres_info.length > 0 && (
                <div><span className="opacity-60">Жанры: </span>{movie.genres_info.map(g => g.name).join(", ")}</div>
              )}
              {Array.isArray(movie.actors) && movie.actors.length > 0 && (
                <div className="md:col-span-2">
                  <span className="opacity-60">В главных ролях: </span>
                  {movie.actors.map(a => a.name).join(", ")}
                </div>
              )}
            </div>

            <div className="flex gap-3 pt-2">
              <button onClick={onPlay} className="px-4 py-2 rounded-xl bg-black text-white">
                Воспроизвести
              </button>
              <button onClick={onClose} className="px-4 py-2 rounded-xl bg-gray-200">
                Закрыть
              </button>
            </div>
          </div>
        </div>
      </div>,
      document.body
    );
}
