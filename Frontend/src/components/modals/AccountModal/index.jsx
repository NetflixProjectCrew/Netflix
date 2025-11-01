import { useState, useEffect } from 'react';
import './AccountModal.css';
import { authApi } from '../../../api/authApi';

const AccountModal = ({ onClose, onLogout, userData, isDarkTheme }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    username: userData?.username || '',
    firstName: userData?.first_name || '',
    lastName: userData?.last_name || '',
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
    setError('');
    setSuccess('');
  };

  const handleSave = async () => {
    setError('');
    setSuccess('');
    setIsLoading(true);

    try {
      await authApi.updateProfile({
        username: formData.username,
        firstName: formData.firstName,
        lastName: formData.lastName,
      });

      setSuccess('Профиль успешно обновлён!');
      setIsEditing(false);
      
      // Обновляем localStorage
      const updatedUser = { ...userData, ...formData };
      localStorage.setItem('cinemate_user', JSON.stringify(updatedUser));
      
      // Перезагружаем профиль
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } catch (err) {
      console.error('Update error:', err);
      const errorMsg = err.response?.data?.message || 'Ошибка обновления профиля';
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      onLogout();
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Недавно';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const getInitials = (username) => {
    if (!username) return 'U';
    return username.charAt(0).toUpperCase();
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="account-modal">
        <div className="account-header">
          <h2 className="account-title">Мой аккаунт</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        {error && (
          <div className="account-error">
            {error}
          </div>
        )}

        {success && (
          <div className="account-success">
            {success}
          </div>
        )}

        <div className="account-content">
          <div className="account-avatar">
            <div className="avatar-large">
              {userData?.avatar ? (
                <img src={userData.avatar} alt="Avatar" className="avatar-img" />
              ) : (
                <span className="avatar-text">
                  {getInitials(userData?.username)}
                </span>
              )}
            </div>
          </div>

          <div className="user-info">
            <h3 className="user-name">
              {userData?.full_name || userData?.username || 'Пользователь'}
            </h3>
            <p className="user-email">{userData?.email || 'email@example.com'}</p>
            <p className="user-join-date">
              Участник с {formatDate(userData?.created_at)}
            </p>
          </div>

          <div className="account-form">
            <div className="form-group">
              <label className="form-label">Имя пользователя</label>
              <input 
                type="text" 
                name="username"
                className="form-input"
                value={formData.username}
                onChange={handleInputChange}
                readOnly={!isEditing}
                disabled={isLoading}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Имя</label>
                <input 
                  type="text" 
                  name="firstName"
                  className="form-input"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  readOnly={!isEditing}
                  disabled={isLoading}
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Фамилия</label>
                <input 
                  type="text" 
                  name="lastName"
                  className="form-input"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  readOnly={!isEditing}
                  disabled={isLoading}
                />
              </div>
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
                <span className="plan-name">
                  {userData?.subscription?.plan?.name || 'Без подписки'}
                </span>
                {(!userData?.subscription || !userData?.subscription?.is_active) && (
                  <button className="upgrade-button">Оформить подписку</button>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="account-footer">
          {!isEditing ? (
            <>
              <button 
                className="save-button" 
                onClick={() => setIsEditing(true)}
                disabled={isLoading}
              >
                Редактировать профиль
              </button>
              <button 
                className="logout-button" 
                onClick={handleLogout}
                disabled={isLoading}
              >
                Выйти из аккаунта
              </button>
            </>
          ) : (
            <>
              <button 
                className="save-button" 
                onClick={handleSave}
                disabled={isLoading}
              >
                {isLoading ? 'Сохранение...' : 'Сохранить изменения'}
              </button>
              <button 
                className="cancel-button" 
                onClick={() => {
                  setIsEditing(false);
                  setFormData({
                    username: userData?.username || '',
                    firstName: userData?.first_name || '',
                    lastName: userData?.last_name || '',
                  });
                }}
                disabled={isLoading}
              >
                Отмена
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AccountModal;