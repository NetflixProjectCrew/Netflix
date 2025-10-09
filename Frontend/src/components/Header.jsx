import './Header.css';

const Header = ({ onSettingsClick, onAccountClick, isLoggedIn, userData }) => {
  return (
    <header className="header">
      <h1 className="header__logo">
        Cinemate
      </h1>

      <div className="header__search">
        <input type="text" placeholder="Search for movies, series..." />
      </div>

      <div className="header__icons">
        <div 
          className="header__icon settings" 
          onClick={onSettingsClick}
          title="Settings"
        ></div>
        <div 
          className="header__icon avatar"
          onClick={onAccountClick}
          title={isLoggedIn ? "Account" : "Login"}
        >
          {isLoggedIn && userData && (
            <div className="avatar-indicator"></div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;