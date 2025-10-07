import './Account.css';
import { useNavigate } from 'react-router-dom';

const Account = () => {
  const navigate = useNavigate();

  const handleBackClick = () => {
    navigate(-1);
  };

  return (
    <div className="account-page">
      <button className="back-button" onClick={handleBackClick}>
        ← Назад
      </button>
      
      <div className="account-container">
        <h2 className="account-title">Аккаунт</h2>
        
        <div className="account-form">
          <div className="form-group">
            <label className="form-label">Имя аккаунта</label>
            <input 
              type="text" 
              className="form-input"
              placeholder="Введите имя аккаунта"
              defaultValue="user123"
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Пароль аккаунта</label>
            <input 
              type="password" 
              className="form-input"
              placeholder="Введите пароль"
              defaultValue="••••••••"
            />
          </div>

          <div className="form-actions">
            <button className="save-button">Сохранить изменения</button>
            <button className="logout-button">Выйти из аккаунта</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Account;