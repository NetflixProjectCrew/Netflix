import './MoviePlayer.css';

const MoviePlayer = ({ onClose, isDarkTheme }) => {
  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="movie-player-modal">
        <button className="close-button-large" onClick={onClose}>×</button>
        
        <div className="video-player">
          <div className="player-placeholder">
            <span>Видеоплеер</span>
          </div>
        </div>

        <div className="player-controls">
          <button className="play-button">▶ Воспроизвести</button>
        </div>
      </div>
    </div>
  );
};

export default MoviePlayer;