import { useState } from 'react';
import './AuthModal.css';
import { authApi } from '../../../../api/authApi';

const AuthModal = ({ onClose, onLogin, isDarkTheme }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: ''
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
    setError(''); // Очищаем ошибку при вводе
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      if (isLogin) {
        // Логин
        const response = await authApi.login(formData.email, formData.password);
        
        // Получаем профиль пользователя
        const profile = await authApi.getProfile();
        
        onLogin(profile);
      } else {
        // Регистрация
        if (formData.password !== formData.confirmPassword) {
          setError('Пароли не совпадают!');
          setIsLoading(false);
          return;
        }

        const response = await authApi.register({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          passwordConfirm: formData.confirmPassword,
          firstName: formData.firstName,
          lastName: formData.lastName
        });

        // После успешной регистрации получаем профиль
        const profile = await authApi.getProfile();
        onLogin(profile);
      }
    } catch (err) {
      console.error('Auth error:', err);
      
      // Обработка ошибок
      if (err.response?.data) {
        const errorData = err.response.data;
        
        // Формируем читаемое сообщение об ошибке
        if (typeof errorData === 'object') {
          const messages = Object.entries(errorData)
            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
            .join('; ');
          setError(messages);
        } else {
          setError(errorData.message || 'Произошла ошибка');
        }
      } else {
        setError('Ошибка соединения с сервером');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setFormData({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      firstName: '',
      lastName: ''
    });
    setError('');
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="auth-modal">
        <div className="auth-header">
          <h2 className="auth-title">{isLogin ? 'Вход в аккаунт' : 'Регистрация'}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label className="form-label">Имя пользователя *</label>
              <input 
                type="text" 
                name="username"
                className="form-input"
                placeholder="Введите имя пользователя"
                value={formData.username}
                onChange={handleInputChange}
                required
                disabled={isLoading}
              />
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Email *</label>
            <input 
              type="email" 
              name="email"
              className="form-input"
              placeholder="Введите email"
              value={formData.email}
              onChange={handleInputChange}
              required
              disabled={isLoading}
            />
          </div>

          {!isLogin && (
            <>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Имя</label>
                  <input 
                    type="text" 
                    name="firstName"
                    className="form-input"
                    placeholder="Имя"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    disabled={isLoading}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Фамилия</label>
                  <input 
                    type="text" 
                    name="lastName"
                    className="form-input"
                    placeholder="Фамилия"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    disabled={isLoading}
                  />
                </div>
              </div>
            </>
          )}
          
          <div className="form-group">
            <label className="form-label">Пароль *</label>
            <input 
              type="password" 
              name="password"
              className="form-input"
              placeholder="Введите пароль"
              value={formData.password}
              onChange={handleInputChange}
              required
              disabled={isLoading}
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label className="form-label">Подтвердите пароль *</label>
              <input 
                type="password" 
                name="confirmPassword"
                className="form-input"
                placeholder="Повторите пароль"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                required
                disabled={isLoading}
              />
            </div>
          )}

          <button 
            type="submit" 
            className="auth-submit-button"
            disabled={isLoading}
          >
            {isLoading ? 'Загрузка...' : (isLogin ? 'Войти' : 'Зарегистрироваться')}
          </button>
        </form>

        <div className="auth-footer">
          <p className="auth-switch-text">
            {isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?'}
            <button 
              className="auth-switch-button" 
              onClick={switchMode}
              disabled={isLoading}
            >
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