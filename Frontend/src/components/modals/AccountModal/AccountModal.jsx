import './AccountModal.css';

const AccountModal = ({ onClose, onLogout, userData, isDarkTheme }) => {
  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="account-modal">
        <div className="account-header">
          <h2 className="account-title">Мой аккаунт</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="account-content">
          <div className="account-avatar">
            <div className="avatar-large">
              <span className="avatar-text">
                {userData?.username?.charAt(0).toUpperCase() || 'U'}
              </span>
            </div>
          </div>

          <div className="user-info">
            <h3 className="user-name">{userData?.username || 'Пользователь'}</h3>
            <p className="user-email">{userData?.email || 'email@example.com'}</p>
            <p className="user-join-date">Участник с {userData?.joinDate || 'сегодня'}</p>
          </div>

          <div className="account-form">
            <div className="form-group">
              <label className="form-label">Имя пользователя</label>
              <input 
                type="text" 
                className="form-input"
                value={userData?.username || ''}
                readOnly
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Email</label>
              <input 
                type="email" 
                className="form-input"
                value={userData?.email || ''}
                readOnly
              />
            </div>

            <div className="form-group">
              <label className="form-label">Текущий план</label>
              <div className="plan-info">
                <span className="plan-name">{userData?.plan || 'Basic'}</span>
                <button className="upgrade-button">Обновить до Премиум</button>
              </div>
            </div>
          </div>
        </div>

        <div className="account-footer">
          <button className="save-button">Сохранить изменения</button>
          <button className="logout-button" onClick={onLogout}>Выйти из аккаунта</button>
          <button className="cancel-button" onClick={onClose}>Отмена</button>
        </div>
      </div>
    </div>
  );
};

export default AccountModal;