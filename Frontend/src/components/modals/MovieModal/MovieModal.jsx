import './MovieModal.css';

const MovieModal = ({ onClose, onPlay, isDarkTheme }) => {
  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="movie-modal">
        <button className="close-button" onClick={onClose}>×</button>
        
        <div className="movie-poster">
          <div className="poster-placeholder">
            <span>Постер фильма</span>
          </div>
        </div>

        <div className="movie-details">
          <h2 className="movie-title">Трансформеры</h2>
          <div className="movie-meta">
            <span className="movie-year">2007</span>
            <span className="movie-rating">⭐ 7.3/10</span>
            <span className="movie-duration">⏱ 2ч 23м</span>
          </div>
          
          <p className="movie-description">
          американский научно-фантастический боевик 2007 года режиссёра Майкла Бэя,
          снятый по мотивам серии игрушек компании Hasbro и одноимённого мультсериала.
          Фильм повествует о войне автоботов и десептиконов — разумных инопланетных роботов, 
          способных трансформироваться в разнообразную технику. 
          Предметом их раздора становится могущественный артефакт Великая Искра, 
          который при неправильном использовании может принести в Галактику разрушения и смерть. 
          Автоботы прилетают на Землю, чтобы защитить Искру от десептиконов, 
          которые хотят использовать её в своих корыстных целях. Слабые, но смелые люди приходят на помощь автоботам.      
          </p>

          <div className="movie-genres">
            <span className="genre-tag">Научная фантастика</span>
            <span className="genre-tag">Боевик</span>
            <span className="genre-tag">Приключения</span>
          </div>

          <div className="movie-cast">
            <h3>В главных ролях:</h3>
            <p>Шайа Лабаф (Сэм Уитвики), Меган Фокс (Микаэла Бейнс), 
                Джош Дюамель (майор Леннокс), Тайриз Гибсон (сержант Эппс), 
                Джон Туртурро (агент Сеймур Симмонс), 
                а также Питер Каллен (озвучка Оптимуса Прайма) 
                и Хьюго Уивинг (озвучка Мегатрона)</p>
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