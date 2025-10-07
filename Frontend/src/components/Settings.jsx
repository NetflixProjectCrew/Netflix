import './Settings.css';
import { useNavigate } from 'react-router-dom';

const Settings = () => {
  const navigate = useNavigate();

  const handleBackClick = () => {
    navigate(-1);
  };

  return (
    <div className="settings-page">
      <button className="back-button" onClick={handleBackClick}>
        ← Назад
      </button>
      
      <div className="settings-container">
        <h2 className="settings-title">Настройки</h2>
        
        <div className="settings-item">
          <span className="settings-label">Тема</span>
          <select className="settings-select">
            <option value="dark">Темная</option>
            <option value="light">Светлая</option>
            <option value="auto">Авто</option>
          </select>
        </div>
        
        <div className="settings-item">
          <span className="settings-label">Подписки</span>
          <div className="settings-value">
            Активные: 3
            <button className="settings-button">Управлять</button>
          </div>
        </div>
        
        <div className="settings-item">
          <span className="settings-label">Текущий план</span>
          <div className="settings-value">
            Премиум
            <button className="settings-button upgrade">Обновить</button>
          </div>
        </div>

        <div className="settings-item">
          <span className="settings-label">Язык</span>
          <select className="settings-select">
            <option value="ru">Русский</option>
            <option value="en">English</option>
          </select>
        </div>

        <div className="settings-item">
          <span className="settings-label">Уведомления</span>
          <div className="settings-value">
            <label className="settings-switch">
              <input type="checkbox" defaultChecked />
              <span className="slider"></span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;