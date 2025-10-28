import axios from 'axios';
import {toast} from 'react-toastify'


const API_BASE_URL = 'http://localhost:8000'; // Измени на свой URL

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false,
});

// Interceptor для добавления токена к запросам
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor для обработки 401 и обновления токена
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Если 401 и это не повторный запрос
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          `${API_BASE_URL}/api/v1/auth/token/refresh/`,
          { refresh: refreshToken }
        );

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        // Повторяем оригинальный запрос с новым токеном
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        // Если refresh не удался - разлогиниваем
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
     if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          if (data.detail) {
            toast.error(data.detail)
          } else if (typeof data === 'object') {
            // Показываем первую ошибку валидации
            const firstError = Object.values(data)[0]
            if (Array.isArray(firstError)) {
              toast.error(firstError[0])
            }
          }
          break
        case 403:
          toast.error('У вас нет прав для выполнения этого действия.')
          break
        case 404:
          toast.error('Запрашиваемый ресурс не найден.')
          break
        case 429:
          toast.error('Слишком много запросов. Попробуйте позже.')
          break
        case 500:
          toast.error('Внутренняя ошибка сервера. Попробуйте позже.')
          break
        default:
          toast.error('Произошла неожиданная ошибка.')
      }
    } else if (error.request) {
      toast.error('Не удается подключиться к серверу.')
    } else {
      toast.error('Произошла ошибка при отправке запроса.')
    }


    return Promise.reject(error);
  }
);

export default axiosInstance;
