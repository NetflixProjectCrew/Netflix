import React, { useState, useEffect } from 'react';  
import Header from './components/common/Header/Header';
import MovieRow from './components/common/MovieRow/MovieRow';
import SettingsModal from './components/modals/SettingsModal/SettingsModal';
import AccountModal from './components/modals/AccountModal/AccountModal';
import AuthModal from './components/modals/AuthModal/AuthModal';
import MovieModal from './components/modals/MovieModal/MovieModal';
import MoviePlayer from './components/modals/MoviePlayer/MoviePlayer';
import './App.css';  
const rowTitles = [
  'Continue Watching',
  'Recommendation for You',
  'Top Detectives of This Year',
  'Top Thrillers of This Year',
  'Top Horrors of This Year'
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

  useEffect(() => {
    const savedUser = localStorage.getItem('cinemate_user');
    if (savedUser) {
      setUserData(JSON.parse(savedUser));
      setIsLoggedIn(true);
    }
  }, []);

  const toggleTheme = () => {
    setIsDarkTheme(!isDarkTheme);
  };

  const handleLogin = (userRawData) => {
    setUserData(userData);
    setIsLoggedIn(true);
    setIsAuthOpen(false);

    localStorage.setItem('cinemate_user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUserData(null);
    setIsLoggedIn(false);
    setIsAccountOpen(false);
    localStorage.removeItem('cinemate_user');
  };

  const handleAccountClick = () => {
    if (isLoggedIn) {
      setIsAccountOpen(true);
    } else {
      setIsAuthOpen(true);
    }
  };

  const handleMovieClick = () => {
    setIsMovieModalOpen(true);
  };

  const handlePlayMovie = () => {
    setIsMovieModalOpen(false);
    setIsMoviePlayerOpen(true);
  };

  return (
    <div className={`app ${isDarkTheme ? 'dark-theme' : 'light-theme'}`}>
      <Header 
        onSettingsClick={() => setIsSettingsOpen(true)}
        onAccountClick={handleAccountClick}
        isLoggedIn={isLoggedIn}
        userData={userData}
      />
      
      <main className="main">
        {rowTitles.map((title, index) => (
          <MovieRow 
            key={index} 
            title={title}
            onMovieClick={handleMovieClick}
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

      {isMovieModalOpen && (
        <MovieModal 
          onClose={() => setIsMovieModalOpen(false)}
          onPlay={handlePlayMovie}
          isDarkTheme={isDarkTheme}
        />
      )}

      {isMoviePlayerOpen && (
        <MoviePlayer 
          onClose={() => setIsMoviePlayerOpen(false)}
          isDarkTheme={isDarkTheme}
        />
      )}
    </div>
  );
}

export default App;