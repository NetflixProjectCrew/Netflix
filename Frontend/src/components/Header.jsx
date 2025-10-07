import './Header.css';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();

  const handleSettingsClick = () => {
    navigate('/settings');
  };

  const handleAccountClick = () => {
    navigate('/account');
  };

  const handleLogoClick = () => {
    navigate('/');
  };

  return (
    <header className="header">
      <h1 className="header__logo" onClick={handleLogoClick}>
        Cinemate
      </h1>

      <div className="header__search">
        <input type="text" placeholder="Search for movies, series..." />
      </div>

      <div className="header__icons">
        <div 
          className="header__icon settings" 
          onClick={handleSettingsClick}
          title="Settings"
        ></div>
        <div 
          className="header__icon avatar"
          onClick={handleAccountClick}
          title="Account"
        ></div>
      </div>
    </header>
  );
};

export default Header;