import './MovieModal.css';
import { ToastContainer } from 'react-toastify';

const MovieModal = ({ movie, onClose, onPlay, isDarkTheme }) => {
  if (!movie){
    return null
  }
  
  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };
  

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <ToastContainer />
      <div className="movie-modal">
        <button className="close-button" onClick={onClose}>×</button>
        
        <div className="movie-poster">
          <div className="poster-placeholder">
            {
              movie.poster? (
                <img 
                src={movie.poster}
                alt={movie.title}
                className='poster-img'
                />
              ) : (
                <div className="poster-placeholder"><span>Постер фильма</span></div>
              )
            }
          </div>
        </div>

        <div className="movie-details">
          <h2 className="movie-title">{movie.title}</h2>
          <div className="movie-meta">
            <span className="movie-year">{movie.year}</span>
            {/* <span className="movie-rating">⭐ {movie.rating}/10</span> */}
            
            {/* <span className="movie-rating">⏱ {movie.likes_count}</span>
            <span className="movie-duration">⏱ {movie.duration}</span> */}
          </div>
          
          <p className="movie-description">
          {movie.description}
          </p>


          {movie.genres_info?.length > 0 && (
            <div className="movie-genres">
              {movie.genres_info.map(g => (
                <span key={g.id} className="genre-tag">{g.name}</span>
              ))}
            </div>
          )}


          <div className="movie-cast">
            <h3>В главных ролях:</h3>
            {}
          </div>
        </div>

        <div className="movie-actions">
          <button className="play-button" onClick={onPlay}>
            ▶ Воспроизвести
          </button>
          <button className="trailer-button">
            📺 Трейлер
          </button>
          <button className="favorite-button">
            ❤️ В избранное
          </button>
        </div>
      </div>
    </div>
  );
};

export default MovieModal;