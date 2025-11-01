import api from './axios';

export const authApi = {
  // Регистрация (с password_confirm!)
  register: async (userData) => {
    const { username, email, password, password_confirm, firstName, lastName, avatar } = userData;
    
    const formData = new FormData();
    formData.append('username', username);
    formData.append('email', email);
    formData.append('password', password);
    formData.append('password_confirm', password_confirm);
    

    const response = await api.post('/api/v1/auth/register/',{
      username,
      email,
      password,
      password_confirm
    }, 
    {
      headers: { "Content-Type": "application/json" }
    }
  );
    return response.data;
  },

   
  login: async (email, password) => {
    const response = await api.post('/api/v1/auth/login/', {
      email,   
      password,
    },{
      headers: { "Content-Type": "application/json" }
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

  
  updateProfile: async (data) => {
    const formData = new FormData();
    
    if (data.username) formData.append('username', data.username);
    if (data.firstName) formData.append('first_name', data.firstName);
    if (data.lastName) formData.append('last_name', data.lastName);
    if (data.avatar) formData.append('avatar', data.avatar);

    const response = await api.patch('/api/v1/auth/profile/', formData, 
  );
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