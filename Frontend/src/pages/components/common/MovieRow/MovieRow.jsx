import { useState, useEffect } from 'react';
import './MovieRow.css';
import { moviesApi } from '../../../../api/moviesApi';
import MovieCard from '../MovieCard';

const MovieRow = ({ title, type, onMovieClick, isLoggedIn }) => {
  const [movies, setMovies] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadMovies();
  }, [type, isLoggedIn]);

  const loadMovies = async () => {
    setIsLoading(true);
    setError(null);

    try {
      let data = [];

      if (type === 'watched' && isLoggedIn) {
        // Загружаем просмотренные фильмы
        data = await moviesApi.getWatchedMovies();
      } else if (type === 'year') {
        // Фильмы текущего года
        const currentYear = new Date().getFullYear();
        data = await moviesApi.getMovies({ year: currentYear, ordering: '-views' });
      } else if (type === 'popular') {
        // Популярные фильмы
        data = await moviesApi.getMovies({ ordering: '-views' });
      } else {
        // Все фильмы
        data = await moviesApi.getMovies();
      }

      // Ограничиваем до 10 фильмов
      setMovies(Array.isArray(data) ? data.slice(0, 10) : []);
    } catch (err) {
      console.error('Error loading movies:', err);
      setError('Не удалось загрузить фильмы');
      setMovies([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Не показываем ряд "Continue Watching" если пользователь не авторизован
  if (type === 'watched' && !isLoggedIn) {
    return null;
  }

  return (
    <div className="movie-row">
      <h2 className="movie-row__title">{title}</h2>
      
      {isLoading ? (
        <div className="movie-row__loading">
          <div className="loading-spinner">Загрузка...</div>
        </div>
      ) : error ? (
        <div className="movie-row__error">{error}</div>
      ) : movies.length === 0 ? (
        <div className="movie-row__empty">
          {type === 'watched' ? 'Вы ещё ничего не смотрели' : 'Фильмы не найдены'}
        </div>
      ) : (
        <div className="movie-row__list">
          {movies.map((movie) => (
            <MovieCard key={movie.slug} movie={movie} onClick={onMovieClick} />
          ))}
        </div>
      )}
      
      <hr className="movie-row__divider" />
    </div>
  );
};

export default MovieRow;