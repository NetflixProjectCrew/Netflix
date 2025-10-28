import api from './axios';

export const charactersApi = {
  getCharacters: async () => {
    const { data } = await api.get('/api/v1/movies/characters/');
    return data;
  },
  getCharacter: async (slug) => {
    const { data } = await api.get(`/api/v1/movies/characters/${slug}/`);
    return data;
  },
  createCharacter: async (payload) => {
    const { data } = await api.post('/api/v1/movies/characters/', payload);
    return data;
  },
};
