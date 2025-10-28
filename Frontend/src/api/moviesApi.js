import api from './axios';

export const moviesApi = {
  // Получить список фильмов
  getMovies: async (params = {}) => {
    const response = await api.get('/api/v1/movies/movies/', { params });
    return response.data;
  },

  // Получить фильм по slug
  getMovie: async (slug) => {
    const response = await api.get(`/api/v1/movies/movies/${slug}/`);
    return response.data;
  },

  // Создать фильм (админ)
  createMovie: async (data) => {
    const response = await api.post('/api/v1/movies/movies/', data);
    return response.data;
  },

  // Обновить фильм (админ)
  updateMovie: async (slug, data) => {
    const response = await api.patch(`/api/v1/movies/movies/${slug}/`, data);
    return response.data;
  },

  // Удалить фильм (админ)
  deleteMovie: async (slug) => {
    await api.delete(`/api/v1/movies/movies/${slug}/`);
  },

  getMovieCast: async (slug, params = {}) => {
    const { data } = await api.get(`/api/v1/movies/movies/${slug}/cast/`, { params });
    return data; // ожидаем [{ id, actor, character, ... }, ...]
  },

  addMovieCast: async (slug, payload) => {
    // payload: { actor: <id|slug>, character: <id|slug>, role_name?: string, ... }
    const { data } = await api.post(`/api/v1/movies/movies/${slug}/cast/`, payload);
    return data;
  },
  
  deleteMovieCast: async (slug, castId) => {
    await api.delete(`/api/v1/movies/movies/${slug}/cast/${castId}/`);
  },
  
  // Лайкнуть фильм
  likeMovie: async (slug) => {
    const response = await api.post(`/api/v1/movies/movies/${slug}/like/`);
    return response.data;
  },

  // Убрать лайк
  unlikeMovie: async (slug) => {
    const response = await api.post(`/api/v1/movies/movies/${slug}/unlike/`);
    return response.data;
  },

  // Обновить прогресс просмотра
  updateProgress: async (slug, positionSec, durationSec) => {
    const response = await api.post(`/api/v1/movies/movies/${slug}/progress/`, {
      position_sec: positionSec,
      duration_sec: durationSec,
    });
    return response.data;
  },

  // Мои просмотренные
  getWatchedMovies: async () => {
    const response = await api.get('/api/v1/movies/me/watched/');
    return response.data;
  },
};