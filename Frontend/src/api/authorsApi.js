import api from './axios';

export const authorsApi = {
  getAuthors: async () => {
    const response = await api.get('/api/v1/movies/authors/');
    return response.data;
  },

  getAuthor: async (slug) => {
    const response = await api.get(`/api/v1/movies/authors/${slug}/`);
    return response.data;
  },

  createAuthor: async (name, bio) => {
    const response = await api.post('/api/v1/movies/authors/', { name, bio });
    return response.data;
  },
};