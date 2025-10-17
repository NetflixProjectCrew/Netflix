import { useState } from 'react';
import './AuthModal.css';
import {authApi} from '../../../api/authApi';

const AuthModal = ({ onClose, onLogin, isDarkTheme }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (isLogin) {
      const userData = {
        username: formData.username,
        email: formData.email || `${formData.username}@example.com`,
        plan: 'Basic',
        joinDate: new Date().toLocaleDateString()
      };
      onLogin(userData);
    } else {
      if (formData.password !== formData.confirmPassword) {
        alert('Пароли не совпадают!');
        return;
      }
      const userData = {
        username: formData.username,
        email: formData.email,
        plan: 'Basic',
        joinDate: new Date().toLocaleDateString()
      };
      onLogin(userData);
      authApi.register({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        passwordConfirm: formData.confirmPassword
    })
    };
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setFormData({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    });
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="auth-modal">
        <div className="auth-header">
          <h2 className="auth-title">{isLogin ? 'Вход в аккаунт' : 'Регистрация'}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Имя пользователя</label>
            <input 
              type="text" 
              name="username"
              className="form-input"
              placeholder="Введите имя пользователя"
              value={formData.username}
              onChange={handleInputChange}
              required
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label className="form-label">Email</label>
              <input 
                type="email" 
                name="email"
                className="form-input"
                placeholder="Введите email"
                value={formData.email}
                onChange={handleInputChange}
                required
              />
            </div>
          )}
          
          <div className="form-group">
            <label className="form-label">Пароль</label>
            <input 
              type="password" 
              name="password"
              className="form-input"
              placeholder="Введите пароль"
              value={formData.password}
              onChange={handleInputChange}
              required
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label className="form-label">Подтвердите пароль</label>
              <input 
                type="password" 
                name="confirmPassword"
                className="form-input"
                placeholder="Повторите пароль"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                required
              />
            </div>
          )}

          <button type="submit" className="auth-submit-button">
            {isLogin ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </form>

        <div className="auth-footer">
          <p className="auth-switch-text">
            {isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?'}
            <button className="auth-switch-button" onClick={switchMode}>
              {isLogin ? 'Зарегистрироваться' : 'Войти'}
            </button>
          </p>

          <div className="auth-features">
            <h4>Преимущества аккаунта:</h4>
            <ul>
              <li>📝 Сохранение истории просмотров</li>
              <li>❤️ Создание списка избранного</li>
              <li>🎬 Персональные рекомендации</li>
              <li>⚙️ Настройки под вас</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;