import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { moviesApi } from "../../api/moviesApi";

export default function WatchPage() {
  const { slug } = useParams();
  const [movie, setMovie] = useState(null);
  const videoRef = useRef(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await moviesApi.getMovie(slug);
        setMovie(data);
      } catch (e) {
        setErr("Не удалось загрузить фильм");
      }
    })();
  }, [slug]);

  // отправка прогресса раз в 10 сек
  useEffect(() => {
    if (!movie) return;
    const id = setInterval(async () => {
      const el = videoRef.current;
      if (!el || !el.duration || Number.isNaN(el.duration)) return;
      try {
        await moviesApi.updateProgress(
            slug,
            Math.floor(el.currentTime),
            Math.floor(el.duration)
            );
        } catch {}
    }, 10000);
    return () => clearInterval(id);
  }, [movie, slug]);

  if (err) return <Shell><p className="text-red-600">{err}</p></Shell>;
  if (!movie) return <Shell><p>Загрузка...</p></Shell>;

  return (
    <Shell>
      <div className="space-y-4">
        <h1 className="text-xl font-bold">{movie.title}</h1>
        <div className="w-full aspect-video bg-black rounded-2xl overflow-hidden">
          <video ref={videoRef} className="w-full h-full" src={movie.video} controls autoPlay />
        </div>
        <p className="opacity-80">{movie.description}</p>
      </div>
    </Shell>
  );
}

function Shell({ children }) {
  return <main className="px-4 py-6 max-w-6xl mx-auto">{children}</main>;
}
