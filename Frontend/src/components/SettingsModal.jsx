import { useState } from 'react';
import './SettingsModal.css';

const SettingsModal = ({ onClose, isDarkTheme, onThemeToggle }) => {
  const [language, setLanguage] = useState('ru');
  const [videoQuality, setVideoQuality] = useState('auto');
  const [notifications, setNotifications] = useState(true);
  const [autoplay, setAutoplay] = useState(true);

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleSave = () => {
    const settings = {
      language,
      videoQuality,
      notifications,
      autoplay,
      isDarkTheme
    };
    localStorage.setItem('cinemate_settings', JSON.stringify(settings));
    alert('Настройки сохранены!');
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="settings-modal">
        <div className="settings-header">
          <h2 className="settings-title">Настройки</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="settings-content">
          <div className="settings-item">
            <span className="settings-label">Тема</span>
            <div className="theme-switch">
              <span className="theme-label">Темная</span>
              <label className="switch">
                <input 
                  type="checkbox" 
                  checked={!isDarkTheme}
                  onChange={onThemeToggle}
                />
                <span className="slider"></span>
              </label>
              <span className="theme-label">Светлая</span>
            </div>
          </div>
          
          <div className="settings-item">
            <span className="settings-label">Язык</span>
            <select 
              className="settings-select"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="ru">Русский</option>
              <option value="en">English</option>
              <option value="es">Español</option>
              <option value="fr">Français</option>
              <option value="de">Deutsch</option>
            </select>
          </div>

          <div className="settings-item">
            <span className="settings-label">Качество видео</span>
            <select 
              className="settings-select"
              value={videoQuality}
              onChange={(e) => setVideoQuality(e.target.value)}
            >
              <option value="auto">Авто</option>
              <option value="1080p">1080p</option>
              <option value="720p">720p</option>
              <option value="480p">480p</option>
            </select>
          </div>

          <div className="settings-item">
            <span className="settings-label">Уведомления</span>
            <label className="switch">
              <input 
                type="checkbox" 
                checked={notifications}
                onChange={(e) => setNotifications(e.target.checked)}
              />
              <span className="slider"></span>
            </label>
          </div>

          <div className="settings-item">
            <span className="settings-label">Автовоспроизведение</span>
            <label className="switch">
              <input 
                type="checkbox" 
                checked={autoplay}
                onChange={(e) => setAutoplay(e.target.checked)}
              />
              <span className="slider"></span>
            </label>
          </div>
        </div>

        <div className="settings-footer">
          <button className="save-button" onClick={handleSave}>Сохранить</button>
          <button className="cancel-button" onClick={onClose}>Отмена</button>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;