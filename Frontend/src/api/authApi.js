import api from './axios';

export const authApi = {
  // Регистрация (с password_confirm!)
  register: async (userData) => {
    const { username, email, password, passwordConfirm, firstName, lastName, avatar } = userData;
    
    const formData = new FormData();
    formData.append('username', username);
    formData.append('email', email);
    formData.append('password', password);
    formData.append('password_confirm', passwordConfirm);
    
    if (firstName) formData.append('first_name', firstName);
    if (lastName) formData.append('last_name', lastName);
    if (avatar) formData.append('avatar', avatar);

    const response = await api.post('/api/v1/auth/register/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

   
  login: async (email, password) => {
    const response = await api.post('/api/v1/auth/login/', {
      email,   
      password,
    });
    
    // Сохраняем токены
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
    }
    return response.data;
  },

  // Логаут
  logout: async () => {
    try {
      await api.post('/api/v1/auth/logout/');
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  // Получить профиль
  getProfile: async () => {
    const response = await api.get('/api/v1/auth/profile/');
    return response.data;
  },

  // Обновить профиль (PATCH, не POST!)
  updateProfile: async (data) => {
    const formData = new FormData();
    
    if (data.username) formData.append('username', data.username);
    if (data.firstName) formData.append('first_name', data.firstName);
    if (data.lastName) formData.append('last_name', data.lastName);
    if (data.avatar) formData.append('avatar', data.avatar);

    const response = await api.patch('/api/v1/auth/profile/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Сменить пароль (с new_password_confirm!)
  changePassword: async (oldPassword, newPassword, newPasswordConfirm) => {
    const response = await api.post('/api/v1/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    });
    return response.data;
  },
};