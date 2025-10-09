import { useState, useEffect } from 'react';
import Header from './components/Header';
import MovieRow from './components/MovieRow';
import SettingsModal from './components/SettingsModal';
import AccountModal from './components/AccountModal';
import AuthModal from './components/AuthModal';
import MoviePlayer from './components/MoviePlayer';
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

  const handleLogin = (userData) => {
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
            onMovieClick={() => setIsMoviePlayerOpen(true)}
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