import './MovieRow.css';

const MovieRow = ({ title, onMovieClick }) => {
  const movies = Array.from({ length: 7 });

  return (
    <div className="movie-row">
      <h2 className="movie-row__title">{title}</h2>
      <div className="movie-row__list">
        {movies.map((_, index) => (
          <div 
            key={index} 
            className="movie-row__item"
            onClick={onMovieClick}
          >
            <div className="movie-placeholder">
              Movie {index + 1}
            </div>
          </div>
        ))}
      </div>
      <hr className="movie-row__divider" />
    </div>
  );
};

export default MovieRow;