import api from './axios';

export const genresApi = {
  getGenres: async () => {
    const response = await api.get('/api/v1/movies/genres/');
    return response.data;
  },

  getGenre: async (slug) => {
    const response = await api.get(`/api/v1/movies/genres/${slug}/`);
    return response.data;
  },

  createGenre: async (name) => {
    const response = await api.post('/api/v1/movies/genres/', { name });
    return response.data;
  },
};
