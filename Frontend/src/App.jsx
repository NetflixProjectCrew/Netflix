import React, { useState, useEffect } from 'react';  
import Header from './pages/components/common/Header';
import MovieRow from './pages/components/common/MovieRow/MovieRow';
import SettingsModal from './pages/components/modals/SettingsModal/SettingsModal';
import AccountModal from './pages/components/modals/AccountModal/AccountModal';
import AuthModal from './pages/components/modals/AuthModal/AuthModal';
import MovieModal from './pages/components/modals/MovieModal/MovieModal';
import MoviePlayer from './pages/components/modals/MoviePlayer/MoviePlayer';
import { authApi } from './api/authApi';
import { moviesApi } from './api/moviesApi';
import './App.css';

const rowTitles = [
  { title: 'Continue Watching', type: 'watched' },
  { title: 'Recommendation for You', type: 'all' },
  { title: 'Top Movies of This Year', type: 'year' },
  { title: 'Popular Movies', type: 'popular' }
];

function App() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isAccountOpen, setIsAccountOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isMovieModalOpen, setIsMovieModalOpen] = useState(false);
  const [isMoviePlayerOpen, setIsMoviePlayerOpen] = useState(false);
  const [isDarkTheme, setIsDarkTheme] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userData, setUserData] = useState(null);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [isLoadingUser, setIsLoadingUser] = useState(true);
  const [selectedSlug, setSelectedSlug] = useState(null);

  // Проверка авторизации при загрузке
  useEffect(() => {
    checkAuth();
    loadTheme();
  }, []);

  const loadTheme = () => {
    const savedSettings = localStorage.getItem('cinemate_settings');
    if (savedSettings) {
      const settings = JSON.parse(savedSettings);
      setIsDarkTheme(settings.isDarkTheme !== false);
    }
  };

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      setIsLoadingUser(false);
      return;
    }

    try {
      const profile = await authApi.getProfile();
      setUserData(profile);
      setIsLoggedIn(true);
    } catch (error) {
      console.error('Auth check failed:', error);
      // Токен недействителен - очищаем
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('cinemate_user');
    } finally {
      setIsLoadingUser(false);
    }
  };

  const toggleTheme = () => {
    const newTheme = !isDarkTheme;
    setIsDarkTheme(newTheme);
    
    // Сохраняем в настройки
    const settings = JSON.parse(localStorage.getItem('cinemate_settings') || '{}');
    settings.isDarkTheme = newTheme;
    localStorage.setItem('cinemate_settings', JSON.stringify(settings));
  };

  const handleLogin = (userProfile) => {
    setUserData(userProfile);
    setIsLoggedIn(true);
    setIsAuthOpen(false);
    localStorage.setItem('cinemate_user', JSON.stringify(userProfile));
  };

  const handleLogout = () => {
    setUserData(null);
    setIsLoggedIn(false);
    setIsAccountOpen(false);
    localStorage.removeItem('cinemate_user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  const handleAccountClick = () => {
    if (isLoggedIn) {
      setIsAccountOpen(true);
    } else {
      setIsAuthOpen(true);
    }
  };

  const handleMovieClick = (movie, slug) => {
    setSelectedMovie(movie);
    setIsMovieModalOpen(true);
    setSelectedSlug(slug);

  };

  const handlePlayMovie = () => {
    setIsMovieModalOpen(false);
    setIsMoviePlayerOpen(true);
  };

  if (isLoadingUser) {
    return (
      <div className={`app ${isDarkTheme ? 'dark-theme' : 'light-theme'}`}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh',
          color: 'var(--text-primary)'
        }}>
          Загрузка...
        </div>
      </div>
    );
  }

  return (
    <div className={`app ${isDarkTheme ? 'dark-theme' : 'light-theme'}`}>
      <Header 
        onSettingsClick={() => setIsSettingsOpen(true)}
        onAccountClick={handleAccountClick}
        isLoggedIn={isLoggedIn}
        userData={userData}
      />
      
      <main className="main">
        {rowTitles.map((row, index) => (
          <MovieRow 
            key={index} 
            title={row.title}
            type={row.type}
            onMovieClick={handleMovieClick}
            isLoggedIn={isLoggedIn}
          />
        ))}
      </main>

      {isSettingsOpen && (
        <SettingsModal 
          onClose={() => setIsSettingsOpen(false)}
          isDarkTheme={isDarkTheme}
          onThemeToggle={toggleTheme}
        />
      )}

      {isAccountOpen && isLoggedIn && (
        <AccountModal 
          onClose={() => setIsAccountOpen(false)}
          onLogout={handleLogout}
          userData={userData}
          isDarkTheme={isDarkTheme}
        />
      )}

      {isAuthOpen && (
        <AuthModal 
          onClose={() => setIsAuthOpen(false)}
          onLogin={handleLogin}
          isDarkTheme={isDarkTheme}
        />
      )}

      {isMovieModalOpen && selectedMovie && (
        <MovieModal 
          movie={selectedMovie}
          onClose={() => setIsMovieModalOpen(false)}
          onPlay={handlePlayMovie}
          isDarkTheme={isDarkTheme}
          isLoggedIn={isLoggedIn}
        />
      )}

      {isMoviePlayerOpen && selectedMovie && (
        <MoviePlayer 
          movie={selectedMovie}
          onClose={() => setIsMoviePlayerOpen(false)}
          isDarkTheme={isDarkTheme}
        />
      )}
    </div>
  );
}

export default App;