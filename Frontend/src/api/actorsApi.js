import api from './axios';

export const actorsApi = {
  getActors: async () => {
    const { data } = await api.get('/api/v1/movies/actors/');
    return data;
  },
  getActor: async (slug) => {
    const { data } = await api.get(`/api/v1/movies/actors/${slug}/`);
    return data;
  },
  createActor: async (payload) => {
    // payload: { name, bio, ... }
    const { data } = await api.post('/api/v1/movies/actors/', payload);
    return data;
  },
};