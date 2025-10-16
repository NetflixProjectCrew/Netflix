import { useState } from 'react';
import './MoviePlayer.css';

const MoviePlayer = ({ onClose, isDarkTheme }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(120); 

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = (e) => {
    setCurrentTime(e.target.value);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="modal-overlay movie-player-overlay" onClick={handleOverlayClick}>
      <div className="movie-player-fullscreen">
        <button className="close-button-player" onClick={onClose}>×</button>
        
        <div className="video-container">
          <div className="video-placeholder">
            {isPlaying ? (
              <div className="playing-video">
                <div className="video-content">
                  <h3>Интерстеллар</h3>
                  <p>Сейчас воспроизводится...</p>
                </div>
              </div>
            ) : (
              <div className="paused-video">
                <button className="big-play-button" onClick={handlePlayPause}>
                  ▶
                </button>
                <h3>Интерстеллар</h3>
                <p>Нажмите для воспроизведения</p>
              </div>
            )}
          </div>

          <div className="player-controls-fullscreen">
            <div className="progress-bar">
              <input 
                type="range" 
                min="0" 
                max={duration}
                value={currentTime}
                onChange={handleTimeUpdate}
                className="progress-slider"
              />
              <div className="time-display">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(duration)}</span>
              </div>
            </div>

            <div className="control-buttons">
              <button 
                className="control-button play-pause-fullscreen"
                onClick={handlePlayPause}
              >
                {isPlaying ? '⏸' : '▶'}
              </button>
              
              <button className="control-button volume-button">
                🔈
              </button>
              
              <button className="control-button fullscreen-button">
                ⛶
              </button>
            </div>
          </div>
        </div>

        <div className="movie-info-fullscreen">
          <h2>Интерстеллар</h2>
          <p>2014 · Фантастика, Драма · ⭐ 8.6/10</p>
        </div>
      </div>
    </div>
  );
};

export default MoviePlayer;