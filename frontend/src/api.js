const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  async post(endpoint, data, token = null) {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error?.message || 'Ошибка запроса');
    }

    return result;
  },

  async get(endpoint, token = null) {
    const headers = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'GET',
      headers,
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error?.message || 'Ошибка запроса');
    }

    return result;
  },

  async put(endpoint, data, token = null) {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error?.message || 'Ошибка запроса');
    }

    return result;
  },

  async delete(endpoint, token = null) {
    const headers = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'DELETE',
      headers,
    });

    if (response.status === 204) {
      return null;
    }

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error?.message || 'Ошибка запроса');
    }

    return result;
  },
};

export const authApi = {
  register: (email, password) =>
    api.post('/api/auth/register', { email, password }),

  login: (email, password) =>
    api.post('/api/auth/login', { email, password }),
};

export const linksApi = {
  create: (url, token = null) => api.post('/api/links', { url }, token),

  getMyLinks: (token) => api.get('/api/my/links', token),

  delete: (id, token) => api.delete(`/api/my/links/${id}`, token),

  setAlias: (id, alias, token) =>
    api.put(`/api/my/links/${id}/alias`, { alias }, token),
};

export const adminApi = {
  getUsers: (token) => api.get('/api/admin/users', token),

  blockUser: (id, is_blocked, token) =>
    api.post(`/api/admin/users/${id}/block`, { is_blocked }, token),
};
