import React from "react";

export default function MovieCard({ movie, onClick }) {
    return (
        <div
            className="movie-card"
            onClick={() => onClick(movie.slug)}
            style={{ cursor: "pointer" }}
            title={movie.title}
        >
            {/* <img src={movie.poster} alt={movie.title} width={160} height={240} />
            <div>{movie.title}</div> */}
            <div 
              key={movie.id} 
              className="movie-row__item"
              onClick={() => onClick(movie, movie.slug)}
            >
              {movie.poster ? (
                <img 
                  src={movie.poster} 
                  alt={movie.title}
                  className="movie-poster-img"
                  loading="lazy"
                />
              ) : (
                <div className="movie-placeholder">
                  <div className="movie-placeholder-content">
                    <h3>{movie.title}</h3>
                    <p>{movie.year}</p>
                    <p>{movie.genres_info?movie.genres_info[0]:"none"}</p>
                  </div>
                </div>
              )}
              
              <div className="movie-overlay">
                <div className="movie-overlay-content">
                  <h4 className="movie-overlay-title">{movie.title}</h4>
                  <div className="movie-overlay-meta">
                    {movie.year && <span>{movie.year}</span>}
                    {movie.likes && (
                      <span className="movie-likes">
                        ❤️ {typeof movie.likes === 'object' ? movie.likes.count : movie.likes}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
        </div>
           
    );
}
