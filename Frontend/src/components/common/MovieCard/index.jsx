// MovieCard/index.jsx
export default function MovieCard({ movie, onClick }) {
  const handleClick = () => onClick(movie, movie.slug);

  return (
    <div className="movie-card" onClick={handleClick} style={{ cursor: 'pointer' }} title={movie.title}>
      <div className="movie-row__item">
        {movie.poster ? (
          <img src={movie.poster} alt={movie.title} className="movie-poster-img" loading="lazy" />
        ) : (
          <div className="movie-placeholder">
            <div className="movie-placeholder-content">
              <h3>{movie.title}</h3>
              <p>{movie.year}</p>

              {/* genres в лістинге — обычно массив строк. Рендерим через map */}
              {Array.isArray(movie.genres) && movie.genres.length > 0 && (
                <div className="movie-genres">
                  {movie.genres.map((g, i) => (
                    <p key={g?.id || g || i}>{typeof g === 'string' ? g : g?.name}</p>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        <div className="movie-overlay">
          <div className="movie-overlay-content">
            <h4 className="movie-overlay-title">{movie.title}</h4>
            <div className="movie-overlay-meta">
              {movie.year && <span>{movie.year}</span>}
              {movie.likes && (
                <span className="movie-likes">❤️ {typeof movie.likes === 'object' ? movie.likes.count : movie.likes}</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
